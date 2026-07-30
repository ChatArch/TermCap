import os

import pytest
from PIL import Image

from termcap.gif_converter import convert_svg_to_gif


pytestmark = pytest.mark.skipif(
    os.getenv("TERMCAP_BROWSER_TESTS") != "1",
    reason="set TERMCAP_BROWSER_TESTS=1 to run Chrome-backed acceptance tests",
)


def test_discrete_terminal_keyframes_are_captured_in_order(tmp_path):
    svg_path = tmp_path / "three-frames.svg"
    gif_path = tmp_path / "three-frames.gif"
    svg_path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" id="terminal"
     width="100" height="50" viewBox="0 0 100 50">
  <defs>
    <style><![CDATA[
      :root { --animation-duration: 300ms; }
      @keyframes roll {
        0% { transform: translateY(0px); }
        33.333% { transform: translateY(-50px); }
        66.667% { transform: translateY(-100px); }
        100% { transform: translateY(-100px); }
      }
      #screen_view {
        animation-duration: 300ms;
        animation-iteration-count: infinite;
        animation-name: roll;
        animation-timing-function: steps(1,end);
        animation-fill-mode: forwards;
      }
    ]]></style>
  </defs>
  <svg id="screen" width="100" height="50" viewBox="0 0 100 50"
       preserveAspectRatio="xMinYMin meet" overflow="hidden">
    <g id="screen_view">
      <rect x="0" y="0" width="100" height="50" fill="#ff0000"/>
      <rect x="0" y="50" width="100" height="50" fill="#00ff00"/>
      <rect x="0" y="100" width="100" height="50" fill="#0000ff"/>
    </g>
  </svg>
</svg>
""",
        encoding="utf-8",
    )

    convert_svg_to_gif(svg_path, gif_path, fps=20)

    image = Image.open(gif_path)
    colors = []
    for index in range(image.n_frames):
        image.seek(index)
        colors.append(image.convert("RGB").getpixel((50, 25)))

    assert colors == [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    assert image.size == (100, 50)
