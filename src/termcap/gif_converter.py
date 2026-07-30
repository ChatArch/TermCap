"""Browser-backed SVG and asciicast to GIF conversion."""

import math
import re
import socket
import tempfile
import threading
import time
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from lxml import etree
from PIL import Image
from platformdirs import user_cache_dir

from termcap.parser.asciicast import read_records
from termcap.renderer import render_animation

ProgressCallback = Optional[Callable[[str], None]]


def parse_animation_duration_ms(svg_content: str) -> Optional[float]:
    """Return the first CSS animation duration expressed in milliseconds."""
    patterns = (
        r"--animation-duration:\s*([0-9]+(?:\.[0-9]+)?)\s*ms",
        r"animation-duration:\s*([0-9]+(?:\.[0-9]+)?)\s*ms",
    )
    for pattern in patterns:
        match = re.search(pattern, svg_content, flags=re.IGNORECASE)
        if match:
            value = float(match.group(1))
            return int(value) if value.is_integer() else value
    return None


def _parse_svg_length(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else None


def infer_svg_size(svg_content: str) -> Tuple[int, int]:
    """Infer the rendered SVG size from root dimensions and viewBox."""
    root = etree.fromstring(svg_content.encode("utf-8"))
    width = _parse_svg_length(root.get("width"))
    height = _parse_svg_length(root.get("height"))

    view_width = view_height = None
    view_box = root.get("viewBox")
    if view_box:
        parts = view_box.replace(",", " ").split()
        if len(parts) == 4:
            view_width = float(parts[2])
            view_height = float(parts[3])

    if width and not height and view_width and view_height:
        height = width * view_height / view_width
    elif height and not width and view_width and view_height:
        width = height * view_width / view_height

    width = width or view_width or 800
    height = height or view_height or 600
    return max(1, int(round(width))), max(1, int(round(height)))


def extract_keyframe_percentages(svg_content: str) -> List[float]:
    """Extract discrete translate keyframes used by TermCap/termtosvg SVGs."""
    pattern = re.compile(
        r"([0-9]+(?:\.[0-9]+)?)%\s*\{[^{}]*?"
        r"transform\s*:\s*translate(?:Y|3D)?\s*\(",
        flags=re.IGNORECASE | re.DOTALL,
    )
    return sorted({float(value) for value in pattern.findall(svg_content)})


def quantize_durations_ms(durations_ms: Sequence[float]) -> List[int]:
    """Quantize GIF durations to centiseconds while preserving total time."""
    if not durations_ms:
        return []

    target_total = max(10, int(round(sum(durations_ms) / 10.0)) * 10)
    quantized: List[int] = []
    carry_ms = 0.0
    for duration in durations_ms[:-1]:
        corrected = duration + carry_ms
        actual_ms = max(10, int(round(corrected / 10.0)) * 10)
        carry_ms = corrected - actual_ms
        quantized.append(actual_ms)

    last = target_total - sum(quantized)
    if last < 10 and quantized:
        deficit = 10 - last
        donor = max(range(len(quantized)), key=quantized.__getitem__)
        transferable = min(deficit, max(0, quantized[donor] - 10))
        quantized[donor] -= transferable
        last += transferable
    quantized.append(max(10, last))
    return quantized


def _validate_sampling_args(fps: int, speed: float) -> float:
    speed = float(speed)
    if speed <= 0:
        raise ValueError("speed must be greater than 0")
    if fps <= 0:
        raise ValueError("fps must be greater than 0")
    return speed


def build_sampling_plan(duration_ms: float, fps: int, speed: float) -> Tuple[List[int], List[int]]:
    """Build a uniform fallback sampling plan for generic SVG animations."""
    speed = _validate_sampling_args(fps, speed)
    duration_ms = max(1.0, float(duration_ms))
    interval = 1000.0 / float(fps)
    frame_count = max(1, int(math.ceil(duration_ms / interval)))
    sample_times = [
        min(int(duration_ms - 1), int(round(index * interval)))
        for index in range(frame_count)
    ]
    raw_duration = (duration_ms / speed) / frame_count
    durations = quantize_durations_ms([raw_duration] * frame_count)
    return sample_times, durations


def build_keyframe_sampling_plan(
    duration_ms: float,
    percentages: Sequence[float],
    speed: float,
) -> Tuple[List[int], List[int]]:
    """Build one GIF frame per discrete terminal keyframe interval."""
    speed = _validate_sampling_args(1, speed)
    duration_ms = max(1.0, float(duration_ms))
    values = sorted({min(100.0, max(0.0, float(value))) for value in percentages})
    if not values or values[0] != 0.0:
        values.insert(0, 0.0)
    if values[-1] != 100.0:
        values.append(100.0)

    sample_times = [
        min(int(duration_ms - 1), int(math.ceil(duration_ms * value / 100.0)))
        for value in values[:-1]
    ]
    raw_durations = [
        duration_ms * (values[index + 1] - values[index]) / 100.0 / speed
        for index in range(len(values) - 1)
    ]
    return sample_times, quantize_durations_ms(raw_durations)


def ensure_viewport_fits(
    driver,
    width: int,
    height: int,
    max_attempts: int = 5,
    margin: int = 8,
) -> Dict[str, int]:
    """Grow the browser outer window until its viewport contains the SVG."""
    script = """
return {
  outerWidth: window.outerWidth,
  outerHeight: window.outerHeight,
  innerWidth: window.innerWidth,
  innerHeight: window.innerHeight
};
"""
    metrics = driver.execute_script(script)
    for _ in range(max_attempts):
        width_deficit = max(0, int(math.ceil(width - metrics["innerWidth"])))
        height_deficit = max(0, int(math.ceil(height - metrics["innerHeight"])))
        if width_deficit == 0 and height_deficit == 0:
            return metrics
        driver.set_window_size(
            metrics["outerWidth"] + width_deficit + margin,
            metrics["outerHeight"] + height_deficit + margin,
        )
        time.sleep(0.05)
        metrics = driver.execute_script(script)

    if metrics["innerWidth"] < width or metrics["innerHeight"] < height:
        raise RuntimeError(
            "Browser viewport is smaller than the SVG target: "
            f"viewport={metrics['innerWidth']}x{metrics['innerHeight']}, "
            f"target={width}x{height}"
        )
    return metrics


def _notify(progress: ProgressCallback, message: str) -> None:
    if progress:
        progress(message)


@contextmanager
def _serve_directory(directory: Path):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return

    handler = partial(QuietHandler, directory=str(directory))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)


