"""Package-level smoke tests.

These are not unit tests for any specific feature.  They exist to ensure the
package is importable and the version machinery works correctly.  Real feature
tests live in the subdirectories alongside the modules they cover.
"""

from importlib.metadata import PackageNotFoundError, version


def test_package_is_importable() -> None:
    import recigraph

    _ = recigraph.__version__


def test_version_attribute_is_a_string() -> None:
    import recigraph

    assert isinstance(recigraph.__version__, str)
    assert len(recigraph.__version__) > 0


def test_importlib_metadata_version_consistent() -> None:
    import recigraph

    try:
        meta_version = version("recigraph")
        assert recigraph.__version__ == meta_version
    except PackageNotFoundError:
        # Package not installed (running from raw source tree) — the
        # fallback sentinel is acceptable here.
        assert recigraph.__version__ == "0.0.0.dev0+uninstalled"
