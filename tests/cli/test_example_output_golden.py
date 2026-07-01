"""Golden output tests for example render text."""

from pathlib import Path

from click.testing import CliRunner

from recigraph.cli import main


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_render_examples_match_expected_output_files() -> None:
    runner = CliRunner()
    examples = (
        "001_hello_world",
        "002_simple",
        "003_equipment",
        "004_substitution",
        "005_shared_procedure",
    )

    for example_name in examples:
        example_dir = _project_root() / "examples" / example_name
        expected_path = example_dir / "expected" / "output.txt"
        expected_text = expected_path.read_text(encoding="utf-8")

        result = runner.invoke(main, ["render", str(example_dir)])

        assert result.exit_code == 0, result.output
        assert result.output == expected_text