def _create_chrome_driver(progress: ProgressCallback = None):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.driver_cache import DriverCacheManager
    except ImportError as exc:
        raise RuntimeError(
            "GIF backend dependencies are missing. Reinstall TermCap or install "
            "selenium, webdriver-manager, and pillow."
        ) from exc

    _notify(progress, "启动 Chrome 渲染后端")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--hide-scrollbars")

    cache_root = Path(user_cache_dir("termcap", "termcap")) / "webdriver"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache = DriverCacheManager(root_dir=str(cache_root))
    _notify(progress, "准备 ChromeDriver")
    service = Service(ChromeDriverManager(cache_manager=cache).install())
    return webdriver.Chrome(service=service, options=options)


def _prepare_svg_page(driver, width: int, height: int) -> None:
    driver.execute_script(
        """
const width = arguments[0];
const height = arguments[1];
const root = document.getElementById('terminal') || document.querySelector('svg');
document.documentElement.style.margin = '0';
document.documentElement.style.padding = '0';
document.documentElement.style.background = 'transparent';
document.body.style.margin = '0';
document.body.style.padding = '0';
document.body.style.background = 'transparent';
if (root) {
  root.setAttribute('width', width);
  root.setAttribute('height', height);
  root.style.width = `${width}px`;
  root.style.height = `${height}px`;
  root.style.display = 'block';
  root.style.overflow = 'hidden';
}
""",
        width,
        height,
    )
    ensure_viewport_fits(driver, width, height)
    driver.execute_async_script(
        """
const done = arguments[arguments.length - 1];
const fontsReady = document.fonts && document.fonts.ready
  ? document.fonts.ready
  : Promise.resolve();
fontsReady.then(() => requestAnimationFrame(() => requestAnimationFrame(done)));
"""
    )


def _freeze_svg_at(driver, sample_time_ms: int, duration_ms: float) -> None:
    driver.execute_async_script(
        """
const sampleTime = arguments[0];
const duration = arguments[1];
const done = arguments[arguments.length - 1];
const screenView = document.getElementById('screen_view');
if (screenView) {
  screenView.style.animationPlayState = 'paused';
  screenView.style.animationDelay = '0ms';
  screenView.style.animationDuration = `${duration}ms`;
  screenView.style.animationTimingFunction = 'steps(1,end)';
  screenView.style.animationFillMode = 'both';
}
let controlledScreenView = false;
for (const animation of document.getAnimations()) {
  try {
    animation.pause();
    animation.currentTime = sampleTime;
    const target = animation.effect && animation.effect.target;
    if (screenView && target === screenView) {
      controlledScreenView = true;
    }
  } catch (_) {
    // Some script-driven animations do not expose a writable currentTime.
  }
}
if (screenView && !controlledScreenView) {
  screenView.style.animationDelay = `-${sampleTime}ms`;
}
const fontsReady = document.fonts && document.fonts.ready
  ? document.fonts.ready
  : Promise.resolve();
fontsReady.then(() => requestAnimationFrame(() => requestAnimationFrame(done)));
""",
        int(sample_time_ms),
        float(duration_ms),
    )


