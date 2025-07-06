import pymongo
import time
from dotenv import load_dotenv
import os
from keyword_detection import detect_drug_keywords

load_dotenv()

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
                    img = full_document["img"]
                    sender = full_document["sender"]
                    
                    if not img:
                        
                        MlData = detect_drug_keywords(txt)
                        
                        if MlData["isFlagged"]:
                            is_flagged_user = flagged_collection.find_one({"_id": sender})
                            if is_flagged_user:
                                flagged_collection.find_one_and_update({"_id": sender},{"$set":{"tag":"Red"},
                                   "$push": {"suspicious_words": {"$each": [*MlData["suspicious_words"]]}},
                                    "$inc": {"suspicious_word_count": MlData["suspicious_word_count"]}
                                },upsert=True)
                            else:
                                new_flagged_user = flagged_collection.insert_one({
                                     "user_id": sender,
                                     "isFlagged":"Red",
                                     "suspicious_word_count": MlData["suspicious_word_count"],
                                     "suspicious_words": MlData["suspicious_words"],
                                     "classses": [],

                                 })
                            convo = conversation_collection.find_one({"_id": full_document["conversationId"]})
                            interaction_status = interaction_collection.insert_one({
                                 "conversation id":  full_document["conversationId"],
                                 "members": convo["participants"]

                             })   
                       
                                                 
                        

        except pymongo.errors.PyMongoError as e:
            print(f"Error: {e}")
            if e.code == 40586:  # Invalid resume token
                resume_token = None
            time.sleep(1)  # Wait for 1 second before retrying


def chat_analysis():
    client = pymongo.MongoClient(os.getenv("MONGO_URI"))  # Replace with your connection string
    db = client["test"]
    collection = db["messages"]
    conversation_collection = db["conversations"]
    user_collection = db["users"]
    flagged_collection = db["flaggedusers"]
    interaction_collection =db["interactions"]

    monitor_changes(collection)

__all__ = ["chat_analysis"]