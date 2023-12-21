from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
import random
from faker import Faker
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password, make_password

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

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
            db = client['user']
            log_and_auth = db['logAndAuth']

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            hashed_password = make_password(password)

            user_data = {
                'username': username,
                'password': hashed_password,
            }

            log_and_auth.insert_one(user_data)

            return redirect('myfirstapp:home')
    else:
        form = SignUpForm()
    template = loader.get_template('signup.html')
    return HttpResponse(template.render({'form': form}, request))

# myfirstapp/views.py
def staff_profile(request):
    user_data = request.session.get('user')

    if user_data and 'staff' in user_data:
        return render(request, 'staff_profile.html', {'user_data': user_data})
    else:
        return redirect('login')
    
def patient_profile(request):
    user_data = request.session.get('user')

    if user_data and 'patient' in user_data:
        return render(request, 'patient_profile.html', {'user_data': user_data})
    else:
        return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
            db = client['user']
            users = db['logAndAuth']

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user_data = users.find({'username': username})

            for user in user_data:
                stored_password = user['password']
                if check_password(password, stored_password):
                    request.session['user'] = user
                    if 'user' in user:
                        return redirect('myfirstapp:patient_profile')
                    elif 'staff' in user:
                        return redirect('myfirstapp:staff_profile')
                    else:
                        return redirect('myfirstapp:home')
            
            # If no matching username and password found
            return redirect('myfirstapp:home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# The check_password function in Django uses the PBKDF2 algorithm with a SHA-256 hash. 
# It is the default password hashing algorithm used by Django for user authentication.