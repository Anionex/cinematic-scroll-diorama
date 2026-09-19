#!/usr/bin/env python3
"""Check the exported file in an isolated, offline Chromium context."""

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

from playwright.sync_api import sync_playwright


def verify(source, viewport):
    source = source.resolve(strict=True)
    output = source.parent / (source.stem + "-review")
    output.mkdir(exist_ok=True)
    errors, external, screenshots = [], [], []
    deadline = time.monotonic() + 110

    def settle(page):
        assert time.monotonic() < deadline, "Verification deadline exceeded"
        page.evaluate("() => { window.__ALBUM_QA_READY__ = false; requestAnimationFrame(() => requestAnimationFrame(() => { window.__ALBUM_QA_READY__ = true; })); }")
        page.wait_for_function("window.__ALBUM_QA_READY__ === true")

    with tempfile.TemporaryDirectory(prefix=".album-offline-", dir=source.parent) as directory, sync_playwright() as playwright:
        isolated = Path(directory) / source.name
        shutil.copy2(source, isolated)
        uri = isolated.as_uri()
        browser = playwright.chromium.launch(
            headless=True, timeout=20000,
            args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
        )

        def new_page():
            context = browser.new_context(viewport=viewport, offline=True, device_scale_factor=1)
            context.set_default_timeout(15000)

            def route(request):
                if request.request.url == uri or request.request.url.startswith("data:"):
                    request.continue_()
                else:
                    external.append(request.request.url)
                    request.abort()
            context.route("**/*", route)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
            page.goto(uri, wait_until="load")
            return context, page

        try:
            context, page = new_page()
            sections = page.locator("main section.chapter")
            assert sections.count() >= 3, "Expected cover, chapter(s), and ending"
            assert page.locator("canvas").count() > 0, "Missing 3D canvas"
            assert page.locator(".memory-photo img").count() > 0, "Missing original photographs"
            page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
            for index in range(sections.count()):
                page.evaluate("i => window.scrollTo({top: document.querySelectorAll('main section.chapter')[i].offsetTop, behavior: 'instant'})", index)
                settle(page)
                page.wait_for_timeout(450)
                photo = sections.nth(index).locator(".memory-photo img")
                for photo_index in range(photo.count()):
                    photo.nth(photo_index).evaluate("img => { img.loading = 'eager'; }")
                    page.wait_for_function("([section, photo]) => { const img = document.querySelectorAll('main section.chapter')[section].querySelectorAll('.memory-photo img')[photo]; return img.complete && img.naturalWidth > 0; }", arg=[index, photo_index])
                    assert photo.nth(photo_index).evaluate("img => img.naturalWidth > 0 && img.src.startsWith('data:')"), "Unembedded or broken photo"
                path = output / f"{index:02d}-start.png"
                page.screenshot(path=str(path), full_page=False, timeout=15000)
                screenshots.append(str(path))
            page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            settle(page)
            page.wait_for_function("scrollY < 1")
            page.mouse.move(viewport["width"] / 2, viewport["height"] / 2)
            initial = page.evaluate("scrollY")
            distance = max(100, viewport["height"] / 2)
            page.mouse.wheel(0, distance)
            page.wait_for_function("start => scrollY > start + 25", arg=initial)
            settle(page)
            forward = page.evaluate("scrollY")
            page.mouse.wheel(0, -distance)
            page.wait_for_function("start => scrollY < start - 25", arg=forward)
            settle(page)
            reverse = page.evaluate("scrollY")
            context.close()
        finally:
            browser.close()

    assert not external, f"Unexpected resource requests: {external}"
    assert not errors, f"Browser errors: {errors}"
    result = {"status": "passed", "file": str(source), "screenshots": screenshots,
              "external_requests": external, "errors": errors,
              "scroll_positions": {"initial": initial, "forward": forward, "reverse": reverse},
              "checks": ["isolated_file_offline", "chapter_screenshots", "embedded_photos",
                         "native_scroll_forward_reverse"],
              "visual_review": "Inspect screenshots and a representative transition before delivery"}
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("html", type=Path)
    cli.add_argument("--viewport", default="1280x800", help="Confirmed desktop viewport")
    args = cli.parse_args()
    try:
        width, height = map(int, args.viewport.lower().split("x"))
        assert width > 0 and height > 0, "Invalid viewport"
        result = verify(args.html, {"width": width, "height": height})
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
