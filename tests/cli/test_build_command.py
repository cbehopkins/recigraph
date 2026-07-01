"""CLI tests for static-site build command behavior."""

from pathlib import Path

from click.testing import CliRunner

from recigraph.cli import main


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _fixtures_dir() -> Path:
    return _project_root() / "tests" / "fixtures" / "procedures"


def test_build_creates_expected_html_artifacts(tmp_path: Path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "site"

    result = runner.invoke(main, ["build", str(_fixtures_dir()), str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "recipes" / "substitution_base.html").exists()
    assert (output_dir / "recipes" / "vanilla_base.html").exists()


def test_build_reports_summary_to_stdout(tmp_path: Path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "site"

    result = runner.invoke(main, ["build", str(_fixtures_dir()), str(output_dir)])

    assert result.exit_code == 0, result.output
    assert "Built" in result.output
    assert "Compiled recipes:" in result.output
    assert "Artifacts:" in result.output
