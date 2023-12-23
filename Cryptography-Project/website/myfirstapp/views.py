from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
from django.contrib.auth.hashers import check_password, make_password

from bson import ObjectId
from django.views.decorators.cache import never_cache
from .source.mypackages.CA import CentralizedAuthority
from.utils import create_new_EHR, get_data, insert_data

server_CA = CentralizedAuthority()
# server_CA.AddPolicy()

def index(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())

@never_cache
def signup(request):
    if request.method == 'POST':
        db = server_CA.client['user']
        log_and_auth = db['logAndAuth']

        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        status = request.POST['status']

        if status == 'Patient':
            role = 'user'
        else:
            role = 'staff'

        hashed_password = make_password(password)

        user_data = {
            'name': name,
            'email': email,
            'username': username,
            'password': hashed_password,
            'role': role,
            'status': status
        }
        result = log_and_auth.insert_one(user_data)

        # Get the ObjectId
        object_id = result.inserted_id

        # Generate public key master key for new user
        server_CA.Setup(str(object_id))

        # Generate EHR document for new user
        create_new_EHR(request, str(object_id))

        return redirect('myfirstapp:index')
    else:
        return render(request, 'pages-register.html')
    
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
        # client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
        db = server_CA.client['user']
        collection = db['logAndAuth']

        username = request.POST['username']
        password = request.POST['password']

        user = collection.find_one({'username': username})
        stored_password = user['password']
        if check_password(password, stored_password):
            # Convert ObjectId to string
            user['_id'] = str(user['_id'])
            request.session['user'] = user
            if user['role'] == 'user':
                return redirect('myfirstapp:patient_profile')
            else:
                return redirect('myfirstapp:staff_profile')
        # If no matching username and password found
        return redirect('myfirstapp:index')
    else:
        return render(request, 'pages-login1.html')

def logout(request):
    request.session.pop('user', None)
    return redirect('myfirstapp:index')

def forgot_password(request):
    return render(request, 'forgot_password.html')

# myfirstapp/views.py
@never_cache
@custom_login_required
def staff_profile(request):
    user = request.session['user']

    user_id = str(user['_id'])
    template = loader.get_template('staff_profile.html')
    return HttpResponse(template.render({'user_id': user_id}, request))

@never_cache
@custom_login_required
def patient_profile(request):
    user = request.session['user']
    # user_id = str(user['_id'])
    # client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
    # collection = client['data']['ehr']
    # patient_info = collection.find_one({'_id': ObjectId(user_id)})

    # Check if the user's role is 'user'
    # if user['role'] != 'user':
    # template = loader.get_template('users-profile copy.html')
    return render(request, 'users-profile copy.html')
    # return HttpResponse(template.render({'patient_info': patient_info}, request))
# The check_password function in Django uses the PBKDF2 algorithm with a SHA-256 hash. 
# It is the default password hashing algorithm used by Django for user authentication.
        
