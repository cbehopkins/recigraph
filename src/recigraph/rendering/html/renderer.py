"""Minimal HTML renderer for the v1 vertical slice."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from recigraph.rendering.common.artifact import RenderArtifact
from recigraph.rendering.common.result import RenderResult
from recigraph.rendering.common.view_model import ViewModel
from recigraph.rendering.html.view_models import RecipeSiteViewModel


class HtmlRenderer:
    """Render recipe site view models into a static HTML artifact set."""

    name = "html"

    def __init__(self) -> None:
        templates_path = Path(__file__).resolve().parent / "templates"
        self._environment = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape(("html", "xml")),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, model: ViewModel, output_dir: Path) -> RenderResult:
        """Render index and recipe pages from a recipe-site view model."""

        if not isinstance(model, RecipeSiteViewModel):
            raise TypeError("HtmlRenderer expects RecipeSiteViewModel")

        recipes_dir = output_dir / "recipes"
        recipes_dir.mkdir(parents=True, exist_ok=True)

        artifacts: list[RenderArtifact] = []
        index_template = self._environment.get_template("index.html.j2")
        recipe_template = self._environment.get_template("recipe.html.j2")

        for page in model.pages:
            recipe_relative_path = Path("recipes") / f"{page.slug}.html"
            recipe_path = output_dir / recipe_relative_path
            recipe_html = recipe_template.render(page=page)
            recipe_path.write_text(recipe_html, encoding="utf-8")
            artifacts.append(
                RenderArtifact(relative_path=recipe_relative_path, media_type="text/html")
            )

        index_relative_path = Path("index.html")
        index_path = output_dir / index_relative_path
        index_html = index_template.render(pages=model.pages)
        index_path.write_text(index_html, encoding="utf-8")
        artifacts.insert(
            0,
            RenderArtifact(relative_path=index_relative_path, media_type="text/html"),
        )

        return RenderResult(renderer_name=self.name, artifacts=tuple(artifacts))
