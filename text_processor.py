# File: text_processor.py

import re

def split_by_sentences(text_block):
    """Splits a block of text into sentences."""
    sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z"\'])|(?<=[.?!])\n+', text_block)
    return [s.strip() for s in sentences if s and s.strip()]

def chunk_text_sensibly(full_text, max_chars_per_chunk):
    """
    Definitive version: Tries to accumulate paragraphs to fill chunks close to max_chars_per_chunk.
    Handles chapters, oversized paragraphs, and oversized sentences gracefully.
    """
    print(f"  Chunking text... Max chars per chunk: {max_chars_per_chunk}")
    # The full chunk_text_sensibly function from the notebook goes here
    # (Pasted from your provided code for completeness)
    if not full_text or not full_text.strip():
        return []
    final_chunks = []
    chapter_split_regex = r'(\n## .*?\n)'
    # Use re.split to keep the chapter markers as separate elements
    segments = re.split(chapter_split_regex, full_text)

    # Process segments
    for i in range(len(segments)):
        segment_text = segments[i]
        if not segment_text.strip():
            continue

        # If the segment is a chapter marker
        if re.match(chapter_split_regex, segment_text):
            final_chunks.append(segment_text.strip())
            continue
        
        # If it's a content segment
        paragraphs = segment_text.strip().split('\n\n')
        current_chunk_buffer = ""
        for paragraph in paragraphs:
            para = paragraph.strip()
            if not para:
                continue

            if len(para) > max_chars_per_chunk:
                # Flush buffer before handling the oversized paragraph
                if current_chunk_buffer:
                    final_chunks.append(current_chunk_buffer)
                    current_chunk_buffer = ""
                # Split oversized paragraph by sentence
                sentences = split_by_sentences(para)
                current_sentence_buffer = ""
                for sentence in sentences:
                    if len(current_sentence_buffer) + len(sentence) + 1 <= max_chars_per_chunk:
                        current_sentence_buffer += sentence + " "
                    else:
                        if current_sentence_buffer: final_chunks.append(current_sentence_buffer.strip())
                        # Handle case where a single sentence is too long
                        if len(sentence) > max_chars_per_chunk:
                            for j in range(0, len(sentence), max_chars_per_chunk):
                                final_chunks.append(sentence[j:j+max_chars_per_chunk])
                            current_sentence_buffer = ""
                        else:
                            current_sentence_buffer = sentence + " "
                if current_sentence_buffer: final_chunks.append(current_sentence_buffer.strip())
            elif len(current_chunk_buffer) + len(para) + 2 <= max_chars_per_chunk:
                if current_chunk_buffer: current_chunk_buffer += "\n\n"
                current_chunk_buffer += para
            else:
                final_chunks.append(current_chunk_buffer)
                current_chunk_buffer = para
        if current_chunk_buffer: final_chunks.append(current_chunk_buffer)
    
    final_chunks = [chunk for chunk in final_chunks if chunk] # Cleanup empty chunks
    print(f"    Text divided into {len(final_chunks)} final small chunk(s).")
    return final_chunks