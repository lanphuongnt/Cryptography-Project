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
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


server_CA = CentralizedAuthority()
abac = AttributeBaseAccessControl()

client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')

def index(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())
    
def custom_login_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if 'user' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('myfirstapp:login')
    return _wrapped_view_func


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
@custom_login_required
def patient_profile(request):
    user = request.session['user']
    return render(request, 'patient-profile.html', user)
    # return HttpResponse(template.render({'patient_info': patient_info}, request))
# The check_password function in Django uses the PBKDF2 algorithm with a SHA-256 hash. 
# It is the default password hashing algorithm used by Django for user authentication.

def ehr_view(request):
    user = request.session['user']
    print("user : ", user)
    ok = abac.request_access(request, requester_id=user['_id'])
    print(ok, user['_id'])
    if ok:
        response_data = get_data({'source': request.GET.get('source'), 'database': 'data',
                                 'collection': 'ehr', '_id': request.GET.get('patient_id'), 'requester_id': user['_id']})
        print(response_data)
        return render(request, "patient-view.html", response_data)
    else:
        return redirect('myfirstapp:reference')
    

@csrf_exempt
def reception(request):
    client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
    db = client['HospitalData']
    collection = db['EHR']
    account_collection = db['Account']

    post_data = request.POST
    patient_data = {}

    if request.method == 'POST':
        # Get all CCCD from EHR documents
        client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
        db = client['HospitalData']
        collection = db['EHR']

        cccd_list = set()
        for document in collection.find():
            try:
                cccd = document['patient_info']['cccd']
            except KeyError:
                break # No patients in the database
            cccd_list.add(cccd)
        print(cccd_list)
        cccd = request.POST.get('cccd')

        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                patient_data[key] = str(value)
        patient_data = unflatten(patient_data, ".")

        if cccd not in cccd_list:
            # Create a new account for the patient
            new_account = {
                'username': f"{cccd}",
                'password': make_password(cccd),
                'status': 'patient'
            }
            account_collection.insert_one(new_account)
            patient_data['cccd'] = request.POST.get('cccd')
            patient_data_insert = {
                'patient_info': patient_data,
                'visit_history' : [],
            }
            collection.insert_one(patient_data_insert)
            patient_id = collection.find_one({'patient_info.cccd': cccd})['_id']
            db = client['CA']
            collection = db['SubjectAttribute']
            new_subject_attribute = {
                '_id': str(patient_id),
                'attributes': {
                    'status': 'patient',
                    'specialty': request.POST.get('disease'),
                }
            }
            collection.insert_one(new_subject_attribute)
            messages.success(request, "Patient account created and data inserted")
        else:
            # patient_data = collection.find_one({'patient_info.cccd': patient_id})
            collection.update_one({'cccd': cccd}, {'$set': patient_data}, upsert=True)
            messages.success(request, "Patient data updated")
        
        return redirect('myfirstapp:reception')

    return render(request, 'reception.html', patient_data)

def get_patient_info(request):
    client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')
    db = client['HospitalData']
    collection = db['EHR']

    patient_id = request.GET.get('patient_id')
    patient_data = collection.find_one({'patient_info.cccd': patient_id})
    if patient_data is not None:
        patient_data['_id'] = str(patient_data['_id'])
    else:
        patient_data = {}
    return JsonResponse(patient_data)

def get_medical_history(request): # Call when staff click userID (request is POST) 
    patient_id = request.POST.get('patient_id') # name in html is the same this ('userID')
    staff_id = request.POST.get('staff_id') # Co j m fix cho nay nha @kean
    request = { # Dont mofify this request (template)
        'database' : 'data', 
        'collection' : 'ehr', 
        '_id' : patient_id, 
        'requester_id' : staff_id,
        'source' : 'visit_history',
    }
    patient_data = get_data(request)
    '''
    {'visit_history' : ...}
    '''
    return JsonResponse(patient_data)    

# DB: HospitalData - Account

def login_view(request):
    if request.method == 'POST':
        db = client['HospitalData']
        collection = db['Account']

        username = request.POST['username']
        password = request.POST['password']

        user = collection.find_one({'username': username})
        stored_password = user['password']
        if check_password(password, stored_password):
            user['_id'] = str(user['_id'])
            request.session['user'] = user
            if user['status'] == 'patient':
                return redirect('myfirstapp:patient_profile')
            elif user['status'] == 'doctor':
                return redirect('myfirstapp:doctor')
            elif user['status'] == 'receptionist':
                return redirect('myfirstapp:reception')
            else:
                return redirect('myfirstapp:index')
        # If no matching username and password found
        return redirect('myfirstapp:index')
    else:
        return render(request, 'pages-login1.html')

def signup(request):
    if request.method == 'POST':
        db = client['HospitalData']
        accounts = db['Account']

        username = request.POST['username']
        password = request.POST['password']
        status = request.POST['status'].lower()

        hashed_password = make_password(password)

        user_data = {
            'username': username,
            'password': hashed_password,
            'status' : status
        }
        result = accounts.insert_one(user_data)

        # Get the ObjectId
        object_id = result.inserted_id


        return redirect('myfirstapp:index')
    else:
        return render(request, 'pages-register.html')