def _capture_svg_element(driver, width: int, height: int) -> Image.Image:
    element = driver.find_element("css selector", "#terminal, svg")
    image = Image.open(BytesIO(element.screenshot_as_png)).convert("RGBA")
    if image.width < width or image.height < height:
        ensure_viewport_fits(driver, width, height)
        image = Image.open(BytesIO(element.screenshot_as_png)).convert("RGBA")
    if image.width < width or image.height < height:
        raise RuntimeError(
            "Captured SVG frame is incomplete: "
            f"captured={image.width}x{image.height}, expected={width}x{height}"
        )
    if image.size != (width, height):
        image = image.crop((0, 0, width, height))
    return image.convert("P", palette=Image.ADAPTIVE)


def convert_svg_to_gif(
    input_svg,
    output_gif,
    speed: float = 1.0,
    fps: int = 20,
    loop: int = 0,
    progress: ProgressCallback = None,
) -> Tuple[int, float]:
    """Convert an animated SVG to GIF with deterministic browser sampling."""
    input_path = Path(input_svg).expanduser().resolve()
    output_path = Path(output_gif).expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"SVG not found: {input_path}")
    if loop < 0:
        raise ValueError("loop must be zero or greater")

    _notify(progress, "读取 SVG")
    svg_content = input_path.read_text(encoding="utf-8", errors="replace")
    duration_ms = parse_animation_duration_ms(svg_content) or 1000
    width, height = infer_svg_size(svg_content)
    percentages = extract_keyframe_percentages(svg_content)
    if percentages:
        sample_times, frame_durations = build_keyframe_sampling_plan(
            duration_ms,
            percentages,
            speed,
        )
        _notify(progress, f"按 {len(sample_times)} 个离散关键帧采样")
    else:
        sample_times, frame_durations = build_sampling_plan(duration_ms, fps, speed)
        _notify(progress, f"按 {fps} FPS 采样 {len(sample_times)} 帧")

    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\"></head>"
        "<body style=\"margin:0;padding:0;background:transparent;\">"
        f"{svg_content}</body></html>"
    )

    with tempfile.TemporaryDirectory(prefix="termcap-svg2gif-") as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "scene.html").write_text(html, encoding="utf-8")
        driver = _create_chrome_driver(progress=progress)
        images: List[Image.Image] = []
        try:
            with _serve_directory(temp_path) as server_url:
                driver.set_window_size(max(200, width + 32), max(200, height + 180))
                driver.get(f"{server_url}/scene.html")
                _prepare_svg_page(driver, width, height)
                _notify(progress, "渲染 GIF 帧")
                for sample_time in sample_times:
                    _freeze_svg_at(driver, sample_time, duration_ms)
                    images.append(_capture_svg_element(driver, width, height))
        finally:
            driver.quit()

    if not images:
        raise RuntimeError("No GIF frames were captured")

    _notify(progress, "写入 GIF")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=frame_durations,
        loop=loop,
        optimize=False,
        disposal=2,
    )
    return len(images), float(duration_ms) / float(speed)


def convert_cast_to_gif(
    input_cast,
    output_gif,
    template_name: str,
    min_duration: int,
    max_duration: Optional[int],
    loop_delay: int,
    speed: float = 1.0,
    fps: int = 20,
    loop: int = 0,
    progress: ProgressCallback = None,
) -> Tuple[int, float]:
    """Render an asciicast to an intermediate SVG, then convert it to GIF."""
    _notify(progress, "读取 CAST")
    records_iter = read_records(str(input_cast))
    try:
        header = next(records_iter)
    except StopIteration as exc:
        raise ValueError("Empty input file") from exc

    with tempfile.TemporaryDirectory(prefix="termcap-cast2gif-") as temp_dir:
        temp_svg = Path(temp_dir) / "rendered.svg"
        _notify(progress, "渲染中间 SVG")
        render_animation(
            records_iter,
            header,
            str(temp_svg),
            template_name,
            min_duration,
            max_duration,
            loop_delay,
        )
        return convert_svg_to_gif(
            temp_svg,
            output_gif,
            speed=speed,
            fps=fps,
            loop=loop,
            progress=progress,
        )
