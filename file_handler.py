# File: file_handler.py

import ebooklib
from ebooklib import epub
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import re
import os
import time

# --- Extraction Functions ---

def extract_text_from_epub(epub_filepath):
    """Extracts textual content from an EPUB file, marking headings."""
    print(f"  Extracting text from EPUB: {os.path.basename(epub_filepath)}")
    try:
        book = epub.read_epub(epub_filepath)
        full_text_parts = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content_bytes = item.get_content()
            try:
                content_str = content_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                content_str = content_bytes.decode('latin-1', errors='replace')

            soup = BeautifulSoup(content_str, 'html.parser')
            # Use a more targeted approach for text
            text_in_item = []
            for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
                if element.name.startswith('h'):
                    text_in_item.append(f"\n\n## {element.get_text(strip=True)}\n\n")
                else:
                    text_in_item.append(element.get_text(strip=True))
            full_text_parts.append("\n\n".join(text_in_item))

        extracted_text = "\n\n".join(full_text_parts)
        # Consolidate excessive newlines
        extracted_text = re.sub(r'(\n\s*){3,}', '\n\n', extracted_text).strip()
        print(f"    EPUB extraction complete. Characters: {len(extracted_text)}")
        return extracted_text
    except Exception as e:
        print(f"    ❌ ERROR parsing EPUB {os.path.basename(epub_filepath)}: {e}")
        return None

def extract_text_from_pdf(pdf_filepath):
    """Extracts textual content from a PDF file."""
    print(f"  Extracting text from PDF: {os.path.basename(pdf_filepath)}")
    try:
        doc = fitz.open(pdf_filepath)
        full_text_parts = [page.get_text("text") for page in doc]
        extracted_text = "".join(full_text_parts)
        extracted_text = re.sub(r'(\n\s*){2,}', '\n\n', extracted_text).strip()
        print(f"    PDF extraction complete. Characters: {len(extracted_text)}")
        return extracted_text
    except Exception as e:
        print(f"    ❌ ERROR parsing PDF {os.path.basename(pdf_filepath)}: {e}")
        return None

def get_book_text(book_filepath):
    """Detects file type and calls the appropriate extraction function."""
    if not os.path.exists(book_filepath):
        print(f"❌ ERROR: File does not exist at path: {book_filepath}")
        return None

    _, file_extension = os.path.splitext(book_filepath.lower())
    if file_extension == '.epub':
        return extract_text_from_epub(book_filepath)
    elif file_extension == '.pdf':
        return extract_text_from_pdf(book_filepath)
    else:
        print(f"❌ ERROR: Unsupported file type: '{file_extension}'. Please use .epub or .pdf.")
        return None

# --- Reconstruction Functions ---

def save_text_file(text, output_filepath):
    """Saves the translated text as a simple TXT file."""
    print(f"  Reconstructing basic TXT: {os.path.basename(output_filepath)}")
    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"    TXT reconstruction complete: {os.path.basename(output_filepath)}")
        return True
    except Exception as e:
        print(f"    ERROR saving TXT file: {e}")
        return False

