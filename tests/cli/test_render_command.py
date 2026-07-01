"""CLI tests for text rendering from example inputs."""

from pathlib import Path

from click.testing import CliRunner

from recigraph.cli import main


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _hello_world_dir() -> Path:
    return _project_root() / "examples" / "001_hello_world"


def _expected_output() -> str:
    expected_path = _hello_world_dir() / "expected" / "output.txt"
    return expected_path.read_text(encoding="utf-8")


def test_render_prints_expected_hello_world_output() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["render", str(_hello_world_dir())])

    assert result.exit_code == 0, result.output
    assert result.output == _expected_output()


def test_render_writes_output_file_when_requested(tmp_path: Path) -> None:
    runner = CliRunner()
    output_path = tmp_path / "hello_world.txt"

    result = runner.invoke(
        main,
        [
            "render",
            str(_hello_world_dir()),
            "--output-file",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert output_path.read_text(encoding="utf-8") == _expected_output()


def test_render_fails_on_unresolved_ingredient_reference(tmp_path: Path) -> None:
    runner = CliRunner()
    example_dir = tmp_path / "bad_example"
    example_dir.mkdir()

    (example_dir / "ingredients.yaml").write_text(
        """
ingredients:
  - id: water
    name: Water
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (example_dir / "procedures.yaml").write_text(
        """
procedures:
  - id: hello_world
    name: Hello World Recipe
    inputs:
      - ingredient.water
      - ingredient.salt
    steps:
      - action: procedure.mix
        inputs:
          - target: ingredient.water
          - target: ingredient.salt
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(main, ["render", str(example_dir)])

    assert result.exit_code != 0
    assert "MISSING_REFERENCE" in result.output


def test_render_requires_procedure_id_when_multiple_entrypoints_exist(tmp_path: Path) -> None:
    runner = CliRunner()
    example_dir = tmp_path / "multi"
    example_dir.mkdir()

    (example_dir / "ingredients.yaml").write_text(
        "ingredients:\n  - id: water\n    name: Water\n  - id: salt\n    name: Salt\n",
        encoding="utf-8",
    )
    (example_dir / "procedures.yaml").write_text(
        "procedures:\n"
        "  - id: hello_world\n"
        "    name: Hello World Recipe\n"
        "    inputs:\n"
        "      - ingredient.water\n"
        "    steps:\n"
        "      - action: procedure.mix\n"
        "        inputs:\n"
        "          - target: ingredient.water\n"
        "  - id: salted_water\n"
        "    name: Salted Water\n"
        "    inputs:\n"
        "      - ingredient.water\n"
        "      - ingredient.salt\n"
        "    steps:\n"
        "      - action: procedure.mix\n"
        "        inputs:\n"
        "          - target: ingredient.water\n"
        "          - target: ingredient.salt\n",
        encoding="utf-8",
    )

    result = runner.invoke(main, ["render", str(example_dir)])

    assert result.exit_code != 0
    assert "Multiple entrypoint procedures found" in result.output


def test_render_infers_single_entrypoint_when_multiple_procedures_exist(tmp_path: Path) -> None:
    runner = CliRunner()
    example_dir = tmp_path / "infer_entrypoint"
    example_dir.mkdir()

    (example_dir / "ingredients.yaml").write_text(
        "ingredients:\n  - id: water\n    name: Water\n",
        encoding="utf-8",
    )
    (example_dir / "procedures.yaml").write_text(
        "procedures:\n"
        "  - id: base_recipe\n"
        "    name: Base Recipe\n"
        "    inputs:\n"
        "      - ingredient.water\n"
        "    steps:\n"
        "      - action: procedure.mix\n"
        "        inputs:\n"
        "          - target: ingredient.water\n"
        "  - id: main_recipe\n"
        "    name: Main Recipe\n"
        "    steps:\n"
        "      - action: procedure.base_recipe\n",
        encoding="utf-8",
    )

    result = runner.invoke(main, ["render", str(example_dir)])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("Main Recipe")
    assert "Mix water." in result.output


def test_render_can_select_specific_procedure_from_multi_file(tmp_path: Path) -> None:
    runner = CliRunner()
    example_dir = tmp_path / "multi"
    example_dir.mkdir()

    (example_dir / "ingredients.yaml").write_text(
        "ingredients:\n  - id: water\n    name: Water\n  - id: salt\n    name: Salt\n",
        encoding="utf-8",
    )
    (example_dir / "procedures.yaml").write_text(
        "procedures:\n"
        "  - id: hello_world\n"
        "    name: Hello World Recipe\n"
        "    inputs:\n"
        "      - ingredient.water\n"
        "    steps:\n"
        "      - action: procedure.mix\n"
        "        inputs:\n"
        "          - target: ingredient.water\n"
        "  - id: salted_water\n"
        "    name: Salted Water\n"
        "    inputs:\n"
        "      - ingredient.water\n"
        "      - ingredient.salt\n"
        "    steps:\n"
        "      - action: procedure.mix\n"
        "        inputs:\n"
        "          - target: ingredient.water\n"
        "          - target: ingredient.salt\n",
        encoding="utf-8",
    )

    result = runner.invoke(main, ["render", str(example_dir), "--procedure-id", "salted_water"])

    assert result.exit_code == 0, result.output
    assert result.output.startswith("Salted Water")
    assert "Mix water and salt." in result.output
