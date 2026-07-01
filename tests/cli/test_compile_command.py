"""CLI tests for graph compilation command behavior."""

from pathlib import Path

from click.testing import CliRunner

from recigraph.cli import main


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _hello_world_dir() -> Path:
    return _project_root() / "examples" / "001_hello_world"


def test_compile_prints_graph_summary_for_single_example() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["compile", str(_hello_world_dir())])

    assert result.exit_code == 0, result.output
    assert "Procedure: procedure.hello_world" in result.output
    assert "Final graph snapshot:" in result.output
    assert "Trace length:" in result.output


def test_compile_writes_json_output_file(tmp_path: Path) -> None:
    runner = CliRunner()
    output_file = tmp_path / "compiled.json"

    result = runner.invoke(
        main,
        ["compile", str(_hello_world_dir()), "--output-file", str(output_file)],
    )

    assert result.exit_code == 0, result.output
    content = output_file.read_text(encoding="utf-8")
    assert '"final_graph"' in content
    assert '"trace"' in content
