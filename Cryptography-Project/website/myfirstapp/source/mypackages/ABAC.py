from pymongo import MongoClient
from py_abac import PDP, Policy, Request
from py_abac.storage.mongo import MongoStorage
from CA import CentralizedAuthority

server_CA = CentralizedAuthority()

def AttributeBaseAccessControl():
    def __init__(self):
        self.position = {'database' : 'policy_repository', 'collection' : 'abac'}
        self.storage = MongoStorage(server_CA.client, db_name=self.position['database'], collection=self.position['collection'])
        self.pdp = PDP(self.storage)
    
    # In the case that staff request to get data of user in ehr
    def inform_request(request):
        patient_attribute = server_CA.GetSubjectAttribute(request.GET.get('patient_id'))
        requester_attribute = server_CA.GetSubjectAttribute(request.session['user']['_id'])
        request_access_format = {
                                    "subject": {
                                        "id": "",
                                        "attributes": {"name": f"{requester_attribute['status']}"}
                                    },
                                    "resource": {
                                        "id": "",
                                        # "attributes": {"name": f"{request.GET.get('database')}:{request.GET.get('collection')}:{request.GET.get('patient_id')}:{request.GET.get('source')}"}
                                        "attributes": {"name": f"data:ehr:{request.GET.get('patient_id')}:{request.GET.get('source')}"}
                                    },
                                    "action": {
                                        "id": "",
                                        "attributes": {"method": f"{request.method}"}
                                    },
                                    "context": {
                                        "specialty" : f"{requester_attribute['specialty']}",
                                        "disease" : f"{patient_attribute['specialty']}",
                                    }
                                }
        return request_access_format
        

    def request_access(self, request):
        request_access_json = inform_request(request)
        rqst = Request.from_json(request_access_json)
        if self.pdp.is_allowed(request):
            return True
        else:
            return False



        
























'''

connect_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
ok_policy_json = {
    "uid": "1",
    "description": "Doctor, nurse and phamarcist can get medical history of all patient in data.ehr if their specialty is the same with patient's disease.",
    "effect": "allow",
    "rules": {
        "subject": [{"$.name": {"condition": "Equals", "value": "doctor"}},
                    {"$.name": {"condition": "Equals", "value": "nurse"}},
                    {"$.name": {"condition": "Equals", "value": "pharmacist"}}],
        "resource": [{"$.name": {"condition": "RegexMatch", "value": "^data:ehr:.+:medical_history$"}}],
        "action": [{"$.method": {"condition": "Equals", "value": "get"}}],
        "context": [{"$.specialty": {"condition": "Equals", "value": "stomach"}, "$.disease" : {"condition": "Equals", "value": "stomach"}},
                    {"$.specialty": {"condition": "Equals", "value": "dermatology"}, "$.disease" : {"condition": "Equals", "value": "dermatology"}}]
    },
    "targets": {},
    "priority": 0
}


policy = Policy.from_json(ok_policy_json)

# Setup policy storage
client = MongoClient(connect_string)
storage = MongoStorage(client, db_name="policy_repository", collection="abac")
# Add policy to storage
storage.add(policy)

# Create policy decision point
pdp = PDP(storage)

# A sample access request JSON
request_access_format = {
    "subject": {
        "id": "2",
        "attributes": {"name": "pharmacist"}
    },
    "resource": {
        "id": "2",
        "attributes": {"name": "data:ehr:22521168:patient_info"}
    },
    "action": {
        "id": "3",
        "attributes": {"method": "get"}
    },
    "context": {
        "specialty" : "dermatology",
        "disease" : "dermatology",
    }
}

# Parse JSON and create access request object
request = Request.from_json(request_access_format)

# Check if access request is allowed. Evaluates to True since
# Max is allowed to get any resource when client IP matches.
if pdp.is_allowed(request):
    print("LMAO")
else:
    print("NOT OK")
'''



