import pytest

from termcap.gif_converter import (
    build_keyframe_sampling_plan,
    build_sampling_plan,
    ensure_viewport_fits,
    extract_keyframe_percentages,
    infer_svg_size,
    parse_animation_duration_ms,
)


class FakeDriver:
    def __init__(self, outer_width, outer_height, inner_width, inner_height):
        self.outer_width = outer_width
        self.outer_height = outer_height
        self.inner_width = inner_width
        self.inner_height = inner_height
        self.resize_calls = []

    def execute_script(self, script):
        return {
            "outerWidth": self.outer_width,
            "outerHeight": self.outer_height,
            "innerWidth": self.inner_width,
            "innerHeight": self.inner_height,
        }

    def set_window_size(self, width, height):
        width_delta = width - self.outer_width
        height_delta = height - self.outer_height
        self.outer_width = width
        self.outer_height = height
        self.inner_width += width_delta
        self.inner_height += height_delta
        self.resize_calls.append((width, height))


def test_parse_animation_duration_ms_accepts_integer_and_decimal_values():
    assert parse_animation_duration_ms(":root { --animation-duration: 2750ms; }") == 2750
    assert parse_animation_duration_ms("#screen_view { animation-duration: 12.5ms; }") == 12.5


def test_infer_svg_size_uses_viewbox_when_root_height_is_missing():
    content = '<svg xmlns="http://www.w3.org/2000/svg" width="640" viewBox="0 0 640 325"></svg>'
    assert infer_svg_size(content) == (640, 325)


def test_extract_keyframe_percentages_handles_normal_css_spacing():
    content = """
    @keyframes roll {
      0% { transform: translateY(0px); }
      25.5%{transform:translateY(-100px)}
      100% { transform: translateY(-200px); }
    }
    """
    assert extract_keyframe_percentages(content) == [0.0, 25.5, 100.0]


def test_keyframe_sampling_plan_preserves_exact_timeline():
    sample_times, durations = build_keyframe_sampling_plan(
        duration_ms=2000,
        percentages=[0.0, 25.0, 100.0],
        speed=1.0,
    )
    assert sample_times == [0, 500]
    assert durations == [500, 1500]
    assert sum(durations) == 2000


def test_uniform_sampling_plan_rejects_invalid_speed_and_fps():
    with pytest.raises(ValueError, match="speed"):
        build_sampling_plan(duration_ms=1000, fps=20, speed=0)
    with pytest.raises(ValueError, match="fps"):
        build_sampling_plan(duration_ms=1000, fps=0, speed=1)


def test_ensure_viewport_fits_grows_outer_window_to_target_size():
    driver = FakeDriver(
        outer_width=656,
        outer_height=506,
        inner_width=656,
        inner_height=367,
    )

    metrics = ensure_viewport_fits(driver, width=640, height=410)

    assert metrics["innerWidth"] >= 640
    assert metrics["innerHeight"] >= 410
    assert driver.resize_calls
