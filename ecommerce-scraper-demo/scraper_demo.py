import argparse
import csv
import logging
from pathlib import Path
from urllib.parse import urljoin
from html.parser import HTMLParser


BASE_URL = "https://demo-store.example"


def configure_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


class ProductHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict] = []
        self.current: dict | None = None
        self.current_field: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        class_name = attr_map.get("class", "")

        if tag == "div" and class_name == "product-card":
            self.current = {"product_id": attr_map.get("data-id", "")}
            self.current_field = None
            return

        if self.current is None:
            return

        if tag == "a" and class_name == "details":
            self.current["product_url"] = urljoin(BASE_URL, attr_map.get("href", ""))
            self.current_field = None
            return

        field_map = {
            "name": "name",
            "category": "category",
            "price": "price_usd",
            "rating": "rating",
            "availability": "availability",
        }
        if class_name in field_map:
            self.current_field = field_map[class_name]

    def handle_data(self, data: str) -> None:
        if self.current is None or self.current_field is None:
            return
        value = data.strip()
        if not value:
            return
        if self.current_field == "price_usd":
            self.current["price_usd"] = float(value.replace("$", ""))
        elif self.current_field == "rating":
            self.current["rating"] = float(value.replace(" stars", ""))
        else:
            self.current[self.current_field] = value

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.current is not None:
            required = {"product_id", "name", "category", "price_usd", "rating", "availability", "product_url"}
            if required <= self.current.keys():
                self.items.append(self.current)
            self.current = None
            self.current_field = None


def parse_page(page_path: Path) -> list[dict]:
    parser = ProductHTMLParser()
    parser.feed(page_path.read_text(encoding="utf-8"))
    for item in parser.items:
        item["source_page"] = page_path.name
    return parser.items


def simulate_scale(records: list[dict], multiplier: int) -> list[dict]:
    if multiplier <= 1:
        return records

    expanded = []
    for batch_index in range(multiplier):
        for record in records:
            clone = record.copy()
            clone["product_id"] = f"{record['product_id']}-{batch_index:04d}"
            clone["name"] = f"{record['name']} Batch {batch_index:04d}"
            expanded.append(clone)
    return expanded


def save_csv(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise ValueError("No records available to save.")

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Scrape and clean sample product listings.")
    parser.add_argument("--source-dir", default=project_dir / "data", type=Path)
    parser.add_argument("--simulate-scale", default=1, type=int)
    parser.add_argument("--raw-output", default=project_dir / "output" / "raw_product_listings.csv", type=Path)
    parser.add_argument("--clean-output", default=project_dir / "output" / "clean_product_listings.csv", type=Path)
    parser.add_argument("--log-file", default=project_dir / "logs" / "scraper.log", type=Path)
    args = parser.parse_args()

    configure_logging(args.log_file)

    source_pages = sorted(args.source_dir.glob("page*.html"))
    if not source_pages:
        raise FileNotFoundError(f"No source pages found in {args.source_dir}")

    raw_records: list[dict] = []
    for page_path in source_pages:
        page_records = parse_page(page_path)
        raw_records.extend(page_records)
        logging.info("Parsed %s records from %s", len(page_records), page_path.name)

    raw_records = simulate_scale(raw_records, args.simulate_scale)
    save_csv(raw_records, args.raw_output)
    logging.info("Saved %s raw rows to %s", len(raw_records), args.raw_output)

    deduped: dict[str, dict] = {}
    for record in raw_records:
        deduped[record["product_id"]] = record
    clean_records = [deduped[key] for key in sorted(deduped)]
    save_csv(clean_records, args.clean_output)
    logging.info("Saved %s unique rows to %s", len(clean_records), args.clean_output)


if __name__ == "__main__":
    main()
