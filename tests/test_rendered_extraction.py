from commercelens.core.renderer import RenderedPage
from commercelens.extractors import listing as listing_module
from commercelens.extractors import product as product_module


def test_extract_product_with_render_uses_renderer(monkeypatch) -> None:
    def fake_render_html(*args, **kwargs):
        return RenderedPage(
            url="https://example.com/product",
            final_url="https://example.com/product",
            html="""
            <html><body>
              <h1 class="product-title">Rendered Product</h1>
              <span class="price">$20.00</span>
            </body></html>
            """,
            screenshot_path="debug/product.png",
            html_snapshot_path="debug/product.html",
        )

    monkeypatch.setattr(product_module, "render_html", fake_render_html)

    result = product_module.extract_product("https://example.com/product", render=True)

    assert result.product.name == "Rendered Product"
    assert result.product.price is not None
    assert result.product.price.amount == 20.0
    assert result.product.metadata["rendered"] is True
    assert result.product.metadata["screenshot_path"] == "debug/product.png"
    assert result.product.metadata["html_snapshot_path"] == "debug/product.html"


def test_extract_listing_with_render_uses_renderer(monkeypatch) -> None:
    def fake_render_html(*args, **kwargs):
        return RenderedPage(
            url="https://example.com/listing",
            final_url="https://example.com/listing",
            html="""
            <html><body>
              <article class="product_pod">
                <h3><a href="/p/1" title="Rendered Card">Rendered Card</a></h3>
                <p class="price_color">$12.50</p>
              </article>
            </body></html>
            """,
            screenshot_path="debug/listing.png",
            html_snapshot_path="debug/listing.html",
        )

    monkeypatch.setattr(listing_module, "render_html", fake_render_html)

    result = listing_module.extract_listing("https://example.com/listing", render=True)

    assert result.product_count == 1
    assert result.products[0].name == "Rendered Card"
    assert result.products[0].price is not None
    assert result.products[0].price.amount == 12.5
    assert "Saved screenshot to debug/listing.png" in result.warnings
    assert "Saved HTML snapshot to debug/listing.html" in result.warnings
