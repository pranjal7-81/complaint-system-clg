import re

def clean_text(text: str) -> str:
    """
    Clean and normalize complaint narrative text for TF-IDF vectorization.
    
    Steps:
    1. Handle missing/non-string input cleanly.
    2. Convert text to lowercase.
    3. Remove CFPB redaction patterns (e.g., XXXX, XX/XX/XXXX).
    4. Remove noise characters while retaining words and numbers.
    5. Normalize extra whitespace and line breaks.
    """
    if not isinstance(text, str) or not text:
        return ""
    
    # Step 1: Lowercase
    text = text.lower()
    
    # Step 2: Remove CFPB anonymization redaction tokens (e.g. 'xxxx', 'xx/xx/xxxx')
    text = re.sub(r'\b(x{2,}|xx/xx/x{2,}|xx/xx/\d{2,4})\b', ' ', text)
    
    # Step 3: Remove non-alphanumeric characters except basic whitespace
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Step 4: Replace multiple spaces and newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def tokenize(text: str) -> list[str]:
    """
    Simple whitespace tokenizer returning non-empty tokens.
    """
    cleaned = clean_text(text)
    return [token for token in cleaned.split(' ') if token]
