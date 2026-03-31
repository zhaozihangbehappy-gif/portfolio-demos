"""Generate Fiverr gig gallery images for Excel/Data Automation gig."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "gig_images"
OUTPUT_DIR.mkdir(exist_ok=True)

W, H = 1200, 720
BG = (15, 23, 42)
ACCENT = (56, 189, 248)
WHITE = (255, 255, 255)
GRAY = (148, 163, 184)
ROW_ALT = (22, 33, 55)
HEADER_BG = (30, 58, 95)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
YELLOW = (250, 204, 21)

try:
    font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
    font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 28)
    font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 36)
except:
    font_sm = font_md = font_lg = font_xl = ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)


# === IMAGE 1: Before / After comparison ===
def make_before_after():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((40, 25), "Data Automation — Before & After", fill=ACCENT, font=font_xl)

    # BEFORE side
    draw.text((40, 80), "BEFORE (Raw Data)", fill=RED, font=font_lg)
    draw_rounded_rect(draw, (30, 115, 580, 430), 8, (25, 15, 15))

    before_headers = ["Date", "Team", "Status", "Revenue"]
    before_data = [
        ["03/15/2026", "  marketing", "done", "1200"],
        ["2026-03-15", "Marketing ", "DONE", "1,200"],
        ["15-Mar-26", "MARKETING", "complete", "$1200"],
        ["", "sales", "in progress", "800"],
        ["03/16/2026", "Sales", "inprogress", "800.00"],
        ["2026/03/17", " engineering", "blocked", ""],
        ["03-17-2026", "Engineering", "BLOCKED", "n/a"],
        ["03/18/2026", "marketing", "Done ", "950"],
    ]

    bx = [45, 190, 370, 490]
    y = 125
    for i, h in enumerate(before_headers):
        draw.text((bx[i], y), h, fill=YELLOW, font=font_sm)
    y += 28
    draw.line([(40, y), (570, y)], fill=(60, 30, 30), width=1)
    y += 5
    for row in before_data:
        for i, cell in enumerate(row):
            color = RED if cell in ["", "n/a"] else (200, 150, 150)
            draw.text((bx[i], y), cell, fill=color, font=font_sm)
        y += 28

    # Arrow
    draw.text((590, 260), ">>>", fill=ACCENT, font=font_lg)

    # AFTER side
    draw.text((650, 80), "AFTER (Cleaned)", fill=GREEN, font=font_lg)
    draw_rounded_rect(draw, (640, 115, W - 30, 430), 8, (15, 25, 15))

    after_headers = ["Date", "Team", "Status", "Revenue"]
    after_data = [
        ["2026-03-15", "Marketing", "Completed", "$1,200"],
        ["2026-03-16", "Sales", "In Progress", "$800"],
        ["2026-03-17", "Engineering", "Blocked", "$0"],
        ["2026-03-18", "Marketing", "Completed", "$950"],
    ]

    ax = [655, 800, 930, 1060]
    y = 125
    for i, h in enumerate(after_headers):
        draw.text((ax[i], y), h, fill=YELLOW, font=font_sm)
    y += 28
    draw.line([(650, y), (W - 40, y)], fill=(30, 60, 30), width=1)
    y += 5
    for row in after_data:
        for i, cell in enumerate(row):
            draw.text((ax[i], y), cell, fill=GREEN, font=font_sm)
        y += 28

    # Stats
    y = 460
    draw_rounded_rect(draw, (30, y, W - 30, y + 100), 8, (20, 30, 50))
    stats = [
        ("8 rows", "Raw Input"),
        ("4 rows", "After Dedup"),
        ("3 issues", "Auto-fixed"),
        ("1 click", "To Run"),
    ]
    sx = 80
    for val, label in stats:
        draw.text((sx, y + 15), val, fill=ACCENT, font=font_lg)
        draw.text((sx, y + 50), label, fill=GRAY, font=font_sm)
        sx += 280

    # Footer
    draw.text((40, H - 50), "Automated with Python + Pandas", fill=GRAY, font=font_sm)

    img.save(OUTPUT_DIR / "gig2_image_1_before_after.png")
    print(f"Saved gig2_image_1_before_after.png")


# === IMAGE 2: Excel Report Output ===
def make_report_image():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((40, 25), "Automated Weekly Report — Excel Output", fill=ACCENT, font=font_xl)
    draw.text((40, 70), "4 sheets generated in one click", fill=GRAY, font=font_md)

    # Sheet tabs
    tabs = ["Raw_Data", "Cleaned_Data", "Weekly_Summary", "Team_Summary"]
    tx = 40
    for i, tab in enumerate(tabs):
        bg = ACCENT if i == 3 else (40, 50, 70)
        text_col = BG if i == 3 else GRAY
        tw = len(tab) * 12 + 20
        draw_rounded_rect(draw, (tx, 110, tx + tw, 140), 5, bg)
        draw.text((tx + 10, 115), tab, fill=text_col, font=font_sm)
        tx += tw + 8

    # Team Summary table
    draw_rounded_rect(draw, (30, 155, W - 30, 480), 8, (18, 22, 35))

    headers = ["Team", "Tasks", "Completed", "Hours Saved", "Revenue Impact"]
    col_x = [50, 250, 400, 560, 780]
    y = 170
    draw_rounded_rect(draw, (35, y - 5, W - 35, y + 28), 5, HEADER_BG)
    for i, h in enumerate(headers):
        draw.text((col_x[i], y), h, fill=ACCENT, font=font_md)

    data = [
        ["Marketing", "12", "10", "18.5 hrs", "$4,200"],
        ["Sales", "8", "6", "12.0 hrs", "$3,800"],
        ["Engineering", "15", "13", "24.5 hrs", "$6,100"],
        ["Operations", "6", "5", "8.0 hrs", "$1,900"],
        ["Finance", "4", "4", "6.5 hrs", "$2,400"],
        ["Support", "9", "7", "10.0 hrs", "$1,500"],
    ]

    y = 210
    for idx, row in enumerate(data):
        if idx % 2 == 0:
            draw.rectangle([35, y - 2, W - 35, y + 26], fill=ROW_ALT)
        for i, cell in enumerate(row):
            color = GREEN if i == 4 else WHITE
            draw.text((col_x[i], y), cell, fill=color, font=font_sm)
        y += 32

    # Summary cards
    y = 510
    cards = [
        ("54", "Total Tasks", ACCENT),
        ("45", "Completed", GREEN),
        ("79.5 hrs", "Time Saved", YELLOW),
        ("$19,900", "Revenue Impact", GREEN),
    ]
    cx = 50
    for val, label, color in cards:
        draw_rounded_rect(draw, (cx, y, cx + 250, y + 120), 10, (20, 30, 50))
        draw.text((cx + 20, y + 15), val, fill=color, font=font_xl)
        draw.text((cx + 20, y + 65), label, fill=GRAY, font=font_md)
        cx += 275

    draw.text((40, H - 45), "Generated with Python — one command, zero manual work", fill=GRAY, font=font_sm)

    img.save(OUTPUT_DIR / "gig2_image_2_report.png")
    print(f"Saved gig2_image_2_report.png")


# === IMAGE 3: Workflow diagram ===
def make_workflow_image():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((40, 25), "How It Works — Automation Workflow", fill=ACCENT, font=font_xl)

    steps = [
        ("1", "INPUT", "Your messy CSV,\nExcel, or API data", (56, 189, 248)),
        ("2", "CLEAN", "Dedup, fix dates,\nstandardize values", (250, 204, 21)),
        ("3", "TRANSFORM", "Merge, aggregate,\nbuild summaries", (168, 85, 247)),
        ("4", "OUTPUT", "Clean Excel, CSV,\nor Google Sheets", (74, 222, 128)),
    ]

    bx = 50
    for num, title, desc, color in steps:
        draw_rounded_rect(draw, (bx, 100, bx + 245, 320), 12, (20, 28, 45))

        # Number circle
        draw.ellipse([bx + 95, 115, bx + 145, 165], fill=color)
        draw.text((bx + 112, 122), num, fill=BG, font=font_lg)

        draw.text((bx + 30, 180), title, fill=color, font=font_lg)

        lines = desc.split("\n")
        dy = 220
        for line in lines:
            draw.text((bx + 30, dy), line, fill=GRAY, font=font_md)
            dy += 25

        # Arrow between boxes
        if num != "4":
            ax = bx + 255
            draw.text((ax, 190), "->", fill=ACCENT, font=font_lg)

        bx += 280

    # Bottom features
    y = 380
    draw_rounded_rect(draw, (30, y, W - 30, y + 250), 10, (18, 22, 35))

    features = [
        ("Fast Delivery", "Most projects done\nwithin 24-48 hours", ACCENT),
        ("Clean Code", "Documented, reusable\nPython scripts", GREEN),
        ("One-Click Run", "Run the script once,\nuse it forever", YELLOW),
        ("Any Format", "CSV, Excel, Google\nSheets, JSON, DB", (168, 85, 247)),
    ]

    fx = 60
    for title, desc, color in features:
        draw.text((fx, y + 25), title, fill=color, font=font_lg)
        lines = desc.split("\n")
        dy = y + 65
        for line in lines:
            draw.text((fx, dy), line, fill=GRAY, font=font_sm)
            dy += 22
        fx += 280

    # Tech stack bar
    y2 = 550
    draw.text((60, y2), "Python  |  Pandas  |  Excel  |  Google Sheets API  |  SQLite", fill=GRAY, font=font_md)

    draw.text((40, H - 45), "github.com/zhaozihangbehappy-gif/portfolio-demos", fill=GRAY, font=font_sm)

    img.save(OUTPUT_DIR / "gig2_image_3_workflow.png")
    print(f"Saved gig2_image_3_workflow.png")


make_before_after()
make_report_image()
make_workflow_image()
print("Done! Images in:", OUTPUT_DIR)
