# 录制与渲染

TermCap 将终端媒体处理拆成三层：PTY 录制、终端状态重建、媒体导出。每一层都有明确的数据契约，便于单独验收和复用。

<div class="grid cards" markdown>

-   **Capture**

    PTY 输出 → asciicast v2 `.cast`

-   **Render**

    CAST events → `pyte.Screen` → SVG 帧

-   **Export**

    SVG 时间轴 → Chrome 确定性采样 → GIF

</div>

## PTY → CAST

`termcap record` 使用 `pty.fork()` 启动子进程，设置终端 geometry，并将输出事件写成 asciicast v2：

```json
{"version": 2, "width": 80, "height": 20}
[0.15, "o", "hello\r\n"]
```

录制器会：

- 使用增量 UTF-8 decoder，避免多字节字符跨 chunk 时损坏；
- 保留 ANSI 控制序列、颜色和光标移动；
- stdin EOF 后停止轮询 stdin，但继续读取 PTY；
- 子进程退出后 drain PTY 到 EOF/EIO，避免丢失最后一段输出。

## CAST → SVG { #cast-to-svg }

```bash
termcap render demo.cast demo.svg
```

渲染器把 events 输入 `pyte.Stream`，在每个有效时间点保存终端 screen buffer。SVG 中的稳定 DOM 契约包括：

```text
#terminal      外层 SVG 和最终截图区域
#screen        当前终端 viewport
#screen_view   纵向堆叠的离散帧
```

动画使用 `@keyframes roll` 和 `steps(1,end)`，因此终端帧之间不会出现平滑滚动产生的半帧。

### 时间控制

- `--min-duration`：合并过密输出，避免无意义微帧；
- `--max-duration`：限制长时间 idle；
- `--loop-delay`：最后一帧到下一次循环之间的停留时间。

## CAST → GIF { #cast-to-gif }

```bash
termcap render demo.cast demo.gif --format gif
```

TermCap 先在临时目录生成 SVG，再使用同一 SVG→GIF 后端导出。中间 SVG 不写入当前仓库。

## SVG → GIF { #svg-to-gif }

```bash
termcap svg2gif demo.svg demo.gif
```

对 TermCap/termtosvg 风格 SVG，转换器会：

1. 读取 `--animation-duration`；
2. 提取 `translateY(...)` 离散关键帧百分比；
3. 在每个关键帧边界之后确定性冻结动画；
4. 等待 `document.fonts.ready` 和两个 animation frame；
5. 动态增大 Chrome outer window，直到 `innerWidth/innerHeight` 能容纳 `#terminal`；
6. 截图后校验像素尺寸与 SVG 期望尺寸一致；
7. 按 GIF 的 10ms 精度量化每帧时长，并补偿累计误差。

普通 SVG 没有可识别的离散关键帧时，才回退到 `--fps` 均匀采样。

## 避免裁切和空白

### 底部或右侧被裁掉

Selenium 的 `set_window_size()` 设置 outer window，并不等于网页 viewport。TermCap 会读取 `window.innerWidth/innerHeight` 并动态补足差值；如果仍然小于目标 SVG，转换会失败而不是静默写出残缺 GIF。

### 终端内部空白较多

这是录制 geometry 的一部分，不是浏览器截图边框。短命令演示应使用更紧凑的尺寸：

```bash
termcap record short.cast -g 80x12 -c "python demo.py"
```

TermCap 不默认按最后一帧内容自动裁行，因为早期帧或 `vim`、`htop` 等全屏程序可能使用完整终端区域。

### 黑帧或字体错位

转换器不会仅依赖固定 `sleep`；它会等待字体和双 RAF。若浏览器截图仍小于目标尺寸，会立即报错。

## 验收建议

至少覆盖：

- 短命令与交互式 shell；
- ANSI 颜色和光标移动；
- 中文/宽字符；
- 回车原地更新；
- CAST→SVG、CAST→GIF、SVG→GIF；
- GIF 尺寸等于 SVG viewBox，帧总时长接近 SVG 时间轴。
