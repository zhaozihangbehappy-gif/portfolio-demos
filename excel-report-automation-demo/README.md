# Excel Report Automation Demo

Portfolio demo that takes a messy weekly operations export and turns it into a clean Excel workbook with summary tabs and reporting metrics.

## What this demo shows

- One-click spreadsheet automation
- Data cleaning for status values, owner names, and numeric fields
- Weekly summary metrics for manual hours and time saved
- Team-level reporting output for managers
- Excel workbook generation with multiple sheets

## Files

- `automate_weekly_report.py` - reporting workflow
- `data/weekly_operations.csv` - sample raw operations export
- `output/weekly_operations_report.xlsx` - generated workbook
- `output/team_summary.csv` - generated summary table

## Run

```bash
python automate_weekly_report.py
```

## Sheets generated

- `Raw_Data`
- `Cleaned_Data`
- `Weekly_Summary`
- `Team_Summary`

## Notes

This is a portfolio demo built to represent a weekly reporting workflow that replaces repeated manual spreadsheet cleanup with a single command.
