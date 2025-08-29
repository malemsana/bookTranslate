# File: translator.py

def translate_single_chunk(text_to_translate, target_language_name, target_language_code, model):
    """
    Translates a single chunk of text synchronously using the provided Gemini model.
    """
    if not model:
        print("    ❌ ERROR: Gemini model not provided to the translation function.")
        return f"[TRANSLATION FAILED: MODEL NOT FOUND - {text_to_translate[:50]}]"

    prompt = (
        f"You are an expert literary translator. Your task is to translate the following segment of a book into {target_language_name} ({target_language_code}).\n"
        f"Preserve the original meaning, tone, style, and any structural elements like chapter headings (lines starting with '##') or paragraph breaks.\n"
        f"Translate naturally and fluently. Output only the translated text for the segment below, without any extra commentary.\n\n"
        f"--- Text Segment to Translate ---\n"
        f"{text_to_translate}\n"
        f"--- End of Text Segment ---\n\n"
        f"Translated segment in {target_language_name}:"
    )

    try:
        response = model.generate_content(prompt)
        # Check for safety ratings and blockages
        if response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason
            print(f"        ⚠️ Blocked by API: {reason}")
            return f"[CHUNK BLOCKED: {reason} - {text_to_translate[:50]}]"

        translated_text = response.text.strip()
        if not translated_text:
             print(f"        ⚠️ Empty translation from API.")
             return f"[CHUNK FAILED: EMPTY RESPONSE - {text_to_translate[:50]}]"
        
        return translated_text

    except Exception as e:
        print(f"    ❌ EXCEPTION during translation: {type(e).__name__} - {e}")
        return f"[CHUNK FAILED: EXCEPTION {type(e).__name__} - {text_to_translate[:50]}]"