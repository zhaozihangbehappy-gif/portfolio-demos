# E-commerce Scraper Demo

Portfolio demo that extracts product listings from a paginated storefront archive, normalizes the records, removes duplicates, and exports clean CSV files.

## What this demo shows

- Multi-page HTML parsing with the Python standard library
- Product normalization for price, rating, category, and URL
- Deduplication by product ID
- Clean CSV delivery for downstream analytics
- Optional volume simulation to stress-test the pipeline at 50K+ rows

## Files

- `scraper_demo.py` - scraper and data-cleaning pipeline
- `data/page1.html` to `data/page3.html` - sample storefront pages
- `output/` - generated CSV outputs
- `logs/` - execution logs

## Run

```bash
python scraper_demo.py
```

To simulate a larger extraction workload:

```bash
python scraper_demo.py --simulate-scale 6000
```

That mode expands the sample product set to stress-test the CSV and dedup workflow with 50K+ rows.

## Output

- `output/raw_product_listings.csv`
- `output/clean_product_listings.csv`

The clean export contains one row per unique product ID.

## Notes

This is a portfolio demo built to represent a typical e-commerce extraction workflow. It uses a local paginated storefront sample so the pipeline is fully reproducible.
