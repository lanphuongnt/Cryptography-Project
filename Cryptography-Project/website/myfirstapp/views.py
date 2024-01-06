from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .source.mypackages.ABAC import AttributeBaseAccessControl
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from pymongo import MongoClient
from django.contrib.auth.hashers import check_password, make_password

from bson import ObjectId
from django.views.decorators.cache import never_cache
from flatten_json import flatten, unflatten
from .source.mypackages.CA import CentralizedAuthority
# from .utils import get_data


server_CA = CentralizedAuthority()
abac = AttributeBaseAccessControl()

client = MongoClient('mongodb+srv://keandk:mongodb12@cluster0.hfwbqyp.mongodb.net/')


def index(request):
    template = loader.get_template('home.html')
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


@custom_login_required
def patient_profile(request):
    user = request.session['user']
    if request.method == 'POST':
        # Update height and weight
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        patient_id = user['_id']
        db = client['HospitalData']
        collection = db['EHR']
        collection.update_one({'_id': ObjectId(patient_id)}, {
                              '$set': {'patient_info.height': request.POST.get('medical_history.height'),
                                       'patient_info.weight': request.POST.get('medical_history.weight')}})

    return render(request, 'patient-profile.html', user)


# def ehr_view(request):
#     user = request.session['user']
#     print("user : ", user)
#     ok = abac.request_access(request, requester_id=user['_id'])
#     print(ok, user['_id'])
#     if ok:
#         response_data = get_data({'source': request.GET.get('source'), 'database': 'data',
#                                  'collection': 'ehr', '_id': request.GET.get('patient_id'), 'requester_id': user['_id']})
#         print(response_data)
#         return render(request, "patient-view.html", response_data)
#     else:
#         return redirect('myfirstapp:reference')


@csrf_exempt
@custom_login_required
def reception(request):
    db = client['HospitalData']
    collection = db['EHR']
    account_collection = db['Account']

    post_data = request.POST
    patient_data = {}

    if request.method == 'POST':
        # Get all CCCD from EHR documents
        db = client['HospitalData']
        collection = db['EHR']

        cccd_list = set()
        for document in collection.find():
            try:
                cccd = document['patient_info']['cccd']
            except KeyError:
                break  # No patients in the database
            cccd_list.add(cccd)
        print(cccd_list)
        cccd = request.POST.get('cccd')

        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                patient_data[key] = str(value)
        patient_data = unflatten(patient_data, ".")

        if cccd not in cccd_list:
            # Create new account
            new_account = {
                'username': f"{cccd}",
                'password': make_password(cccd),
                'status': 'patient'
            }
            account_collection.insert_one(new_account)
            
            # Insert patient data
            patient_id = account_collection.find_one({'username': cccd})['_id']
            patient_data['cccd'] = request.POST.get('cccd')
            patient_data_insert = {
                '_id': patient_id,
                'patient_info': patient_data,
                'visit_history': [],
            }
            collection.insert_one(patient_data_insert)
            
            # Insert patient attribute
            db = client['CA']
            collection = db['SubjectAttribute']
            new_subject_attribute = {
                '_id': patient_id,
                'status': 'patient',
                'cccd': cccd,
                'specialty': request.POST.get('disease').lower(),
            }
            collection.insert_one(new_subject_attribute)
            messages.success(
                request, "Patient account created and data inserted")
        else:
            # Update patient data
            patient_data_update = {
                'patient_info': patient_data,
            }
            collection.update_one({'patient_info.cccd': cccd}, {
                                  '$set': patient_data_update})
            
            # Update patient attribute
            patient_id = collection.find_one(
                {'patient_info.cccd': cccd})['_id']
            db = client['CA']
            collection = db['SubjectAttribute']
            collection.update_one({'_id': patient_id}, {
                                  '$set': {'specialty': request.POST.get('disease').lower()}})
            messages.success(request, "Patient data updated")

        return redirect('myfirstapp:reception')

    return render(request, 'reception.html', patient_data)


def get_patient_info(request):
    db = client['HospitalData']
    collection = db['EHR']

    patient_id = request.GET.get('patient_id')
    patient_data = collection.find_one({'patient_info.cccd': patient_id})
    if patient_data is not None:
        patient_data['_id'] = str(patient_data['_id'])
    else:
        patient_data = {}
    return JsonResponse(patient_data)


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
            'status': status
        }
        result = accounts.insert_one(user_data)

        # Get the ObjectId
        object_id = result.inserted_id

        return redirect('myfirstapp:index')
    else:
        return render(request, 'pages-register.html')

# MES : views.py
def PatientHealthRecord(request):
    # ABAC
    # Get attribute of user whose cccd
    
    params = GetDictValue(request)
    print("PARAMS:", params)
    if params != {}:
        cccd = request.GET.get('cccd')
        if cccd:
            attribute = server_CA.GetSubjectAttribute({'cccd' : cccd})

            if 'cccd' in attribute:
                handled_request = {
                    'method' : request.method,
                    'resource_attributes' : {
                        'cccd' : cccd,
                        'disease' : attribute['specialty'],
                    },
                    'database' : 'HospitalData',
                    'collection' : 'EHR',
                }
                isAllowed = abac.request_access(handled_request, request.session['user']['_id'])
            else:
                isAllowed = False
        else:
            isAllowed = False
    else:
        isAllowed = True
    print(f"method : {request.method}, isAllowed : {isAllowed}")
    # # END ABAC

    # isAllowed = True
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

