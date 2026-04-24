from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from commercelens.extractors.product import extract_product, extract_product_from_html

app = typer.Typer(help="CommerceLens: product and catalog extraction for developers.")
console = Console()


@app.command()
def product(
    url: str = typer.Argument(..., help="Product page URL to extract."),
    out: Path | None = typer.Option(None, "--out", "-o", help="Optional JSON output path."),
) -> None:
    """Extract a normalized product object from a product page URL."""
    result = extract_product(url)
    payload = result.model_dump(mode="json", exclude_none=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if out:
        out.write_text(text, encoding="utf-8")
        console.print(f"[green]Wrote extraction result to {out}[/green]")
    else:
        console.print_json(text)


@app.command()
def html(
    path: Path = typer.Argument(..., help="Local HTML file to extract from."),
    url: str | None = typer.Option(None, "--url", help="Optional source URL for resolving relative links."),
    out: Path | None = typer.Option(None, "--out", "-o", help="Optional JSON output path."),
) -> None:
    """Extract a normalized product object from a local HTML file."""
    result = extract_product_from_html(path.read_text(encoding="utf-8"), url=url)
    payload = result.model_dump(mode="json", exclude_none=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if out:
        out.write_text(text, encoding="utf-8")
        console.print(f"[green]Wrote extraction result to {out}[/green]")
    else:
        console.print_json(text)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host to bind."),
    port: int = typer.Option(8000, help="Port to bind."),
    reload: bool = typer.Option(False, help="Enable development reload."),
) -> None:
    """Run the CommerceLens FastAPI server."""
    import uvicorn

    uvicorn.run("commercelens.api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
