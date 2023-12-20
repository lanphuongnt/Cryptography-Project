from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
import random
from faker import Faker

def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host=host,
                         port=int(port),
                         username=username,
                         password=password
                        )
    db_handle = client[db_name]
    return db_handle, client

def test_create_record(db_handle):
    test_data = {"name": "Test", "email": "test@example.com"}
    result = db_handle.myCollection.insert_one(test_data)
    return result.inserted_id

def transfer_records(src_db_handle, dest_db_handle):
    # Get all documents from the source collection
    src_documents = src_db_handle.stomach.find()

    # Initialize a Faker instance
    fake = Faker()

    # Iterate over the documents
    for doc in src_documents:
        # Generate random data
        doc['name'] = fake.name()
        doc['email'] = fake.email()
        doc['age'] = random.randint(20, 60)

        # Insert each document into the destination collection
        dest_db_handle.ehr.insert_one(doc)

def home(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())
def template(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())