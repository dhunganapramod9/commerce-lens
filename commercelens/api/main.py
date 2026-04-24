from __future__ import annotations

from fastapi import FastAPI, HTTPException

from commercelens.core.fetcher import FetchError, fetch_html
from commercelens.extractors.product import extract_product_from_html
from commercelens.schemas.product import ProductExtractionRequest, ProductExtractionResult

app = FastAPI(
    title="CommerceLens API",
    description="Product, catalog, and price intelligence extraction for developers.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "commercelens"}


@app.post("/v1/extract/product", response_model=ProductExtractionResult)
def extract_product_endpoint(request: ProductExtractionRequest) -> ProductExtractionResult:
    if not request.url and not request.html:
        raise HTTPException(status_code=400, detail="Provide either 'url' or 'html'.")

    if request.render:
        raise HTTPException(
            status_code=501,
            detail="Browser rendering is planned for v0.2. Use render=false for v0.1.",
        )

    if request.llm_fallback:
        raise HTTPException(
            status_code=501,
            detail="LLM fallback is planned for v0.3. Use llm_fallback=false for v0.1.",
        )

    url = str(request.url) if request.url else None
    html = request.html

    if not html and url:
        try:
            html = fetch_html(url)
        except FetchError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    assert html is not None
    return extract_product_from_html(html, url=url)
