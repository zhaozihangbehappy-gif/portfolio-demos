import argparse
import csv
import logging
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


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


def normalize_status(value: str) -> str:
    cleaned = str(value).strip().lower().replace("_", " ")
    mapping = {
        "done": "Completed",
        "complete": "Completed",
        "completed": "Completed",
        "in progress": "In Progress",
        "inprogress": "In Progress",
        "blocked": "Blocked",
    }
    return mapping.get(cleaned, cleaned.title())


def read_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_sheet_xml(rows: list[list]) -> str:
    def column_name(index: int) -> str:
        name = ""
        current = index
        while current >= 0:
            current, remainder = divmod(current, 26)
            name = chr(65 + remainder) + name
            current -= 1
        return name

    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row):
            if value is None:
                continue
            cell_ref = f"{column_name(col_index)}{row_index}"
            if isinstance(value, (int, float)):
                cells.append(f'<c r="{cell_ref}"><v>{value}</v></c>')
            else:
                cells.append(
                    f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                )
        xml_rows.append(f"<row r=\"{row_index}\">{''.join(cells)}</row>")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(xml_rows)}</sheetData>"
        "</worksheet>"
    )


def write_xlsx(path: Path, sheets: list[tuple[str, list[list]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    relationships = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>',
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>',
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>',
        "</Relationships>",
    ]
    workbook_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    workbook_xml = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>',
    ]

    for index, (sheet_name, _) in enumerate(sheets, start=1):
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        workbook_rels.append(
            f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
        workbook_xml.append(f'<sheet name="{escape(sheet_name)}" sheetId="{index}" r:id="rId{index}"/>')

    content_types.append("</Types>")
    workbook_rels.append("</Relationships>")
    workbook_xml.append("</sheets></workbook>")

    app_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        "<Application>Python</Application>"
        "</Properties>"
    )
    core_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        "</cp:coreProperties>"
    )

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "".join(content_types))
        archive.writestr("_rels/.rels", "".join(relationships))
        archive.writestr("docProps/app.xml", app_xml)
        archive.writestr("docProps/core.xml", core_xml)
        archive.writestr("xl/workbook.xml", "".join(workbook_xml))
        archive.writestr("xl/_rels/workbook.xml.rels", "".join(workbook_rels))
        for index, (_, rows) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", build_sheet_xml(rows))


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate a weekly Excel operations report.")
    parser.add_argument("--input", default=project_dir / "data" / "weekly_operations.csv", type=Path)
    parser.add_argument("--workbook-output", default=project_dir / "output" / "weekly_operations_report.xlsx", type=Path)
    parser.add_argument("--summary-output", default=project_dir / "output" / "team_summary.csv", type=Path)
    parser.add_argument("--log-file", default=project_dir / "logs" / "excel_automation.log", type=Path)
    args = parser.parse_args()

    configure_logging(args.log_file)

    raw_rows = read_csv_rows(args.input)
    logging.info("Loaded %s rows from %s", len(raw_rows), args.input)

    clean_rows = []
    for row in raw_rows:
        manual_before = float(row["manual_minutes_before"] or 0)
        automated_after = float(row["automated_minutes_after"] or 0)
        clean_rows.append(
            {
                "report_week": row["report_week"],
                "team": row["team"].strip().title(),
                "owner": (row["owner"] or "Unassigned").strip().title() or "Unassigned",
                "workflow_name": row["workflow_name"].strip(),
                "status": normalize_status(row["status"]),
                "manual_minutes_before": manual_before,
                "automated_minutes_after": automated_after,
                "hours_saved": round(max(manual_before - automated_after, 0) / 60, 2),
                "revenue_impact_usd": float(row["revenue_impact_usd"] or 0),
            }
        )

    completed_count = sum(1 for row in clean_rows if row["status"] == "Completed")
    total_manual_hours = round(sum(row["manual_minutes_before"] for row in clean_rows) / 60, 2)
    total_hours_saved = round(sum(row["hours_saved"] for row in clean_rows), 2)
    total_revenue = round(sum(row["revenue_impact_usd"] for row in clean_rows), 2)

    weekly_summary = [
        {"metric": "Rows Processed", "value": len(clean_rows)},
        {"metric": "Completed Tasks", "value": completed_count},
        {"metric": "Manual Hours Before", "value": total_manual_hours},
        {"metric": "Hours Saved", "value": total_hours_saved},
        {"metric": "Revenue Impact USD", "value": total_revenue},
    ]

    team_map: dict[str, dict] = {}
    for row in clean_rows:
        entry = team_map.setdefault(
            row["team"],
            {"team": row["team"], "tasks": 0, "completed": 0, "hours_saved": 0.0, "revenue_impact_usd": 0.0},
        )
        entry["tasks"] += 1
        entry["completed"] += int(row["status"] == "Completed")
        entry["hours_saved"] += row["hours_saved"]
        entry["revenue_impact_usd"] += row["revenue_impact_usd"]

    team_summary = sorted(
        (
            {
                "team": team,
                "tasks": values["tasks"],
                "completed": values["completed"],
                "hours_saved": round(values["hours_saved"], 2),
                "revenue_impact_usd": round(values["revenue_impact_usd"], 2),
            }
            for team, values in team_map.items()
        ),
        key=lambda item: (item["hours_saved"], item["revenue_impact_usd"]),
        reverse=True,
    )

    write_csv_rows(args.summary_output, team_summary)

    workbook_sheets = [
        ("Raw_Data", [list(raw_rows[0].keys())] + [list(row.values()) for row in raw_rows]),
        ("Cleaned_Data", [list(clean_rows[0].keys())] + [list(row.values()) for row in clean_rows]),
        ("Weekly_Summary", [list(weekly_summary[0].keys())] + [list(row.values()) for row in weekly_summary]),
        ("Team_Summary", [list(team_summary[0].keys())] + [list(row.values()) for row in team_summary]),
    ]
    write_xlsx(args.workbook_output, workbook_sheets)

    logging.info("Saved workbook to %s", args.workbook_output)
    logging.info("Saved team summary to %s", args.summary_output)


if __name__ == "__main__":
    main()
