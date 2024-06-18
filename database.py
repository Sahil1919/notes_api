
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.notes_db



notes_collection = db.notes
if "title_1_content_1_text" not in notes_collection.index_information():
    notes_collection.create_index([("title", "text"), ("content", "text")])