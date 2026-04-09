import json
import random
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PAGES_DIR = DATA_DIR / "pages"
IMAGES_DIR = DATA_DIR / "images"

TOPICS = [
    "Platform Reliability",
    "Incident Response",
    "Product Roadmaps",
    "Design Systems",
    "Security Standards",
    "Engineering Onboarding",
    "API Guidelines",
    "Release Management",
    "Data Governance",
    "Customer Support",
    "Architecture Decision Records",
    "Sprint Rituals",
]

IMAGE_MAP = {
    "Platform Reliability": "diagram-ops.svg",
    "Incident Response": "diagram-ops.svg",
    "Product Roadmaps": "diagram-release.svg",
    "Design Systems": "diagram-design.svg",
    "Security Standards": "diagram-security.svg",
    "Engineering Onboarding": "diagram-architecture.svg",
    "API Guidelines": "diagram-pipeline.svg",
    "Release Management": "diagram-release.svg",
    "Data Governance": "diagram-architecture.svg",
    "Customer Support": "diagram-ops.svg",
    "Architecture Decision Records": "diagram-architecture.svg",
    "Sprint Rituals": "diagram-pipeline.svg",
}

LABELS = [
    "engineering",
    "product",
    "design",
    "security",
    "operations",
    "data",
    "process",
]


def confluence_css() -> str:
    return """
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; color: #172B4D; background: #FFFFFF; }
.page { max-width: 920px; margin: 24px auto; padding: 0 16px; }
.page h1 { font-size: 28px; margin-bottom: 8px; }
.page h2 { font-size: 20px; margin-top: 24px; }
.page h3 { font-size: 16px; margin-top: 18px; }
.page p { line-height: 1.6; color: #42526E; }
.meta { color: #6B778C; font-size: 12px; margin-bottom: 16px; }
.callout { background: #DEEBFF; border-left: 4px solid #0052CC; padding: 12px 16px; margin: 16px 0; }
.table { width: 100%; border-collapse: collapse; margin: 12px 0; }
.table th, .table td { border: 1px solid #DFE1E6; padding: 8px; }
.code { background: #F4F5F7; border-radius: 6px; padding: 12px; font-family: Consolas, monospace; }
.tag { display: inline-block; background: #EAE6FF; color: #403294; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 6px; }
img { width: 100%; margin: 12px 0; border: 1px solid #DFE1E6; border-radius: 8px; }
</style>
"""


def build_page(page_id: str, title: str, topic: str, labels: list[str]) -> str:
    image_name = IMAGE_MAP.get(topic, "diagram-architecture.svg")
    image_path = f"../images/{image_name}"

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{confluence_css()}
</head>
<body>
<div class="page">
  <h1>{title}</h1>
  <div class="meta">Last updated: {datetime.utcnow().date().isoformat()} · Topic: {topic}</div>
  <div>
    {''.join([f'<span class="tag">{l}</span>' for l in labels])}
  </div>

  <p>This page captures our internal guidance for <strong>{topic}</strong>. Use this as a reference when aligning with cross-functional teams and when documenting new decisions.</p>

  <div class="callout">
    Key takeaway: Keep decisions explicit, document assumptions, and measure outcomes.
  </div>

  <h2>Overview</h2>
  <p>We standardize workflows to improve clarity, reduce rework, and increase operational confidence across teams.</p>
  <img src="{image_path}" alt="{topic} diagram" />

  <h2>Decision Checklist</h2>
  <table class="table">
    <thead>
      <tr><th>Step</th><th>Owner</th><th>Outcome</th></tr>
    </thead>
    <tbody>
      <tr><td>Define scope</td><td>Lead</td><td>Clear boundaries</td></tr>
      <tr><td>Assess impact</td><td>Team</td><td>Risk visibility</td></tr>
      <tr><td>Document plan</td><td>PM</td><td>Execution path</td></tr>
    </tbody>
  </table>

  <h2>Operational Notes</h2>
  <ul>
    <li>Review dependencies weekly.</li>
    <li>Keep SLAs visible for stakeholders.</li>
    <li>Track follow-up actions.</li>
  </ul>

  <h2>Implementation Snippet</h2>
  <div class="code">
  GET /api/{page_id}/status\n  200 OK\n  {{ "status": "green" }}
  </div>

  <h3>Related Links</h3>
  <p>See also: incident triage checklist, rollout guidelines, and monitoring standards.</p>
</div>
</body>
</html>
"""


def main() -> None:
    random.seed(42)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    pages = []
    total_pages = 36

    for idx in range(1, total_pages + 1):
        topic = random.choice(TOPICS)
        title = f"{topic} Playbook #{idx:02d}"
        page_id = f"page-{idx:03d}"
        labels = random.sample(LABELS, k=3)

        html = build_page(page_id, title, topic, labels)
        html_path = PAGES_DIR / f"{page_id}.html"
        html_path.write_text(html, encoding="utf-8")

        pages.append(
            {
                "id": page_id,
                "title": title,
                "topic": topic,
                "labels": labels,
                "html_path": f"pages/{page_id}.html",
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    (PAGES_DIR / "pages.json").write_text(
        json.dumps(pages, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
