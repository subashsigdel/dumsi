from indic_transliteration import sanscript
import re

def preprocess_text(text):
    if not re.match(r'[\u0900-\u097F]', text):
        text = sanscript.transliterate(text, sanscript.OPTITRANS, sanscript.DEVANAGARI)
    text = re.sub(r'\s+', ' ', text.strip())
    return text