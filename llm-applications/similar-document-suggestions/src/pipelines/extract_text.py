import json
from pathlib import Path
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PAGES_DIR = DATA_DIR / "pages"
OUTPUT_PATH = DATA_DIR / "extracted" / "pages_text.json"


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text_blocks = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "td"]):
        content = tag.get_text(" ", strip=True)
        if content:
            text_blocks.append(content)

    return "\n".join(text_blocks)


def main() -> None:
    pages_file = PAGES_DIR / "pages.json"
    if not pages_file.exists():
        raise SystemExit("pages.json not found. Run generate_pages.py first.")

    pages = json.loads(pages_file.read_text(encoding="utf-8"))
    output = []

    for page in pages:
        html_path = DATA_DIR / page["html_path"]
        html = html_path.read_text(encoding="utf-8")
        text = html_to_text(html)
        output.append(
            {
                "id": page["id"],
                "title": page["title"],
                "labels": page["labels"],
                "html_path": page["html_path"],
                "text": text,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
