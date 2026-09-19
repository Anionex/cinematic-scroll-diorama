#!/usr/bin/env python3
"""Inline a prebuilt single-chunk page; derive the output name from its title."""

import argparse
import base64
import html
from html.parser import HTMLParser
import json
import mimetypes
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class Packager(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.root = source.parent.resolve()
        self.parts = []
        self.title = []
        self.in_title = False
        self.style_parts = None
        self.external_script = False
        self.assets = set()

    def local_path(self, reference, base=None):
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            raise ValueError(f"External asset must be embedded before packaging: {reference}")
        path = unquote(url.path)
        result = ((self.root / path.lstrip("/")) if path.startswith("/")
                  else (base or self.root) / path).resolve()
        if not result.is_relative_to(self.root):
            raise ValueError(f"Asset escapes the build directory: {reference}")
        if not result.is_file():
            raise ValueError(f"Missing asset: {reference}")
        self.assets.add(result)
        return result

    def data_uri(self, reference, base=None):
        if reference.startswith(("data:", "#")):
            return reference
        path = self.local_path(reference, base)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        fragment = urlsplit(reference).fragment
        return f"data:{mime};base64,{encoded}" + (f"#{fragment}" if fragment else "")

    def css(self, text, base):
        if re.search(r"@import\b", text, re.I):
            raise ValueError("Bundle CSS @import rules before packaging")
        def replace(match):
            return 'url("' + self.data_uri(match.group(2).strip(), base) + '")'
        return re.sub(r"url\(\s*(['\"]?)([^)'\"\n]+)\1\s*\)", replace, text, flags=re.I)

    @staticmethod
    def escape_end_tag(text, tag):
        return re.sub(r"</" + tag, lambda match: "<\\/" + match[0][2:], text, flags=re.I)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "base":
            raise ValueError("Remove <base>; standalone resources must be self-contained")
        if tag == "link" and "modulepreload" in (attrs.get("rel") or "").split():
            raise ValueError("Build JavaScript as one chunk with modulePreload disabled")
        if tag == "link" and attrs.get("rel") == "stylesheet":
            path = self.local_path(attrs["href"])
            css = self.css(path.read_text(encoding="utf-8"), path.parent)
            self.parts.append("<style>" + self.escape_end_tag(css, "style") + "</style>")
            return
        if tag == "script" and attrs.get("src"):
            if attrs.get("type") != "module":
                raise ValueError("Expected a bundled type=module entry to preserve deferred execution")
            path = self.local_path(attrs["src"])
            scripts = {file.resolve() for file in self.root.rglob("*")
                       if file.is_file() and file.suffix in {".js", ".mjs", ".cjs"}}
            if scripts != {path}:
                raise ValueError("Build JavaScript as one chunk in a clean output directory before packaging")
            code = path.read_text(encoding="utf-8")
            self.parts.append('<script type="module">\n' + self.escape_end_tag(code, "script"))
            self.external_script = True
            return
        if "srcset" in attrs:
            raise ValueError("Use one embedded image src; expand srcset at build time if needed")
        for attribute in ("src", "poster"):
            if attrs.get(attribute):
                attrs[attribute] = self.data_uri(attrs[attribute])
        if tag == "link" and attrs.get("href"):
            attrs["href"] = self.data_uri(attrs["href"])
        if attrs.get("style"):
            attrs["style"] = self.css(attrs["style"], self.root)
        serialized = "".join(
            " " + name + ("" if value is None else '="' + html.escape(value, quote=True) + '"')
            for name, value in attrs.items()
        )
        self.parts.append("<" + tag + serialized + ">")
        if tag == "title":
            self.in_title = True
        if tag == "style":
            self.style_parts = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.external_script = False
        if tag == "style" and self.style_parts is not None:
            css = self.css("".join(self.style_parts), self.root)
            self.parts.append(self.escape_end_tag(css, "style"))
            self.style_parts = None
        self.parts.append("</" + tag + ">")

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.style_parts is not None:
            self.style_parts.append(data)
        elif not self.external_script:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data("&" + name + ";")

    def handle_charref(self, name):
        self.handle_data("&#" + name + ";")

    def handle_decl(self, decl):
        self.parts.append("<!" + decl + ">")

    def handle_comment(self, data):
        self.parts.append("<!--" + data + "-->")


def package(source):
    source = source.resolve(strict=True)
    parser = Packager(source)
    parser.feed(source.read_text(encoding="utf-8"))
    parser.close()
    title = html.unescape("".join(parser.title)).strip() or "album"
    stem = "".join(character if character.isalnum() or character in "-_" else "-"
                   for character in title)
    stem = re.sub("-+", "-", stem).strip("-_")[:70] or "album"
    output = source.parent / (stem + "-digital-exhibition.html")
    if output == source:
        raise ValueError("Input must be the build entry, not an already packaged export")
    output.write_text("".join(parser.parts), encoding="utf-8")
    return {"status": "packaged", "file": str(output), "title": title,
            "bytes": output.stat().st_size, "embedded_files": len(parser.assets),
            "next": "Run verify_offline.py and inspect its screenshots"}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("build_entry", type=Path, help="Built HTML entry, usually dist/index.html")
    args = cli.parse_args()
    try:
        result = package(args.build_entry)
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
