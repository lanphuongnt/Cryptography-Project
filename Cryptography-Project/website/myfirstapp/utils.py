from flatten_json import flatten, unflatten
import json
from .source.mypackages.CA import CentralizedAuthority
from bson import ObjectId
from faker import Faker
import random

fake = Faker()        
server_CA = CentralizedAuthority()
# server_CA.AddPolicy()

def get_policy(request):
    '''
    Example request
    {
        'request' : 'insert',
        'source' : 'medical_history'
    }
    '''
    policy_col = server_CA.client['policy_repository']['abe']
    policy = policy_col.find_one(request)['policy']
    return policy

def create_subject_attribute(request):
    '''
        request = {
            '_id' : ObjectId(userID),
            'status' : status.lower(),
            'role' : 'staff',
            'specialty' : 'stomach', 
        }
    '''
    # Create user attribute
    attr_col = server_CA.client['CA']['subject_attribute']
    attr_col.insert_one(request)

def create_new_staff(request, userID):
    status = request.POST['status']
    addition = {
            "staff_info": {
                "name": request.POST['name'],
                "dob": fake.date_of_birth().strftime("%Y-%m-%d"),
                "gender": fake.random_element(["Male", "Female"]),
                "cccd": fake.random_number(digits=12),
                "status": request.POST['status'],
                "specialty": fake.random_element(["Dermatology", "Stomach"]),
                "contact": {
                    "phone": fake.phone_number(),
                    "email": request.POST['email']
                },
                "address": {
                    "street": fake.street_address(),
                    "city": fake.city(),
                    "state": fake.state(),
                    "zip": fake.zipcode()
                }
            }
        }
    db = server_CA.client['data']
    staff_col = db['staff']
    staff_col.insert_one({'_id' : ObjectId(userID)})

    request_new_attribute = {
        '_id' : ObjectId(userID),
        'status' : status.lower(),
        'role' : 'staff',
        'specialty' : addition["staff_info"]["specialty"].lower(),
    }
    create_subject_attribute(request_new_attribute)

    new_request = {
        '_id' : userID, 
        'database' : 'data', 
        'collection' : 'staff',
        'source' : 'staff_info',
        '$set' : {'staff_info' : addition["staff_info"]}
    }

    insert_data(new_request)