def reconstruct_epub_basic(translated_text, lang_code, book_title, author_name, output_filepath):
    """Creates a basic EPUB from translated text, splitting by '##' headings."""
    print(f"  Reconstructing basic EPUB: {os.path.basename(output_filepath)}")
    # Your full reconstruct_epub_basic function from the notebook goes here
    # (Pasted from your provided code for completeness)
    book = epub.EpubBook()
    book.set_identifier(f"urn:uuid:{book_title.replace(' ', '_')}-{time.time()}")
    book.set_title(book_title)
    book.set_language(lang_code)
    book.add_author(author_name)
    raw_segments = re.split(r'(\n## .*?\n)', translated_text, flags=re.DOTALL)
    epub_chapters_list = []
    current_chapter_title_str = "Introduction"
    current_chapter_content_html_str = ""
    def sanitize_filename(name):
        name = re.sub(r'[^\w\s-]', '', name.lower())
        return re.sub(r'[-\s]+', '-', name).strip('-_')
    processed_first_segment = False
    if raw_segments and raw_segments[0].strip() and not raw_segments[0].startswith("\n## "):
        content_html = "".join([f"<p>{p.strip()}</p>" for p in raw_segments[0].strip().split('\n') if p.strip()])
        current_chapter_content_html_str += content_html
        processed_first_segment = True
    start_idx = 1 if processed_first_segment else 0
    for i in range(start_idx, len(raw_segments)):
        segment = raw_segments[i]
        if segment.startswith("\n## "):
            if current_chapter_content_html_str.strip():
                safe_title_for_file = sanitize_filename(current_chapter_title_str)
                chap_file_name = f'chap_{len(epub_chapters_list)+1:02d}_{safe_title_for_file[:20]}.xhtml'
                ch_obj = epub.EpubHtml(title=current_chapter_title_str, file_name=chap_file_name, lang=lang_code)
                ch_obj.content = f'<h1>{current_chapter_title_str}</h1>{current_chapter_content_html_str}'
                epub_chapters_list.append(ch_obj); book.add_item(ch_obj)
            current_chapter_title_str = segment.replace("\n## ", "").strip().split('\n')[0]
            current_chapter_content_html_str = "".join([f"<p>{p.strip()}</p>" for p in segment.replace("\n## " + current_chapter_title_str, "").strip().split('\n') if p.strip()])
        else:
            current_chapter_content_html_str += "".join([f"<p>{p.strip()}</p>" for p in segment.strip().split('\n') if p.strip()])
    if current_chapter_content_html_str.strip() or not epub_chapters_list:
        if not current_chapter_content_html_str.strip() and not epub_chapters_list and translated_text.strip():
             current_chapter_title_str = book_title
             current_chapter_content_html_str = "".join([f"<p>{p.strip()}</p>" for p in translated_text.strip().split('\n') if p.strip()])
        safe_title_for_file = sanitize_filename(current_chapter_title_str)
        chap_file_name = f'chap_{len(epub_chapters_list)+1:02d}_{safe_title_for_file[:20]}.xhtml'
        ch_obj = epub.EpubHtml(title=current_chapter_title_str, file_name=chap_file_name, lang=lang_code)
        ch_obj.content = f'<h1>{current_chapter_title_str}</h1>{current_chapter_content_html_str}'
        epub_chapters_list.append(ch_obj); book.add_item(ch_obj)
    
    book.toc = tuple(epub_chapters_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + epub_chapters_list
    
    try: 
        epub.write_epub(output_filepath, book, {})
        print(f"    EPUB reconstruction complete: {os.path.basename(output_filepath)}")
        return True
    except Exception as e: 
        print(f"    ERROR writing EPUB file: {e}")
        return False


def reconstruct_pdf_basic(translated_text, output_filepath):
    """Creates a basic PDF from the translated text."""
    print(f"  Reconstructing basic PDF: {os.path.basename(output_filepath)}")
    # Your full reconstruct_pdf_basic function from the notebook goes here
    # (Pasted from your provided code for completeness)
    doc = None
    try:
        doc = fitz.open()
        page_width, page_height = fitz.paper_size("a4")
        margin = 50
        text_area_rect = fitz.Rect(margin, margin, page_width - margin, page_height - margin)
        font_regular = "helvetica"; font_bold = "helvetica-bold"
        regular_fontsize = 11; heading_fontsize = 15
        line_spacing_factor = 1.4
        current_y = text_area_rect.y0
        page = None
        def add_new_page_pdf():
            nonlocal page, current_y
            page = doc.new_page(width=page_width, height=page_height)
            current_y = text_area_rect.y0
            return page
        page = add_new_page_pdf()
        paragraphs = translated_text.split('\n\n')
        for para_text in paragraphs:
            para_text = para_text.strip()
            if not para_text: continue
            is_heading = para_text.startswith("## ")
            display_text = para_text[3:].strip() if is_heading else para_text
            fontsize = heading_fontsize if is_heading else regular_fontsize
            fontname = font_bold if is_heading else font_regular
            effective_line_height = fontsize * line_spacing_factor
            if is_heading and current_y > text_area_rect.y0 + effective_line_height: current_y += heading_fontsize * 0.5
            lines_in_para = display_text.split('\n')
            for single_line in lines_in_para:
                if current_y + effective_line_height > text_area_rect.y1: page = add_new_page_pdf()
                page.insert_text(fitz.Point(text_area_rect.x0, current_y + fontsize), single_line, fontname=fontname, fontsize=fontsize)
                current_y += effective_line_height
            current_y += effective_line_height * 0.2
        if doc.page_count > 0: 
            doc.save(output_filepath, garbage=3, deflate=True)
            print(f"    PDF reconstruction complete: {os.path.basename(output_filepath)}")
            return True
        else: 
            print("    ⚠️ PDF not saved as no content was added.")
            return False
    except Exception as e: 
        print(f"    ERROR saving PDF: {e}")
        return False
    finally:
        if doc: doc.close()