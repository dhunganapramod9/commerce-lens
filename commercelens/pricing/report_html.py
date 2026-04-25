from __future__ import annotations

from html import escape

from commercelens.pricing.recommendations import MarginLeakReport, PricingRecommendation, RecommendationAction


ACTION_LABELS = {
    RecommendationAction.DO_NOT_MATCH: "Do not match",
    RecommendationAction.MATCH_OR_NEAR_MATCH: "Match or near match",
    RecommendationAction.HOLD_OR_RAISE: "Hold or raise",
    RecommendationAction.CONSIDER_RAISE: "Consider raise",
    RecommendationAction.NEEDS_REVIEW: "Needs review",
}


def render_margin_leak_report_html(report: MarginLeakReport) -> str:
    title = f"{report.store_name or 'CommerceLens'} Margin Leak Report"
    rows = "\n".join(_recommendation_row(item) for item in report.recommendations)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #637083;
      --line: #dde3ea;
      --panel: #ffffff;
      --page: #f6f8fb;
      --danger: #b42318;
      --danger-bg: #fff1f0;
      --success: #067647;
      --success-bg: #ecfdf3;
      --warn: #b54708;
      --warn-bg: #fffaeb;
      --info: #175cd3;
      --info-bg: #eff8ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 24px 56px;
    }}
    header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 28px;
    }}
    h1 {{
      margin: 0;
      font-size: 34px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .subtitle {{
      margin: 12px 0 0;
      max-width: 720px;
      color: var(--muted);
      font-size: 16px;
    }}
    .stamp {{
      min-width: 210px;
      color: var(--muted);
      text-align: right;
      font-size: 14px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 104px;
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 26px;
      line-height: 1.1;
    }}
    .metric span {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }}
    .summary {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
      gap: 16px;
      margin-bottom: 16px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .panel h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .action-list {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .action-item {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
    }}
    .action-item span {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }}
    .action-item strong {{
      display: block;
      margin-top: 4px;
      font-size: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 13px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      color: var(--muted);
      background: #fbfcfe;
      font-size: 12px;
      text-transform: uppercase;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .product {{
      min-width: 180px;
      font-weight: 700;
    }}
    .sku {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }}
    .explanation {{
      min-width: 280px;
      max-width: 420px;
      color: #344054;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
    }}
    .danger {{ color: var(--danger); background: var(--danger-bg); }}
    .success {{ color: var(--success); background: var(--success-bg); }}
    .warn {{ color: var(--warn); background: var(--warn-bg); }}
    .info {{ color: var(--info); background: var(--info-bg); }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 920px) {{
      header, .summary {{ display: block; }}
      .stamp {{ text-align: left; margin-top: 14px; }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .action-list {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
    }}
    @media (max-width: 560px) {{
      main {{ padding: 28px 14px 42px; }}
      h1 {{ font-size: 28px; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <p class="eyebrow">CommerceLens</p>
        <h1>{escape(title)}</h1>
        <p class="subtitle">Weekly pricing actions ranked by margin risk, competitor movement, and safe raise opportunities.</p>
      </div>
      <div class="stamp">
        <div>Report ID: {escape(report.report_id)}</div>
        <div>Created: {escape(report.created_at)}</div>
      </div>
    </header>

    <section class="grid" aria-label="Report summary">
      {_metric("Products checked", report.products_checked)}
      {_metric("Competitor URLs", report.competitor_urls_checked)}
      {_metric("Unsafe matches", report.unsafe_matches_count)}
      {_metric("Safe raises", report.safe_raise_count)}
      {_metric("Margin at risk", _money(report.estimated_margin_at_risk))}
    </section>

    <section class="summary">
      <div class="panel">
        <h2>This Week's Actions</h2>
        <div class="action-list">
          {_action_item("Do not match", report.unsafe_matches_count, "Protect margin floors")}
          {_action_item("Consider raise", report.safe_raise_count, "Capture pricing room")}
          {_action_item("Match or near match", report.match_opportunities_count, "Compete safely")}
          {_action_item("Hold or raise", report.out_of_stock_competitors_count, "Ignore unavailable competitors")}
        </div>
      </div>
      <div class="panel">
        <h2>Operator Note</h2>
        <p class="muted">Review high-risk actions first. CommerceLens is intentionally approval-first: every recommendation explains the margin math before any price change.</p>
      </div>
    </section>

    <table>
      <thead>
        <tr>
          <th>Product</th>
          <th>Action</th>
          <th>Current</th>
          <th>Competitor</th>
          <th>Safe Price</th>
          <th>Recommended</th>
          <th>Impact</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </main>
</body>
</html>"""


def _metric(label: str, value: object) -> str:
    return f"""<div class="metric"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>"""


def _action_item(label: str, value: int, note: str) -> str:
    return (
        f"""<div class="action-item"><span>{escape(note)}</span>"""
        f"""<strong>{escape(str(value))} {escape(label)}</strong></div>"""
    )


def _recommendation_row(item: PricingRecommendation) -> str:
    action_label = ACTION_LABELS[item.recommended_action]
    return f"""<tr>
  <td><div class="product">{escape(item.product_name)}</div><div class="sku">{escape(item.sku)}</div></td>
  <td><span class="pill {_pill_class(item.recommended_action)}">{escape(action_label)}</span></td>
  <td>{_money(item.current_price)}<div class="sku">{item.current_margin_percent:.2f}% margin</div></td>
  <td>{escape(item.competitor_name or 'No competitor')}<div class="sku">{_money_or_dash(item.competitor_price)} {_availability(item)}</div></td>
  <td>{_money(item.minimum_safe_price)}</td>
  <td>{_money_or_dash(item.recommended_price)}</td>
  <td>{_money_or_dash(item.estimated_impact)}</td>
  <td class="explanation">{escape(item.explanation)}</td>
</tr>"""


def _pill_class(action: RecommendationAction) -> str:
    if action == RecommendationAction.DO_NOT_MATCH:
        return "danger"
    if action == RecommendationAction.CONSIDER_RAISE:
        return "success"
    if action == RecommendationAction.HOLD_OR_RAISE:
        return "info"
    return "warn"


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _money_or_dash(value: float | None) -> str:
    if value is None:
        return "-"
    return _money(value)


def _availability(item: PricingRecommendation) -> str:
    if not item.competitor_availability:
        return ""
    return f" / {escape(item.competitor_availability)}"
