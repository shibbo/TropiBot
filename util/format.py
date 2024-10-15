import re

def clean_html(raw_text):
    """Remove HTML-like tags such as <br /> from the text."""
    clean_text = re.sub(r'<.*?>', '', raw_text)
    clean_text = clean_text.replace('&nbsp;', ' ')
    return clean_text