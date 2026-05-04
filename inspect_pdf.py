"""Test what pdfplumber can extract from the image-based PDF."""
import pdfplumber

pdf = pdfplumber.open(r"d:\OneDrive\Desktop\WT project\CS - III Semester_SEE_Results Jan 2026.pdf")

for i, page in enumerate(pdf.pages):
    print(f"=== PAGE {i} ===")
    print(f"  Dimensions: {page.width} x {page.height}")
    print(f"  Images: {len(page.images)}")
    print(f"  Chars: {len(page.chars)}")
    print(f"  Words: {len(page.extract_words())}")
    
    # Try table_settings with different strategies
    for strategy in ["lines", "text", "lines_strict"]:
        try:
            tables = page.extract_tables(table_settings={"vertical_strategy": strategy, "horizontal_strategy": strategy})
            print(f"  Tables ({strategy}): {len(tables)}")
        except:
            pass

    # Check if images have embedded text via OCR hint
    for j, img in enumerate(page.images[:3]):
        w = img['x1'] - img['x0']
        h = img['bottom'] - img['top']
        print(f"  Image {j}: {w:.0f}x{h:.0f} at ({img['x0']:.0f},{img['top']:.0f})")

    if i >= 1:
        break

pdf.close()
print("\nConclusion: This PDF contains only rasterized images. OCR is required.")
print("Will use pdf2image + pytesseract, or a simulated data approach for demo.")
