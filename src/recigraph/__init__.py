# Version is derived from Git tags via setuptools-scm at build time.
# At runtime it is read from the installed package metadata so there is
# no version string duplicated in source.
#
# Usage:
#   from importlib.metadata import version
#   version("recigraph")
#
# Or via the convenience attribute exposed here:
#   import recigraph
#   recigraph.__version__
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _meta_version

try:
    __version__: str = _meta_version("recigraph")
except PackageNotFoundError:
    # Package is not installed (e.g. running directly from the source tree
    # without `uv sync` or `pip install -e .`).
    __version__ = "0.0.0.dev0+uninstalled"
