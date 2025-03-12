from keyword_detection import *
from image_deteaction import *
import json
def isDrug(img_name, text):
    res1 = json.loads(img_detection(img_name))
    res2 = detect_drug_keywords(text)
    flag = res1["isFlagged"] or res2["isFlagged"]
    print(type(res1),type(res2) )
    res={
        "isFlagged": flag,
        "tag": res1["tag"],
        "classes": res1["classes"],
        "suspicious_words": res2["found_keyword"],
        "suspicious_word_count": res2["suspicious_word_count"]
    }
    return res
   
