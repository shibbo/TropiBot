import re
import time

def clean_html(raw_text):
    """Remove HTML-like tags such as <br /> from the text."""
    clean_text = re.sub(r'<.*?>', '', raw_text)
    clean_text = clean_text.replace('&nbsp;', ' ')
    return clean_text

def extract_png(raw_text):
    urls = re.findall(r'https?://[^\s]+\.png', raw_text)
    return [f"{url}?t={int(time.time())}" for url in urls]