def create_new_EHR(request, userID):
    status = request.POST['status']
    addition = {
        "patient_info": {
            "full_name": request.POST['name'],
            "dob": fake.date_of_birth().strftime("%Y-%m-%d"),
            "gender": fake.random_element(["Male", "Female"]),
            "ID": fake.random_number(digits=12),
            "address": {
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "zip": fake.zipcode()
            },
            "contact": {
                "phone": fake.phone_number(),
                "email": request.POST['email']
            },
            "emergency_contact": {
                "name": fake.name(),
                "phone": fake.phone_number(),
                "email": fake.email()
            },
        },
        "medical_history": {
            "disease": random.choice(["Stomach"]),
            "doctorID": "6587c812fcc17eb2aa0f2bc8",
            "blood_type": fake.random_element(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            "height": fake.random_int(min=150, max=200),
            "weight": fake.random_int(min=50, max=150),
            "allergies": fake.random_element(["Pollen", "Dust", "Food", "Medication"]),
            "chronic_diseases": fake.random_element(["Diabetes", "Hypertension", "Asthma", "Arthritis"]),
            "medications": fake.random_element(["Aspirin", "Paracetamol", "Ibuprofen", "Antibiotics"]),
            "surgeries": fake.random_element(["Appendectomy", "Cataract surgery", "Knee replacement"]),
            "vaccines": fake.random_element(["Flu", "Hepatitis B", "MMR", "Tetanus"]),
            "family_history": fake.random_element(["Heart disease", "Cancer", "Diabetes", "Alzheimer's"]),
            "insurance": fake.random_element(["Yes", "No"]),
            "insurance_number": fake.random_number(digits=10),
            "insurance_company": fake.company(),
            "visits_history": [
                {
                    "date": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                    "by_who": fake.name(),
                    "reason": fake.sentence(),
                    "prescription": fake.sentence()
                },
                {
                    "date": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                    "by_who": fake.name(),
                    "reason": fake.sentence(),
                    "prescription": fake.sentence()
                }
            ],
            "notes": fake.paragraph(),
            "presentingComplaint": {
                "complaint": fake.sentence()
            },
            "clinicalFindings": {
                "findings": fake.sentence()
            },
            "allergenTesting": {
                "testing": fake.sentence()
            },
            "diagnosis": {
                "diagnosisDescription": {
                    "description": fake.sentence()
                },
                "diagnosisDate": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                "diagnosisLocation": {
                    "location": fake.city()
                },
                "diagnosisType": {
                    "type": fake.word()
                }
            },
            "treatmentPlan": {
                "allergenAvoidance": fake.sentence(),
                "topicalSteroids": fake.sentence(),
                "antihistamines": fake.sentence(),
                "treatmentPlanDescription": {
                    "description": fake.sentence()
                },
                "treatmentPlanDate": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                "treatmentPlanLocation": {
                    "location": fake.city()
                },
                "treatmentPlanType": {
                    "type": fake.word()
                }
            },
            "patientEducation": fake.paragraph(),
            "followUpPlan": {
                "followUpAppointmentDate": fake.date_between(start_date='today', end_date='+1y').strftime("%Y-%m-%d"),
                "prognosis": fake.sentence()
            }
        }
    }
        

    db = server_CA.client['data']
    ehr_col = db['ehr']
    ehr_col.insert_one({'_id' : ObjectId(userID)})

    request_new_attribute = {
        '_id' : ObjectId(userID),
        'status' : status.lower(),
        'role' : 'user',
        'specialty' : addition["medical_history"]["disease"].lower(),
    }
    create_subject_attribute(request_new_attribute)

    # Tui test cai nay
    new_request = {
        '_id' : userID, 
        'database' : 'data', 
        'collection' : 'ehr'
    }

    new_request['source'] = 'patient_info'
    new_request['$set'] = {'patient_info' : addition["patient_info"]}
    insert_data(new_request)
    new_request['source'] = 'medical_history'
    new_request['specialty'] = addition["medical_history"]["disease"].lower()
    new_request['$set'] = {'medical_history' : addition["medical_history"]}
    insert_data(new_request)

def get_data(request_get_data):
    # Request (dict) include: database, collection, username(ObjectID), {'$get' : {'dataname1': datavalue1}, {data}}
    '''
    Example : 
    request_get_data = {
        'database' : 'data', 
        'collection' : 'ehr', 
        '_id' : '65845045be5cf517d0a932e1', 
        'requester_id' : '....',
        'source' : ['medical_history'],
    '''
    if (type(request_get_data['source']) is not list):
        request_get_data['source'] = [request_get_data['source']]

    db = server_CA.client[request_get_data['database']]
    collection = db[request_get_data['collection']] 
    data = collection.find_one({'_id' : ObjectId(request_get_data['_id'])})

    if data:
        encrypted_data = {}
        for s in request_get_data['source']:
            encrypted_data[s] = data[s]
        encrypted_data = flatten(encrypted_data, ".")
        recovered_data = {}

        requester_attribute = server_CA.GetSubjectAttribute(request_get_data['requester_id'])
        private_key, public_key = server_CA.GeneratePrivateKey(request_get_data['_id'], requester_attribute)
        # public_key = server_CA.GetPublicKey(request_get_data['_id'])

        for ed in encrypted_data.items():
            if ed[0] == '_id':
                recovered_data[ed[0]] = ed[1]
                continue
            recovered_data[ed[0]] = server_CA.cpabe.AC17decrypt(public_key, ed[1], private_key)

        recovered_data = flatten(recovered_data, ".")
        recovered_data = unflatten(recovered_data, ".")
        # print(recovered_data)
        return recovered_data
    else:
        return None
    

def insert_data(request):
    # Request (dict) include: database, collection, username(ObjectID), {'$set' : {'dataname1': datavalue1}, {data}}
    '''
    Example : 
    request = {
        'database' : 'data', 
        'collection' : 'ehr', 
        '_id' : '65845045be5cf517d0a932e1', 
        'source' : medical_history,
        'requester_id' : '....', (optional)
        '$set' : {},
    }
    '''
    db = server_CA.client[request['database']]
    collection = db[request['collection']]

    update_data = request['$set']
    encrypted_data = {}
    update_data = flatten(update_data, ".")

    # policy_col = server_CA.client['policy_repository']['abe']
    # policy = policy_col.find_one({'request' : 'insert'})['policy']
    # user
    policy = get_policy({'source' : request['source']})
    # print(f"POLICY : {policy}")
    public_key = server_CA.GetPublicKey(request['_id'])

    for data in update_data.items():
        encrypted_data[data[0]] = server_CA.cpabe.AC17encrypt(public_key, data[1], policy)
    encrypted_data = flatten(encrypted_data, ".")
    # encrypted_data = unflatten(encrypted_data, ".")

    collection.update_one({'_id': ObjectId(request['_id'])}, {'$set': encrypted_data})
    response = collection.find_one({'_id': ObjectId(request['_id'])})
    if response:
        return True
    else:
        return False


def get_ehr_by_specialty(staff_ID):
    '''
        request = {
            'database' : 'data', 
            'collection' : 'ehr', 
            '_id' : '65845045be5cf517d0a932e1',
    '''

    staff_attribute = server_CA.GetSubjectAttribute(staff_ID)
    list_patient = server_CA.client['CA']['subject_attribute'].find({'specialty' : staff_attribute['specialty'], 'status' : 'patient'})
    list_patient_id = []
    for patient in list_patient:
        list_patient_id.append(str(patient['_id']))
    return {'patient' : list_patient_id}