# MES : Cai nay maybe de o utils.py
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

# MES : Cai nay de o views.py
def GetListOfPatientsWithFilter(request):
    '''
        Call ABAC to verify that requester can access this resource.
    '''

    params = GetDictValue(request)
    print("PARAMS:", params)
    if params != {}:
        # print(request.GET.get('cccd'))
        # attribute = server_CA.GetSubjectAttribute({'cccd' : request.GET.get('cccd')})

        handled_request = {
            'method' : request.method,
            'resource_attributes' : params,
            'database' : 'HospitalData',
            'collection' : 'EHR',
        }
        isAllowed = abac.request_access(handled_request, request.session['user']['_id'])
    else:
        isAllowed = True
    print(f"method : {request.method}, isAllowed : {isAllowed}")

    # isAllowed = True
    if isAllowed:
        database = client['HospitalData']
        collection = database['EHR']
        filter = GetDictValue(request)
        filter = flatten({'patient_info' : filter}, ".")
        
        print("Filter: ",filter)
        patients = collection.find(filter)
        list_patients = []
        for patient in patients:
            patient["_id"] = str(patient["_id"])
            list_patients.append(patient)
        print({'patients' : list_patients})
        return JsonResponse({'patients' : list_patients, 'message' : 'Query successfully'})
        # return {'patients' : list_patients}
    else:
        return JsonResponse({"patients" : [], "message" : "You don't have permission to access this resource!"})


def GetHealthRecord(request):
    isAllowed = True
    if isAllowed:
        if request.method == "GET":
            database = client['HospitalData']
            collection = database['EHR']
            cccd = request.GET.get('cccd') # ID means CCCD
            if cccd is None:
                return None
            patient = collection.find_one({'patient_info.cccd' : cccd})
            

            if patient:
                list_visit_history = patient['visit_history']
                print(f"Encrypted Data: {list_visit_history}")
                recovered_list_visit_history = []

                private_key = server_CA.GetPrivateKey(
                    request.session['user']['_id'])
                public_key = server_CA.GetKey('public_key')

                for visit_history in list_visit_history:
                    recovered_visit_history = {}
                    for ed in visit_history.items():
                        if ed[1] == "" or ed[1] is None:
                            recovered_visit_history[ed[0]] = ""
                        else:
                            recovered_visit_history[ed[0]] = server_CA.cpabe.AC17decrypt(
                                public_key, ed[1], private_key)
                    recovered_list_visit_history.append(
                        recovered_visit_history)

                patient['visit_history'] = recovered_list_visit_history
                patient['_id'] = str(patient['_id'])
                print(f"PATIENT : {patient}")
                return patient
            else:
                return None
    else:
        return None


def InsertMedicalData(request):
    isAllowed = True
    if isAllowed:
        database = client['HospitalData']
        collection = database['EHR']
        cccd_patient = request.GET.get('cccd')
        update_data = GetDictValue(request)

        update_data = {
            "visit_history": {
                'appointment_date': update_data['appointment_date'],
                'symptoms': update_data['symptoms'],
                'diagnosis': update_data['diagnosis'],
                'treatment': update_data['treatment'],
            }
        }
        update_data = flatten(update_data, ".")
        print("Update Data:", update_data)
        policy = server_CA.GetPolicy(request.session['user']['_id'])
        print(f"POLICY : {policy}")
        public_key = server_CA.GetKey('public_key')
        encrypted_data = {}
        for data in update_data.items():
            encrypted_data[data[0]] = server_CA.cpabe.AC17encrypt(
                public_key, data[1], policy)
        encrypted_data = unflatten(encrypted_data, ".")
        print("Encrypted data: ", encrypted_data)
        collection.update_one({'patient_info.cccd': cccd_patient}, {
                              '$push': encrypted_data})
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


def GetHealthRecordOfPatient(request):
    # Access Control with ABAC
    params = GetDictValue(request)
    print("PARAMS:", params)
    if params != {}:
        handled_request = {
            'method' : request.method,
            'resource_attributes' : params,
            'database' : 'HospitalData',
            'collection' : 'EHR',
        }
        isAllowed = abac.request_access(handled_request, request.session['user']['_id'])
    else:
        isAllowed = True
    print(f"method : {request.method}, isAllowed : {isAllowed}")
    # -- -- --- -- -- #
    if isAllowed:
        data = GetHealthRecord(request)
    else:
        data = None
    if data is not None:
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Patient not found!'}, status=404)

@custom_login_required
def doctor(request):
    '''
        1. Call GetPatient(request) to get a list of Patient which satisfies with param of request.
        2. Call UpdateRecord(request) to update health record of patient whose ID and update POST data.
    '''
    doctor_attribute = server_CA.GetSubjectAttribute(request.session['user']['_id'])
    return render(request, 'doctor.html', doctor_attribute)
