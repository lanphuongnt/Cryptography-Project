from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
import random
# from faker import Faker
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required

from .source.mypackages.CA import CentralizedAuthority
from django.contrib import messages
from django.contrib.auth import login
from bson import ObjectId
from django.views.decorators.cache import never_cache

import json

server_CA = CentralizedAuthority()
# server_CA.AddPolicy()


def create_new_EHR(request, userID):
    # '''
    # Example: request
    addition = {
                "patient_info": {
                    "name": request.POST.get('username'),
                    "dob": "",
                    "gender": "",
                    "cccd": "",
                    "contact": {
                        "phone": "",
                        "email": ""
                    },
                    "address": {
                        "street": "",
                        "city": "",
                        "state": "",
                        "zip": ""
                    }
                }
            } 
    # ''' 
    addition['_id'] = userID

    ehr_col = server_CA.client['data']['ehr']
    ehr_col.insert_one(addition)

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

@never_cache
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            db = server_CA.client['user']
            log_and_auth = db['logAndAuth']

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            status = form.cleaned_data.get('role')

            if status == 'patient':
                role = 'user'
            else:
                role = 'staff'

            hashed_password = make_password(password)

            user_data = {
                'password': hashed_password,
                'role': role,
                'status': status
            }

            result = log_and_auth.insert_one(user_data)

            # Get the ObjectId
            object_id = result.inserted_id

            # Update the document to set the username to the ObjectId
            log_and_auth.update_one({'_id': object_id}, {'$set': {'username': str(object_id)}})
            # Generate public key master key for new user
            server_CA.Setup(str(object_id))

            # Generate EHR document for new user
            create_new_EHR(request, str(object_id))

            return redirect('myfirstapp:home')
    else:
        form = SignUpForm()
    template = loader.get_template('signup.html')
    return HttpResponse(template.render({'form': form}, request))

def custom_login_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if 'user' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('myfirstapp:login')
    return _wrapped_view_func

@never_cache
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
            db = server_CA.client['user']
            collection = db['logAndAuth']

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = collection.find_one({'username': username})
            stored_password = user['password']
            if check_password(password, stored_password):
                # Convert ObjectId to string
                user['_id'] = str(user['_id'])
                request.session['user'] = user
                if user['role'] == 'user':
                    return redirect('myfirstapp:patient_profile')
                elif user['role'] == 'staff':
                    return redirect('myfirstapp:staff_profile')
                else:
                    return redirect('myfirstapp:home')
            
            # If no matching username and password found
            return redirect('myfirstapp:home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    request.session.pop('user', None)
    return redirect('myfirstapp:home')

# myfirstapp/views.py
@never_cache
@custom_login_required
def staff_profile(request):
    user = request.session['user']

    # Check if the user's role is 'staff'
    if user['role'] != 'staff':
        # If not, redirect them to their correct profile or home page
        if user['role'] == 'user':
            return redirect('myfirstapp:patient_profile')
        else:
            return redirect('myfirstapp:home')

    user_id = str(user['_id'])
    template = loader.get_template('staff_profile.html')
    return HttpResponse(template.render({'user_id': user_id}, request))

@never_cache
@custom_login_required
def patient_profile(request):
    user = request.session['user']

    # Check if the user's role is 'user'
    if user['role'] != 'user':
        # If not, redirect them to their correct profile or home page
        if user['role'] == 'staff':
            return redirect('myfirstapp:staff_profile')
        else:
            return redirect('myfirstapp:home')

    user_id = str(user['_id'])
    template = loader.get_template('patient_profile.html')
    return HttpResponse(template.render({'user_id': user_id}, request))
# The check_password function in Django uses the PBKDF2 algorithm with a SHA-256 hash. 
# It is the default password hashing algorithm used by Django for user authentication.

def insert_data(request):
    # Request (dict) include: database, collection, username(ObjectID), {'$set' : {'dataname1': datavalue1}, {data}}
    # Example : request = {'database' : 'data', 'collection' : 'ehr', 'username' : '65845045be5cf517d0a932e1', {'height' : 153}}
    db = server_CA.client[request['database']]
    collection = db[request['collection']]

    update_data = request['$set']

    CA_db = server_CA.client['CA']
    attribute_col = CA_db['subject_attribute']
    user_attribute = attribute_col.find_one({"_id" : ObjectId(request['username'])})    
    
    server_CA.GeneratePrivateKey()


    collection.update_many({'_id': ObjectId(request['username'])}, {'$set': request['$set']})
    response = collection.find_one({'_id': ObjectId(request['username'])})
    if response:
        return True
    else:
        return False
    


def GetSubjectAttribute(self, userID, attribute_name): # attribute name is a list string 
    # Load public key 
    attribute = {} 
    return attribute
    
