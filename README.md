# 相册 · 3D 滚动数字展

把你的旅行照片做成可滚动浏览的数字回忆：保留真实照片，再用对应的 3D 微缩场景呈现其中的建筑、街道与风景。

你提供相册，回答几个创作问题，Agent 负责制作、截图检查和交付。最终得到一个可离线打开的 HTML 文件。

## 快速开始：复制给 Agent

**把下面这段话发给 Agent，即可开始。** 替换 `【相册路径或附件】`，或直接附上相册；Agent 需要有本私有仓库的访问权限。

```text
请从 GitHub 私有仓库 Anionex/cinematic-scroll-diorama 下载并安装该 Skill，读取其中的 SKILL.md，基于【相册路径或附件】制作高质量的照片与 3D 微缩模型滚动数字展。先查看素材，再按 Skill 询问尚未确定的创作偏好与制作方式；完成制作和验证后，交付可离线双击打开的单文件 HTML。
```

## 实际 Demo：京都旅行回忆

**由 `doubao-seed-evolving` 于 2026 年 9 月 16 日生成的历史成品。**

[![京都旅行回忆：朱红鸟居微缩模型与原照片](docs/kyoto-demo.jpg)](https://github.com/Anionex/cinematic-scroll-diorama/releases/download/demo-2026-09-16/kyoto-memories-demo.mp4)

- **[下载实际 Demo（单文件 HTML）](https://github.com/Anionex/cinematic-scroll-diorama/releases/download/demo-2026-09-16/kyoto-memories-standalone.html)**：下载后用浏览器打开。
- **[观看 / 下载演示视频（MP4，约 55 秒）](https://github.com/Anionex/cinematic-scroll-diorama/releases/download/demo-2026-09-16/kyoto-memories-demo.mp4)**：由原始录屏转码，保留完整时长。
- [下载原始录屏（MOV）](https://github.com/Anionex/cinematic-scroll-diorama/releases/download/demo-2026-09-16/kyoto-memories-original.mov)

HTML 与视频保存在本私有仓库的 Release 附件中，需要仓库访问权限；原版 HTML 和 MOV 未改动，不随 Skill 安装下载。此历史 Demo 不代表当前版本 Skill 的端到端评测结果。

## 成品是什么样的？

- **一段完整的滚动叙事**：从封面进入各个章节，滚动时镜头、照片与文字随之变化，最后抵达结尾页。
- **照片与模型共同呈现记忆**：照片可以像小幅相片一样放在模型旁，也可以先出现，再过渡到对应的立体场景。
- **来自相册的微缩世界**：模型根据照片中的形态与空间关系制作，不用无关景点填充，也不用平面照片冒充立体模型。
- **一个文件即可观看**：照片、代码和其他必要资源内嵌在 HTML 中，观看时不需要服务器或安装依赖。

默认按桌面 `1280×800` 打磨。其他尺寸或移动端需求，请在开始时说明。

## 手动安装与更多用法

### 1. 获取完整 Skill

有仓库访问权限后，可以下载仓库 ZIP 并解压，或克隆：

```sh
git clone git@github.com:Anionex/cinematic-scroll-diorama.git
```

保留整个目录，不要只复制 `SKILL.md`。3D 指南与交付工具已包含在仓库里，无需另装 `3d-creation`。

使用能读取本地文件、执行代码并运行浏览器截图的编码 Agent。制作阶段的构建与检查依赖由 Agent 准备；离线观看成品不需要这些工具。

### 2. 提供相册并发送这段话

将 `【】` 替换为实际路径；也可以直接附上相册 ZIP 和参考图片。

```text
读取【Skill 仓库绝对路径】/SKILL.md，
基于【相册文件夹或 ZIP 路径】制作相册 3D 滚动数字展。
先看素材，再询问需要我确定的偏好。
第一屏样板完成并实际截图后，交给我确认，再扩展其余章节。
```

只提供相册也可以。你不必先写设计方案、规划每个镜头或指定输出文件名。

#### 示例：不做样板，直接全量并行

将 `<path>` 替换为 Skill 仓库路径，`xxx相册` 替换为你的相册路径或附件名称。

```text
请读取 <path>/SKILL.md，基于xxx相册制作高质量的照片与 3D 微缩场景滚动数字展，交付可离线双击打开的单文件 HTML。中文文案。

主题风格、章节分组和重点、照片同屏与转场比例均由你看过素材后按推荐方案决定；只做桌面 1280x800。不做样板，共享基础和接口就绪后尽量并行制作各页，逐页自验并整合后直接交付，不等待我确认。已授权事项不重复询问。
```

### 3. 确认方向与制作方式

Agent 会根据素材提出建议，只询问尚未确定的内容：

| 你可以决定 | 例如 |
| --- | --- |
| 主题与风格 | 温暖手账、纸艺微缩、克制的展览感；也可以附设计参考 |
| 章节与重点 | 哪些照片必须保留，哪些片段略过，是否有指定顺序 |
| 照片的呈现方式 | 偏模型旁同屏、偏照片转入空间，或混合使用 |
| 展示设备 | 默认桌面，或指定其他尺寸与设备 |
| 制作方式 | 先看样板，或直接全量并行（不做样板） |

你可以回答“其余按推荐方案”。先看样板便于你提前把关方向；直接全量并行省去首章串行等待，但仍保留每页的截图自查、实际世界坐标验证和整合验收。制作中需要调整时，直接指出具体位置，例如“这章照片大一点”“夜景到结尾保持暗色”或“保留这张照片，不必为它单独建模”。

## 获取与分享成品

Agent 会提供最终 HTML 的文件路径，并保留源代码供后续修改。标题与文件名根据内容生成。

用支持 WebGL 的桌面浏览器打开 HTML，滚动浏览即可。你可以把文件移到其他目录，或发给别人观看，无需连同源代码一起发送。

**HTML 内含选用的原照片，分享文件也会分享这些照片。** 开始前可说明哪些素材不能使用。地点、日期或经历若无法从素材确认，Agent 应向你询问，而不是编造。

交付前，Agent 会检查离线打开、照片加载、前后滚动以及实际画面；若环境限制导致某项检查未完成，会说明未验证范围。

---

## 项目文件说明

这个仓库保存制作数字展的指导与工具，不包含你的相册。上方历史 Demo 单独保存在 Release 附件中，不是制作时必须复用的模板。

```text
cinematic-scroll-diorama/
├── README.md                         给使用者看的入门说明
├── SKILL.md                          Agent 的统一执行入口
├── agents/
│   └── openai.yaml                   Skill 的显示名称、简介和默认提示词
├── docs/
│   └── kyoto-demo.jpg                README 中的历史 Demo 视频预览图
├── references/
│   ├── intake.md                     创作问答、制作方式与样板确认规则
│   ├── 3d-creation.md                网页微缩模型的制作指导
│   └── runtime-and-delivery.md       滚动实现、离线打包与验收指导
├── scripts/
│   ├── package_html.py               将构建后的网页打包为单文件 HTML
│   └── verify_offline.py             在离线浏览器中检查成品并截图
├── tests/
│   └── test_verify_offline.py        基础检查状态与失败报告的回归测试
└── .gitignore                        避免提交缓存、虚拟环境和本地环境配置
```

### Agent 如何使用这些文件？

Agent 先读取 [SKILL.md](SKILL.md)，再按制作阶段查阅 `references/`：

- [intake.md](references/intake.md)：决定哪些偏好需要询问，以及先看样板和直接全量并行两种方式如何推进。
- [3d-creation.md](references/3d-creation.md)：指导从照片提炼模型，处理构图、材质、灯光、镜头和结构问题。它是参考文档，不是另一个需要安装的 Skill，也不是模型素材库。
- [runtime-and-delivery.md](references/runtime-and-delivery.md)：说明怎样组织滚动叙事、嵌入资源并检查最终 HTML。

`agents/openai.yaml` 是供支持它的工具展示 Skill 信息的元数据，不包含子 Agent 或嵌套 Skill。普通使用者无需修改这些文件。

### 两个脚本负责什么？

[package_html.py](scripts/package_html.py) 接收已构建为单个 JavaScript 包的网页入口，内嵌脚本、样式和图片，并根据页面标题生成 HTML 文件名。它不负责生成网页，也不代替前端构建工具。

[verify_offline.py](scripts/verify_offline.py) 将成品复制到临时独立目录，以断网浏览器检查资源加载、章节、原照片及前后滚动，输出章节截图和 `result.json`。`runtime_passed` 仅表示基础运行通过，不代表模型、视觉或整体验收通过；这些未验证项会单独列出。运行它需要 Python、Playwright 和浏览器环境；截图中的模型与排版仍需 Agent 实际查看。两个脚本由 Agent 按需运行，观看成品的人不需要运行它们。

维护者可用 `python -m unittest discover -s tests -v` 运行脚本回归测试。它不替代独立 Agent 端到端制作评测。

### 相册与生成文件放在哪里？

你的相册位于你指定的位置；Agent 在制作项目的工作区保留简短的 `design.md`、网页源代码、最终 HTML 和必要的检查产物。这些是每次制作生成的文件，不是本 Skill 仓库自带的内容。分享作品时只需发送最终 HTML；后续修改则保留源代码。
