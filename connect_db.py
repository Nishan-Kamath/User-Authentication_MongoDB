from pymongo import MongoClient

connection_string = "mongodb+srv://nishankamath:nishankamath@cluster0.jkgir.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(connection_string)

db = client.my_new_database
collection = db.users

sample_data = {
    "name": "Nishan Kamath",
    "role": "Developer",
    "skills": ["Python", "AI", "Machine Learning"]
}

#inserted_id = collection.insert_one(sample_data).inserted_id
#print(f"Document inserted with ID: {inserted_id}")

for document in db.users.find():
    print(document)

#collection.delete_many({})

print("Collections in the new database:", db.list_collection_names())