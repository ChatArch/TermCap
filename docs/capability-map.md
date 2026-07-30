# 能力边界

## 已实现并验证

| 能力 | 状态 | 契约 |
|---|---|---|
| PTY 录制 | 已实现 | 输出 asciicast v2，支持交互 shell 和 `-c` 单命令 |
| CAST 重放 | 已实现 | 支持速度和 idle 上限 |
| 终端状态重建 | 已实现 | 基于 `pyte`，保留 ANSI 样式、光标和宽字符 |
| SVG 动画 | 已实现 | 稳定 DOM ID、离散 CSS 关键帧、模板化 UI |
| SVG 静帧 | 已实现 | 每个终端状态输出独立 SVG |
| CAST → GIF | 已实现 | 复用 SVG 中间表示和同一时间轴 |
| SVG → GIF | 已实现 | 关键帧优先、普通 SVG 按 FPS 回退 |
| viewport 校正 | 已实现 | 截图尺寸不足时动态扩展或明确失败 |
| 内置模板 | 已实现 | 16 套模板随 wheel 打包 |
| MkDocs 文档 | 已实现 | 中英文 suffix i18n、CLI 树和任务型导航 |

## 安全与默认行为

- 不默认裁剪终端内部行；geometry 是录制契约的一部分。
- 不为未实现能力保留假 CLI 选项。
- GIF 输出默认无限循环，`--loop 0`。
- `--speed 1.0` 保持录制时间；速度变化只调整输出帧时长。
- 浏览器驱动缓存在用户 cache 目录，不写入项目仓库。
- 内置模板从 package data 加载；源码 `docs/examples` 仅作为开发参考。

## 当前不在范围

- MP4/WebM 导出
- 音频录制与同步
- Windows ConPTY 录制
- CAST 剪辑器或 CAST→CAST 重采样
- 基于最后一帧内容的自动裁行
- 完整实现模板文档中历史提到的 WAAPI renderer 模式

## 验证层级

<div class="grid cards" markdown>

-   **单元测试**

    parser、配置、模板、时长量化、关键帧计划、viewport 和 CLI 契约。

-   **浏览器测试**

    红/绿/蓝离散关键帧按顺序进入 GIF，截图尺寸等于 SVG。

-   **真实录制验收**

    ANSI、中文宽字符、逐步输出和回车更新，经 CAST→SVG→GIF 完整转换。

-   **发行验收**

    wheel/sdist 检查、模板 package data、MkDocs strict、Trusted Publisher 和 PyPI clean install。

</div>