def PatientHealthRecord(request):
    '''
        ABAC
    '''
    isAllowed = True
    if isAllowed:
        if request.method == "POST":
            message = InsertMedicalData(request)
            return redirect(request.META.get('HTTP_REFERER', 'myfirstapp:patient_ehr'))
        elif request.method == "GET":
            patient_ehr = GetHealthRecord(request)
            print("EHR", patient_ehr)
            return render(request, 'patient_ehr.html', patient_ehr)
    else:
        return redirect('myfirstapp:patient_ehr')
        


def GetDictValue(request):
    data = {}
    if request.method == "POST":
        post_data = request.POST
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                data[key] = value
    elif request.method == "GET":
        get_param = request.GET 
        for key, value in get_param.items():
            data[key] = value
    return data


def GetListOfPatientsWithFilter(request):
    '''
        Call ABAC to verify that requester can access this resource.
    '''
    isAllowed = True
    if isAllowed:
        database = client['HospitalData']
        collection = database['EHR']
        filter = GetDictValue(request)
        print("Filter: ",filter)
        patients = collection.find(filter)
        list_patients = []
        for patient in patients:
            patient["_id"] = str(patient["_id"])
            list_patients.append(patient)
        print({'patients' : list_patients})
        return JsonResponse({'patients' : list_patients})
        # return {'patients' : list_patients}
    else:
        return None

def GetHealthRecord(request):
    '''
        Call ABAC 
    '''
    '''
        GET
        request gồm cccd thôi :v tại vì lấy từ cái danh sách đã được lọc rồi.
    '''
    isAllowed = True
    if isAllowed:
        if request.method == "GET":
            database = client['HospitalData']
            collection = database['EHR']
            cccd = request.GET['patient'] # ID means CCCD
            if cccd is None:
                return JsonResponse({'error': 'Patient not found!'}, status=404)
            patient = collection.find_one({'patient_info.cccd' : cccd})
            

            if patient:
                list_visit_history = patient['visit_history']
                # list_visit_history = flatten(list_visit_history, ".")
                print(f"Encrypted Data: {list_visit_history}")
                recovered_list_visit_history = []

                private_key = server_CA.GetPrivateKey(request.session['user']['_id'])
                public_key = server_CA.GetKey('public_key')

                for visit_history in list_visit_history:
                    recovered_visit_history = {}
                    for ed in visit_history.items():
                        if ed[1] == "" or ed[1] is None:
                            recovered_visit_history[ed[0]] = ""
                        else:
                            recovered_visit_history[ed[0]] = server_CA.cpabe.AC17decrypt(public_key, ed[1], private_key)
                    recovered_list_visit_history.append(recovered_visit_history)

                # recovered_list_visit_history = flatten(recovered_list_visit_history, ".")
                # recovered_list_visit_history = unflatten(recovered_list_visit_history, ".")

                patient['visit_history'] = recovered_list_visit_history
                patient['_id'] = str(patient['_id'])
                print(f"PATIENT : {patient}")
                return JsonResponse(patient)
            else:
                return JsonResponse({'error': 'Patient not found!'}, status=404)
    else:
        return None
    
def InsertMedicalData(request):
    '''
    Call ABAC maybe add in doctor.
    '''
    isAllowed = True
    if isAllowed:
        database = client['HospitalData']
        collection = database['EHR']
        cccd_patient = request.GET.get('patient')
        update_data = GetDictValue(request)

        update_data = {
            f"visit_history.{update_data['visit_history_time']}" : {
                    'appointment_date' : update_data['appointment_date'],
                    'symptoms' : update_data['symptoms'],
                    'diagnosis' : update_data['diagnosis'],
                    'treatment' : update_data['treatment'],            
            }
        }
        update_data = flatten(update_data, ".")
        print("Update Data:", update_data)
        policy = server_CA.GetPolicy(request.session['user']['_id'])
        print(f"POLICY : {policy}")
        public_key = server_CA.GetKey('public_key')
        encrypted_data = {}
        for data in update_data.items():
            encrypted_data[data[0]] = server_CA.cpabe.AC17encrypt(public_key, data[1], policy)
        encrypted_data = flatten(encrypted_data, ".")
        print("Encrypted data: ", encrypted_data)
        collection.update_one({'patient_info.cccd': cccd_patient}, {'$set': encrypted_data})
        response = collection.find_one({'patient_info.cccd': cccd_patient})
        if response:
            print("Insert sucessfully!")
            return True
        else:
            print("Error!")
            return False
    else:
        print("You don't have permission to access this resource!")
        return False

def doctor(request):
    # print(request.GET.items())
    # return JsonResponse(GetListOfPatientsWithFilter(request))
    '''
        1. Call GetPatient(request) to get a list of Patient which satisfies with param of request.
        2. Call UpdateRecord(request) to update health record of patient whose ID and update POST data.
    '''
    # return render(request, 'lanphuong.html')
    # list_patient_id = GetListOfPatientsWithFilter(request)
    # # list_patient_id_json = json.dumps(list_patient_id)
    # print(GetDictValue(request))
    # print("HAHA", list_patient_id)
    # return HttpResponse('lanphuong.html')
    # return JsonResponse(list_patient_id)
 
    # print(request.method)
    # data = {'name' : 'ok', 'age':'25', 'email':'lmao@gmail.com'}
    # return JsonResponse({'data': data})
    return render(request, 'doctor.html')