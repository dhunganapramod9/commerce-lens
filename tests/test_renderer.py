import pytest

from commercelens.core.renderer import RenderError, render_html


def test_render_html_reports_missing_playwright_cleanly() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        with pytest.raises(RenderError) as exc:
            render_html("https://example.com")
        assert "Playwright is not installed" in str(exc.value)
    else:
        pytest.skip("Playwright is installed in this environment; integration rendering is not run here.")
