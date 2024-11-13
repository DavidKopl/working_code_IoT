#pip install pymongo[srv]
from pymongo import MongoClient
import datetime

# Připojení k MongoDB Atlas
client = MongoClient("mongodb+srv://kopldavid22:123456Ab@cluster-aquaponics-data.9cwcv.mongodb.net/senzori")
db = client["senzori"]  # Název databáze
collection = db["testovaci_senzori"]  # Název kolekce

# Funkce pro vložení dat do MongoDB
def send_data_to_mongodb(data):
    try:
        document = {
            "data": data,
            "timestamp": datetime.datetime.now()
        }
        collection.insert_one(document)
        print("Data uspesne vlozena!")
    except Exception as e:
        print(f"Chyba pri vkladani dat: {e}")

# Příklad dat
example_data = {"teplota": 23.5, "vlhkost": 60}

# Odeslání dat do MongoDB
send_data_to_mongodb(example_data)
