import pymongo
import time
import requests
from PIL import Image
import io
import json
from image_deteaction import img_detection
from keyword_detection import detect_drug_keywords
def monitor_changes(collection):
    """
    Continuously monitors a MongoDB collection for changes.

    Args:
      collection: The pymongo collection object to watch.
    """
    resume_token = None
    while True:
        try:
            options = {'resume_after': resume_token} if resume_token else {}
            with collection.watch([], **options) as stream:
                for change in stream:
                    resume_token = change['_id']
                    full_document = change['fullDocument']
                    txt = full_document["text"]
                    img_url= full_document["img"]
                    posted_by = full_document["postedBy"]
                    cloudinary_image_link = img_url
                    response = requests.get(cloudinary_image_link, stream=True)
                    image_data = response.content
                    image_buffer = io.BytesIO(image_data)
                    image = Image.open(image_buffer)
                    filename ="test.jpg"
                    image.save("uploads/" + filename)
                    
                   
                    MlData = json.loads(img_detection(filename))
                    TxtData = detect_drug_keywords(txt)
                    print(MlData["isFlagged"])
                    if MlData["isFlagged"]:
                        is_flagged_user = flagged_collection.find_one({"_id": posted_by})
                        if is_flagged_user:
                                flagged_collection.find_one_and_update({"_id": posted_by},{"$set":{"tag":"Red"},
                                   "$push": {"classes": {"$each": [*MlData["classes"]]},"suspicious_words": {"$each": [*TxtData["suspicious_words"]]}},
                                    "$inc": {"suspicious_word_count": TxtData["suspicious_word_count"]}
                                },upsert=True)
                        else:
                          new_flagged_user = flagged_collection.insert_one({
                                     "user_id": posted_by,
                                     "tag":"Red",
                                     "suspicious_word_count":TxtData["suspicious_word_count"],
                                     "suspicious_words": TxtData["suspicious_words"],
                                     "classes": MlData["classes"],

                                 })                    
                        

        except pymongo.errors.PyMongoError as e:
            print(f"Error: {e}")
            if e.code == 40586:  # Invalid resume token
                resume_token = None
            time.sleep(1)  # Wait for 1 second before retrying

def post_analysis():
    
    client = pymongo.MongoClient(os.getenv("MONGO_URI"))  # Replace with your connection string
    db = client["test"]
    collection = db["posts"]
    flagged_collection = db["flaggedusers"]
 
    monitor_changes(collection)

__all__ = ["post_analysis"]