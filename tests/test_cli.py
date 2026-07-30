from click.testing import CliRunner

from termcap.cli import main


def test_root_command_without_subcommand_prints_help():
    result = CliRunner().invoke(main, [])
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "record" in result.output
    assert "render" in result.output


def test_svg2gif_help_exposes_stable_conversion_options():
    result = CliRunner().invoke(main, ["svg2gif", "--help"])
    assert result.exit_code == 0
    assert "--speed" in result.output
    assert "--fps" in result.output
    assert "--loop" in result.output


def test_render_help_only_advertises_implemented_formats():
    result = CliRunner().invoke(main, ["render", "--help"])
    assert result.exit_code == 0
    assert "--format [svg|gif]" in result.output
    assert "svg|gif|cast" not in result.output


def test_svg2gif_wraps_backend_errors(monkeypatch, tmp_path):
    source = tmp_path / "input.svg"
    source.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")

    def fail(*args, **kwargs):
        raise LookupError("browser backend unavailable")

    monkeypatch.setattr("termcap.commands.svg2gif.convert_svg_to_gif", fail)
    result = CliRunner().invoke(main, ["svg2gif", str(source)])

    assert result.exit_code != 0
    assert "browser backend unavailable" in result.output
    assert "Traceback" not in result.output


def test_render_wraps_backend_errors(monkeypatch, tmp_path):
    source = tmp_path / "input.cast"
    source.write_text('{"version": 2, "width": 80, "height": 24}\n', encoding="utf-8")

    def fail(*args, **kwargs):
        raise LookupError("browser backend unavailable")

    monkeypatch.setattr("termcap.commands.render.convert_cast_to_gif", fail)
    result = CliRunner().invoke(
        main,
        ["render", str(source), "--format", "gif"],
    )

    assert result.exit_code != 0
    assert "browser backend unavailable" in result.output
    assert "Traceback" not in result.output


def test_replay_empty_cast_exits_nonzero(tmp_path):
    source = tmp_path / "empty.cast"
    source.write_text("", encoding="utf-8")

    result = CliRunner().invoke(main, ["replay", str(source)])

    assert result.exit_code != 0
    assert "Empty file" in result.output
