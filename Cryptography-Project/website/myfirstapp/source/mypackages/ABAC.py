from pymongo import MongoClient
from py_abac import PDP, Policy, Request
from py_abac.storage.mongo import MongoStorage
from .CA import CentralizedAuthority

server_CA = CentralizedAuthority()

class AttributeBaseAccessControl:
    def __init__(self):
        self.position = {'database' : 'policy_repository', 'collection' : 'abac'}
        self.storage = MongoStorage(server_CA.client, db_name=self.position['database'], collection=self.position['collection'])
        self.pdp = PDP(self.storage)
    
    # In the case that staff request to get data of user in ehr
    def inform_request(self, handled_request, requester_id):
        requester_attribute = server_CA.GetSubjectAttribute(requester_id)

        resource = handled_request['resource_attributes']
        resource["source"] = "HospitalData:EHR"

        request_access_format = {
                                    "subject": { # requester
                                        "id": "2",
                                        "attributes": requester_attribute,
                                    },
                                    "resource": {
                                        "id": "2",
                                        "attributes": resource,
                                    },
                                    "action": {
                                        "id": "3",
                                        "attributes": {"method": f"{handled_request['method'].lower()}"}
                                    },
                                    "context": {}
                                }
        print("request_access: \n", request_access_format)
        return request_access_format
        

    def request_access(self, handled_request, requester_id):
        request_access_json = self.inform_request(handled_request, requester_id)
        rqst = Request.from_json(request_access_json)
        print("REQUEST", request_access_json)
        if self.pdp.is_allowed(rqst):
            return True
        else:
            return False


'''
# A sample access request JSON
request_access_format = {
    "subject": {
        "id": "2",
        "attributes": {"name": "patient", "cccd" : "22521168"} // attribute cua benh nhan
    },
    "resource": {
        "id": "2",
        "attributes": {"name": "HospitalData:EHR", "cccd" : "22520064"} // request cua benh nhan
    },
    "action": {
        "id": "3",
        "attributes": {"method": "get"}
    },
    "context": {}
}

request_access_format = {
    "subject": {
        "id": "2",
        "attributes": {"name": "doctor", "specialty" : "stomach"} # Attribute của bác sĩ (co cccd).
    },
    "resource": {
        "id": "2",
        "attributes": {"name": "HospitalData:EHR", "disease" : "dermatology"} # Filter bác sĩ gửi lên. nhưng chỉ quan tâm đến disease thôi.
    },
    "action": {
        "id": "3",
        "attributes": {"method": "get"}
    },
    "context": {}
}
'''
        




# {'subject': {'id': '', 'attributes': {'name': 'doctor'}}, 'resource': {'id': '', 'attributes': {'name': 'data:ehr:6587d0795d62f74e3aced841:medical_history'}}, 'action': {'id': '', 'attributes': {'method': 'GET'}}, 'context': {'specialty': 'dermatology', 'disease': 'dermatology'}}
























# connect_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
# doctor_policy_json = {
#     "uid": "1",
#     "description": "Doctor can get and post EHR of all patient in HospitalData.EHR if their specialty is the same with patient's specialty.",
#     "effect": "allow",
#     "rules": {
#         "subject": [{"$.name": {"condition": "Equals", "value": "doctor"}}],
#         "resource": [{"$.name": {"condition": "RegexMatch", "value": "^HospitalData:EHR$"}}],
#         "action": [{"$.method": {"condition": "Equals", "value": "get"}},
#                    {"$.method": {"condition": "Equals", "value": "post"}}],
#         "context": [{"$.doctor_specialty": {"condition": "Equals", "value": "stomach"}, "$.patient_specialty" : {"condition": "Equals", "value": "stomach"}},
#                     {"$.doctor_specialty": {"condition": "Equals", "value": "dermatology"}, "$.patient_specialty" : {"condition": "Equals", "value": "dermatology"}}]
#     },
#     "targets": {},
#     "priority": 0
# }

# patient_policy_json = {
#     "uid": "1",
#     "description": "Patients can get their own EHR (if their ID (cccd) when they login matchs with EHR ID (cccd))",
#     "effect": "allow",
#     "rules": {
#         "subject": [{"$.name": {"condition": "Equals", "value": "patient"}}],
#         "resource": [{"$.name": {"condition": "Equals", "value": "HospitalData:EHR"}}],
#         "action": [{"$.method": {"condition": "Equals", "value": "get"}}],
#         "context": [{"$.requester_cccd": {"condition": "Equals", "value": "$.ehr_patient_cccd"}}]
#     },
#     "targets": {},
#     "priority": 0
# }

# policy = Policy.from_json(patient_policy_json)

# # Setup policy storage
# client = MongoClient(connect_string)
# storage = MongoStorage(client, db_name="policy_repository", collection="abac")
# # Add policy to storage
# storage.add(policy)

# # Create policy decision point
# pdp = PDP(storage)

# # A sample access request JSON
# request_access_format = {
#     "subject": {
#         "id": "2",
#         "attributes": {"name": "patient"}
#     },
#     "resource": {
#         "id": "2",
#         "attributes": {"name": "HospitalData:EHR"}
#     },
#     "action": {
#         "id": "3",
#         "attributes": {"method": "get"}
#     },
#     "context": {
#         "requester_cccd" : "22521168",
#         "patient_cccd" : "22521168",
#     }
# }

# # Parse JSON and create access request object
# request = Request.from_json(request_access_format)

# # Check if access request is allowed. Evaluates to True since
# # Max is allowed to get any resource when client IP matches.
# if pdp.is_allowed(request):
#     print("LMAO")
# else:
#     print("NOT OK")
