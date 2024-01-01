from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
from django.contrib.auth.hashers import check_password, make_password

from bson import ObjectId
from django.views.decorators.cache import never_cache
from flatten_json import flatten, unflatten
import json
from charm.core.engine.util import objectToBytes, bytesToObject
from .source.mypackages.CA import CentralizedAuthority
from.utils import create_new_EHR, get_data, insert_data, create_new_staff, get_ehr_by_specialty

from .source.mypackages.ABAC import AttributeBaseAccessControl
from django.http import JsonResponse

server_CA = CentralizedAuthority()
abac = AttributeBaseAccessControl()
def index(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())

# @never_cache
def signup(request):
    if request.method == 'POST':
        db = server_CA.client['user']
        log_and_auth = db['logAndAuth']

        username = request.POST['username']
        password = request.POST['password']
        status = request.POST['status']

        if status == 'Patient':
            role = 'user'
        else:
            role = 'staff'

        hashed_password = make_password(password)

        user_data = {
            'username': username,
            'password': hashed_password,
            'role': role,
        }
        result = log_and_auth.insert_one(user_data)

        # Get the ObjectId
        object_id = result.inserted_id

        # Generate public key master key for new user
        server_CA.Setup(str(object_id))
        if role == 'user':
            # Generate EHR document for new user
            create_new_EHR(request, str(object_id))
        else:
            create_new_staff(request, str(object_id))
        # return HttpResponse(lmao)
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


# @never_cache
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
            user['_id'] = str(user['_id'])
            request.session['user'] = user
            if user['role'] == 'user':
                return redirect('myfirstapp:patient_profile')
            elif user['role'] == 'staff':
                return redirect('myfirstapp:staff_profile')
            elif user['role'] == 'receptionist':
                return redirect('myfirstapp:reception')
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
def staff_profile(request): # Tao lo code lon cho
    # request GET ehr following SPECIALTY
    user = request.session['user']
    new_request = {
        'database' : 'data',
        'collection' : 'staff',
        '_id' : user['_id'],
        'requester_id' : user['_id'],
        'source' : 'staff_info'
    }
    staff_info = get_data(new_request)
 
    return render(request, 'staff-profile.html', staff_info)
# @never_cache
# @custom_login_required
# def patient_profile(request):
#     user = request.session['user']
#     new_request = {
#         'database' : 'data',
#         'collection' : 'ehr',
#         '_id' : user['_id'],
#         'requester_id' : user['_id']
#     }
#     staff_info = get_data(new_request)
 
#     return render(request, 'staff-profile.html', staff_info)

@never_cache
@custom_login_required
def patient_profile(request):
    user = request.session['user']
    if request.method == 'POST':
        post_data = request.POST
        update_data = {}
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                update_data[key] = str(value)
        print(update_data)
        update_data = unflatten(update_data, ".")
        # print(update_data)
        for key, value in update_data.items():
            update_request = {
                'database' : 'data', 
                'collection' : 'ehr', 
                '_id' : user['_id'], 
                'source' : key,
                'requester_id' : user['_id'],
                '$set' : {key: value},
            }
            insert_data(update_request)

    if request.method == 'GET' or request.method == 'POST':
        new_request = {
            'database' : 'data',
            'collection' : 'ehr',
            '_id' : user['_id'],
            'requester_id' : user['_id'],
            'source' : ['patient_info', 'medical_history'],
        }
        ehr_patient = get_data(new_request)
        return render(request, 'patient-profile.html', ehr_patient)
    # return HttpResponse(template.render({'patient_info': patient_info}, request))
# The check_password function in Django uses the PBKDF2 algorithm with a SHA-256 hash. 
# It is the default password hashing algorithm used by Django for user authentication.

def ehr_view(request):
    user = request.session['user']
    print("user : ", user)
    ok = abac.request_access(request, requester_id=user['_id'])
    print(ok, user['_id'])
    if ok:
        response_data = get_data({'source' : request.GET.get('source'), 'database' : 'data', 'collection' : 'ehr', '_id' : request.GET.get('patient_id'), 'requester_id' : user['_id']})
        print(response_data)
        return render(request, "patient-view.html", response_data)
    else:
        return redirect('myfirstapp:reference')
    
def reception(request):
    user = request.session['user']
    if request.method == 'POST':
        post_data = request.POST
        update_data = {}
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                update_data[key] = str(value)
        print(update_data)
        update_data = unflatten(update_data, ".")
        # print(update_data)
        for key, value in update_data.items():
            update_request = {
                'database' : 'data', 
                'collection' : 'ehr', 
                '_id' : user['_id'], 
                'source' : key,
                'requester_id' : user['_id'],
                '$set' : {key: value},
            }
            insert_data(update_request)

    if request.method == 'GET' or request.method == 'POST':
        new_request = {
            'database' : 'data',
            'collection' : 'ehr',
            '_id' : user['_id'],
            'requester_id' : user['_id'],
            'source' : ['patient_info', 'medical_history'],
        }
        ehr_patient = get_data(new_request)
        return render(request, 'patient-profile copy.html', ehr_patient)

def reference_by_specialty(request):
    user = request.session['user']
    list_patient_id = get_ehr_by_specialty(user['_id'])
    list_patient_id_json = json.dumps(list_patient_id)
    return render(request, 'reference-data.html', {'list_patient_id' : list_patient_id_json})
    # return JsonResponse(list_patient_id)

def get_medical_history(request): # Call when staff click userID (request is POST) 
    patient_id = request.POST.get('patient_id') # name in html is the same this ('userID')
    staff_id = request.POST.get('staff_id') # Co j m fix cho nay nha @kean
    request = { # Dont mofify this request (template)
        'database' : 'data', 
        'collection' : 'ehr', 
        '_id' : patient_id, 
        'requester_id' : staff_id,
        'source' : 'medical_history',
    }
    patient_data = get_data(request)
    '''
    {'medical_history' : ...}
    '''
    return JsonResponse(patient_data)    
