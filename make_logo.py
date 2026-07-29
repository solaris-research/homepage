import fitz

ACCENT = (0.875, 0.306, 0.235)  # #df4e3c
DARK = (0.035, 0.145, 0.267)    # #092544
BG = (0.969, 0.969, 0.965)      # #f7f7f6
SIZE = 512
MARGIN = 80

def make_logo():
    doc = fitz.open()
    page = doc.new_page(width=SIZE, height=SIZE)

    # Background
    page.draw_rect(fitz.Rect(0, 0, SIZE, SIZE), color=None, fill=BG)

    # Draw "S" in dark color
    tw_s = fitz.TextWriter(page.rect)
    font = fitz.Font("helv")
    fs = 320
    # Position S on the left
    tw_s.append((55, 380), "S", font=font, fontsize=fs)
    page.write_text(writers=[tw_s], color=DARK)

    # Draw "/" in accent color
    tw_sl = fitz.TextWriter(page.rect)
    tw_sl.append((195, 380), "/", font=font, fontsize=fs)
    page.write_text(writers=[tw_sl], color=ACCENT)

    # Draw "R" in dark color
    tw_r = fitz.TextWriter(page.rect)
    tw_r.append((280, 380), "R", font=font, fontsize=fs)
    page.write_text(writers=[tw_r], color=DARK)

    # Save PDF
    doc.save("/Users/annahedstrom/Projects/solaris-research/sr_logo_2.pdf")

    # Save PNG
    pix = page.get_pixmap(dpi=300)
    pix.save("/Users/annahedstrom/Projects/solaris-research/sr_logo_2.png")

    doc.close()
    print("Created sr_logo_2.pdf and sr_logo_2.png")

make_logo()
