import argparse
import json
import logging
import sqlite3
from pathlib import Path


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


def load_mock_pages(data_dir: Path) -> list[dict]:
    pages = []
    for json_path in sorted(data_dir.glob("mock_crm_page_*.json")):
        with json_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        pages.append(payload)
    if not pages:
        raise FileNotFoundError(f"No mock CRM payloads found in {data_dir}")
    return pages


def flatten_contacts(pages: list[dict]) -> list[dict]:
    contacts = []
    for page in pages:
        page_number = page["page"]
        for item in page["data"]:
            contacts.append(
                {
                    "contact_id": item["contact_id"],
                    "email": item["email"].strip().lower(),
                    "full_name": item["full_name"].strip(),
                    "company": item["company"].strip(),
                    "lifecycle_stage": item["lifecycle_stage"].strip(),
                    "owner": item["owner"].strip(),
                    "updated_at": item["updated_at"],
                    "source_page": page_number,
                }
            )
    return contacts


def simulate_records(records: list[dict], target_count: int) -> list[dict]:
    if target_count <= len(records):
        return records

    expanded = []
    batch = 0
    while len(expanded) < target_count:
        for record in records:
            clone = record.copy()
            clone["contact_id"] = f"{record['contact_id']}-{batch:05d}"
            clone["email"] = record["email"].replace("@", f"+{batch:05d}@")
            clone["full_name"] = f"{record['full_name']} Batch {batch:05d}"
            expanded.append(clone)
            if len(expanded) >= target_count:
                break
        batch += 1
    return expanded


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            contact_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            company TEXT NOT NULL,
            lifecycle_stage TEXT NOT NULL,
            owner TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            source_page INTEGER NOT NULL
        )
        """
    )
    connection.commit()


def upsert_contacts(connection: sqlite3.Connection, records: list[dict]) -> None:
    connection.executemany(
        """
        INSERT INTO contacts (
            contact_id, email, full_name, company, lifecycle_stage, owner, updated_at, source_page
        ) VALUES (
            :contact_id, :email, :full_name, :company, :lifecycle_stage, :owner, :updated_at, :source_page
        )
        ON CONFLICT(contact_id) DO UPDATE SET
            email = excluded.email,
            full_name = excluded.full_name,
            company = excluded.company,
            lifecycle_stage = excluded.lifecycle_stage,
            owner = excluded.owner,
            updated_at = excluded.updated_at,
            source_page = excluded.source_page
        """,
        records,
    )
    connection.commit()


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Sync mock CRM API data into SQLite.")
    parser.add_argument("--data-dir", default=project_dir / "data", type=Path)
    parser.add_argument("--database", default=project_dir / "output" / "crm_sync.db", type=Path)
    parser.add_argument("--log-file", default=project_dir / "logs" / "crm_sync.log", type=Path)
    parser.add_argument("--simulate-records", default=0, type=int)
    args = parser.parse_args()

    configure_logging(args.log_file)

    pages = load_mock_pages(args.data_dir)
    contacts = flatten_contacts(pages)
    if args.simulate_records:
        contacts = simulate_records(contacts, args.simulate_records)
        logging.info("Expanded sync payload to %s records for volume testing", len(contacts))
    else:
        logging.info("Loaded %s records from mock CRM pages", len(contacts))

    args.database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.database) as connection:
        ensure_schema(connection)
        upsert_contacts(connection, contacts)
        row_count = connection.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        logging.info("Database now contains %s contact rows", row_count)


if __name__ == "__main__":
    main()
