from flatten_json import flatten, unflatten
import json
from .source.mypackages.CA import CentralizedAuthority
from bson import ObjectId
from faker import Faker

fake = Faker()        
server_CA = CentralizedAuthority()
# server_CA.AddPolicy()

def create_new_EHR(request, userID):
    status = request.POST['status']
    if status == 'Patient':
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
                "medical_history": {
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
                    "notes": fake.paragraph()
                }
            }
        }
    else:
        addition = {
            "staff_info": {
                "name": request.POST['name'],
                "dob": fake.date_of_birth().strftime("%Y-%m-%d"),
                "gender": fake.random_element(["Male", "Female"]),
                "cccd": fake.random_number(digits=12),
                "status": request.POST['status'],
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
    if status == 'Patient':
        ehr_col = db['ehr']
    else:
        ehr_col = db['staff']
    ehr_col.insert_one({'_id' : ObjectId(userID)})

    # Tui test cai nay
    new_request = {'$set' : addition}
    new_request['_id'] = userID
    new_request['database'] = 'data'
    if status == 'Patient':
        new_request['collection'] = 'ehr'
    else:
        new_request['collection'] = 'staff'
    
    insert_data(new_request)

def get_data(request):
    # Request (dict) include: database, collection, username(ObjectID), {'$get' : {'dataname1': datavalue1}, {data}}
    # Example : request = {'database' : 'data', 'collection' : 'ehr', 'username' : '65845045be5cf517d0a932e1', {'height' : 153}}
    db = server_CA.client[request['data']]
    collection = db[request['ehr']]
    encryted_data = collection.find(request['$get'])

    if encryted_data:
        encryted_data = flatten(encryted_data, ".")
        recovered_data = {}
        CA_db = server_CA.client['CA']
        attribute_col = CA_db['subject_attribute']
        user_attribute = attribute_col.find_one(request['$get'])    

        private_key = server_CA.GeneratePrivateKey(request['_id'], user_attribute)
        public_key = server_CA.GetPublicKey(request['_id'])

        for ed in encryted_data.items():
            recovered_data[ed[0]] = server_CA.cpabe.decrypt(public_key, ed[1], private_key)

        recovered_data = flatten(recovered_data, ".")
        recovered_data = unflatten(recovered_data, ".")

        return recovered_data
    else:
        return None
    
def GetSubjectAttribute(self, userID, attribute_name): # attribute name is a list string 
    # Load public key 
    attribute = {} 
    return attribute

def insert_data(request):
    # Request (dict) include: database, collection, username(ObjectID), {'$set' : {'dataname1': datavalue1}, {data}}
    # Example : request = {'database' : 'data', 'collection' : 'ehr', 'username' : '65845045be5cf517d0a932e1', {'height' : 153}}
    db = server_CA.client[request['database']]
    collection = db[request['collection']]

    update_data = request['$set']
    encrypted_data = {}
    update_data = flatten(update_data, ".")

    policy_col = server_CA.client['policy_repository']['abe']
    policy = policy_col.find_one({'request' : 'insert'})['policy']

    # CA_db = server_CA.client['CA']
    # attribute_col = CA_db['subject_attribute']
    # user_attribute = attribute_col.find_one({"_id" : ObjectId(request['username'])})    
    
    # private_key, public_key = server_CA.GeneratePrivateKey(request['username'], user_attribute)
    public_key = server_CA.GetPublicKey(request['_id'])

    for data in update_data.items():
        encrypted_data[data[0]] = server_CA.cpabe.encrypt(public_key, data[1], policy)
    encrypted_data = flatten(encrypted_data, ".")
    encrypted_data = unflatten(encrypted_data, ".")

    collection.update_one({'_id': ObjectId(request['_id'])}, {'$set': encrypted_data})
    response = collection.find_one({'_id': ObjectId(request['_id'])})
    if response:
        return True
    else:
        return False
