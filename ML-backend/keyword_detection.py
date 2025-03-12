import re
from Drug_keywords import drug_keywords

def detect_drug_keywords(text):
  """
  Detects the presence of exact keywords in a text using regex.

  Args:
    text: The text to analyze.
    keywords: A list of keywords to search for (as raw strings with regex patterns).

  Returns:
    A list of found keywords.
  """
  keywords = drug_keywords
  found_keywords = []
  

  for keyword_pattern in keywords:
    # Use re.search with word boundary anchors to match exact words
    if re.search(keyword_pattern, text, flags=re.IGNORECASE):
      # Extract the keyword from the pattern (without the regex \b)
      keyword = keyword_pattern.replace(r"\b", "") 
      if keyword not in found_keywords:
        found_keywords.append(keyword)
        
  isFlagged = True if len(found_keywords) != 0 else False
  res={
    "isFlagged": isFlagged,
    "suspicious_words": found_keywords,
    "suspicious_word_count": len(found_keywords)
  }
  return res

__all__ = ["detect_drug_keywords"]

# Example usage
sample_text = "have bm1 and ibo last had snow and blow"
result = detect_drug_keywords(sample_text)
print(result)  

