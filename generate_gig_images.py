"""Generate Fiverr gig gallery images (712x430 minimum)."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import csv

OUTPUT_DIR = Path(__file__).parent / "gig_images"
OUTPUT_DIR.mkdir(exist_ok=True)

W, H = 1200, 720
BG = (15, 23, 42)
ACCENT = (56, 189, 248)
WHITE = (255, 255, 255)
GRAY = (148, 163, 184)
ROW_ALT = (22, 33, 55)
HEADER_BG = (30, 58, 95)

try:
    font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
    font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 28)
    font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 36)
except:
    font_sm = ImageFont.load_default()
    font_md = font_sm
    font_lg = font_sm
    font_xl = font_sm


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)


# === IMAGE 1: CSV Data Table ===
def make_data_image():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((40, 30), "Web Scraper Output — Clean CSV", fill=ACCENT, font=font_xl)
    draw.text((40, 75), "10 products extracted, deduplicated, ready for analysis", fill=GRAY, font=font_md)

    csv_path = Path(__file__).parent / "ecommerce-scraper-demo" / "output" / "clean_product_listings.csv"
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    headers = ["ID", "Product Name", "Category", "Price", "Rating", "Stock"]
    col_x = [40, 130, 420, 600, 700, 800]

    y = 120
    draw_rounded_rect(draw, (30, y - 5, W - 30, y + 30), 5, HEADER_BG)
    for i, h in enumerate(headers):
        draw.text((col_x[i], y), h, fill=ACCENT, font=font_md)

    y = 155
    for row_idx, row in enumerate(rows[1:], 1):
        if y > H - 40:
            break
        if row_idx % 2 == 0:
            draw.rectangle([30, y - 2, W - 30, y + 28], fill=ROW_ALT)

        cells = [
            row[0].replace("P-", ""),
            row[1][:28],
            row[2],
            f"${row[3]}",
            f"{'★' * int(float(row[4]))} {row[4]}",
            row[5],
        ]
        for i, cell in enumerate(cells):
            color = WHITE if i != 4 else (250, 204, 21)
            draw.text((col_x[i], y), cell, fill=color, font=font_sm)
        y += 32

    draw.line([(30, 148), (W - 30, 148)], fill=ACCENT, width=1)

    # footer
    draw.text((40, H - 50), "✓ Deduplicated   ✓ Formatted   ✓ CSV Export Ready", fill=GRAY, font=font_sm)

    img.save(OUTPUT_DIR / "gig_image_1_data.png")
    print(f"Saved {OUTPUT_DIR / 'gig_image_1_data.png'}")


# === IMAGE 2: Code Preview ===
def make_code_image():
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, W, 40], fill=(35, 35, 50))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([15 + i * 25, 12, 31 + i * 25, 28], fill=color)
    draw.text((110, 10), "scraper_demo.py — Python", fill=GRAY, font=font_sm)

    code_lines = [
        ('keyword', 'import'),    (' default', ' argparse, csv, logging'),
        ('keyword', 'from'),      (' default', ' pathlib '), ('keyword', 'import'), (' default', ' Path'),
        ('', ''),
        ('keyword', 'class'), (' class_name', ' ProductHTMLParser'), ('default', '(HTMLParser):'),
        ('    comment', '    # Parse product cards from HTML pages'),
        ('    keyword', '    def'), (' func', ' parse_page'), ('default', '(self, page_path):'),
        ('        default', '        parser.feed(page_path.read_text())'),
        ('        keyword', '        for'), (' default', ' item '), ('keyword', 'in'), (' default', ' parser.items:'),
        ('            default', '            item["source_page"] = page_path.name'),
        ('', ''),
        ('keyword', 'def'), (' func', ' save_csv'), ('default', '(records, path):'),
        ('    string', '    """Save records to CSV with headers."""'),
        ('    keyword', '    with'), (' default', ' path.open("w") '), ('keyword', 'as'), (' default', ' handle:'),
        ('        default', '        writer = csv.DictWriter(handle, ...)'),
        ('        default', '        writer.writeheader()'),
        ('        default', '        writer.writerows(records)'),
        ('', ''),
        ('keyword', 'def'), (' func', ' main'), ('default', '():'),
        ('    comment', '    # Scrape → Clean → Deduplicate → Export'),
        ('    default', '    raw_records = parse_all_pages(source_dir)'),
        ('    default', '    clean = deduplicate(raw_records)'),
        ('    default', '    save_csv(clean, output_path)'),
        ('    default', '    logging.info("Saved %s rows", len(clean))'),
    ]

    COLORS = {
        'keyword': (198, 120, 221),
        'func': (97, 175, 239),
        'class_name': (229, 192, 123),
        'string': (152, 195, 121),
        'comment': (92, 99, 112),
        'default': (171, 178, 191),
    }

    y = 55
    for item in code_lines:
        if len(item) == 2:
            kind, text = item
            kind = kind.strip()
            if kind == '' and text == '':
                y += 22
                continue
            color = COLORS.get(kind, COLORS['default'])
            draw.text((30, y), text, fill=color, font=font_sm)
            y += 22
        if y > H - 20:
            break

    img.save(OUTPUT_DIR / "gig_image_2_code.png")
    print(f"Saved {OUTPUT_DIR / 'gig_image_2_code.png'}")


# === IMAGE 3: Terminal / Pipeline ===
def make_terminal_image():
    img = Image.new("RGB", (W, H), (10, 10, 15))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, W, 40], fill=(30, 30, 40))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([15 + i * 25, 12, 31 + i * 25, 28], fill=color)
    draw.text((110, 10), "Terminal — scraper_demo.py", fill=GRAY, font=font_sm)

    GREEN = (74, 222, 128)
    YELLOW = (250, 204, 21)
    CYAN = (56, 189, 248)

    lines = [
        (WHITE, "$ python scraper_demo.py"),
        (None, ""),
        (GREEN, "[INFO] Parsed 4 records from page1.html"),
        (GREEN, "[INFO] Parsed 4 records from page2.html"),
        (GREEN, "[INFO] Parsed 4 records from page3.html"),
        (CYAN,  "[INFO] Total raw records: 12"),
        (YELLOW,"[INFO] Removed 2 duplicates"),
        (GREEN, "[INFO] Saved 10 unique rows to output/clean_product_listings.csv"),
        (None, ""),
        (WHITE, "$ python scraper_demo.py --simulate-scale 6000"),
        (None, ""),
        (GREEN, "[INFO] Parsed 4 records from page1.html"),
        (GREEN, "[INFO] Parsed 4 records from page2.html"),
        (GREEN, "[INFO] Parsed 4 records from page3.html"),
        (CYAN,  "[INFO] Expanded to 72,000 raw rows (scale factor: 6000)"),
        (YELLOW,"[INFO] Deduplication complete: 60,000 unique rows"),
        (GREEN, "[INFO] Saved 60,000 rows to output/clean_product_listings.csv"),
        (None, ""),
        (GREEN, "✓ Pipeline complete — 0 errors"),
        (None, ""),
        (GRAY,  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"),
        (ACCENT,"  Web Scraping Pipeline  |  Python + BeautifulSoup"),
        (GRAY,  "  Pagination · Dedup · CSV Export · Error Handling"),
        (GRAY,  "  github.com/zhaozihangbehappy-gif/portfolio-demos"),
    ]

    y = 55
    for color, text in lines:
        if color is None:
            y += 22
            continue
        draw.text((30, y), text, fill=color, font=font_sm)
        y += 26

    img.save(OUTPUT_DIR / "gig_image_3_terminal.png")
    print(f"Saved {OUTPUT_DIR / 'gig_image_3_terminal.png'}")


make_data_image()
make_code_image()
make_terminal_image()
print("Done! Images in:", OUTPUT_DIR)
