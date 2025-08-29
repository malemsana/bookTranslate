# File: main.py

import os
import time
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Import our custom modules
import file_handler
import text_processor
import translator

def main():
    """Main function to run the entire book translation workflow."""

    # --- 1. CONFIGURATION (Replaces the Colab Form) ---
    # Make sure to create a .env file with your GOOGLE_API_KEY
    load_dotenv()
    
    CONFIG = {
        "gemini_model_name": "gemini-1.5-flash", # Updated model
        "input_filename": "The Tale of Genji_Murasaki Shikibu.epub", # The file you place in 'source_books'
        "output_base_filename": "Genjifate_Hindi_Translation",
        "output_format": "EPUB",  # Options: TXT, EPUB, PDF
        "target_language_name": "Hindi",
        "target_language_code": "hi", # ISO 639-1 code
        "max_chars_per_chunk": 10000, # Recommended to keep this within model context limits
        "api_call_delay_seconds": 3,
        "author_name": "Translator AI" # For EPUB metadata
    }

    # --- 2. SETUP & INITIALIZATION ---
    start_time_total = time.time()

    # Configure the Gemini client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("🛑 FATAL ERROR: GOOGLE_API_KEY not found. Please create a .env file and add it.")
        return
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(CONFIG["gemini_model_name"])
    print(f"🤖 Gemini client configured with model: {CONFIG['gemini_model_name']}")

    # Prepare file paths
    input_filepath = os.path.join("source_books", CONFIG["input_filename"])
    output_extension = "." + CONFIG["output_format"].lower()
    output_filename = f"{CONFIG['output_base_filename']}{output_extension}"
    output_filepath = os.path.join("translated_books", output_filename)
    os.makedirs("source_books", exist_ok=True)
    os.makedirs("translated_books", exist_ok=True)
    
    print("\n--- Starting Book Translation Workflow ---")
    print(f"📖 Source: {CONFIG['input_filename']}")
    print(f"💾 Output: {output_filename}")
    print(f"🌐 Language: {CONFIG['target_language_name']} ({CONFIG['target_language_code']})")
    print("-------------------------------------------\n")


    # --- 3. WORKFLOW EXECUTION ---

    # Phase 1: Extract Text
    print("Phase 1/4: Extracting text from book...")
    extracted_text = file_handler.get_book_text(input_filepath)
    if not extracted_text:
        print("❌ ERROR: Failed to extract text. Workflow halted.")
        return
    print(f"✅ Text extracted successfully ({len(extracted_text):,} characters).\n")

    # Phase 2: Chunk Text
    print("Phase 2/4: Chunking text for translation...")
    translation_chunks = text_processor.chunk_text_sensibly(extracted_text, CONFIG["max_chars_per_chunk"])
    if not translation_chunks:
        print("❌ ERROR: No text chunks were created. Workflow halted.")
        return
    num_chunks = len(translation_chunks)
    print(f"✅ Text divided into {num_chunks} chunk(s).\n")
    
    # Phase 3: Translate Chunks
    print(f"Phase 3/4: Translating {num_chunks} chunk(s) sequentially...")
    all_translated_parts = []
    for i, chunk in enumerate(translation_chunks):
        print(f"  Translating chunk {i+1} of {num_chunks} ({len(chunk):,} chars)...")
        translated_part = translator.translate_single_chunk(
            chunk,
            CONFIG["target_language_name"],
            CONFIG["target_language_code"],
            model
        )
        all_translated_parts.append(translated_part)

        if translated_part.startswith("[CHUNK"): # Check for our error markers
             print(f"    ⚠️ WARNING: Chunk {i+1} failed/blocked. See message above.")
        else:
            print(f"    ✅ Chunk {i+1} translated successfully.")

        if i < num_chunks - 1 and CONFIG["api_call_delay_seconds"] > 0:
            time.sleep(CONFIG["api_call_delay_seconds"])
    print("✅ All chunks processed.\n")

    # Phase 4: Assemble and Save
    print("Phase 4/4: Assembling and saving final file...")
    final_translated_text = "\n\n".join(all_translated_parts)
    final_translated_text = re.sub(r'(\n\s*){3,}', '\n\n', final_translated_text)
    
    file_saved = False
    book_title = CONFIG['output_base_filename'].replace('_', ' ')
    if CONFIG["output_format"] == "TXT":
        file_saved = file_handler.save_text_file(final_translated_text, output_filepath)
    elif CONFIG["output_format"] == "EPUB":
        file_saved = file_handler.reconstruct_epub_basic(final_translated_text, CONFIG["target_language_code"], book_title, CONFIG["author_name"], output_filepath)
    elif CONFIG["output_format"] == "PDF":
        file_saved = file_handler.reconstruct_pdf_basic(final_translated_text, output_filepath)

    total_time = time.time() - start_time_total
    print("\n-------------------------------------------")
    if file_saved:
        print(f"🎉 SUCCESS! Translation complete.")
        print(f"   -> Final file saved to: {output_filepath}")
        print(f"   Total processing time: {total_time:.2f} seconds ({total_time/60:.2f} minutes).")
    else:
        print(f"❌ FAILED: The final file could not be saved.")
    print("-------------------------------------------\n")

if __name__ == "__main__":
    main()