from pymongo import MongoClient
from py_abac import PDP, Policy, Request
from py_abac.storage.mongo import MongoStorage





connect_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
doctor_policy_json = {
    "uid": "4",
    "description": "Doctor can get and post EHR of all patient in HospitalData.EHR if their specialty is the same with patient's specialty.",
    "effect": "allow",
    "rules": {
        "subject": {"$.status": {"condition": "Equals", "value": "doctor"}, 
                    "$.specialty": {"condition": "Exists"},
                    "$.specialty": {"condition": "NotEquals", "value": ""},
                    "$.specialty": {"condition": "EqualsAttribute", "ace" : "resource", "path": "$.disease"}},
        "resource": {"$.source": {"condition": "Equals", "value": "HospitalData:EHR"},
                     "$.disease": {"condition" : "Exists"},
                     "$.disease": {"condition": "NotEquals", "value": ""},
                    },
        "action": [{"$.method": {"condition": "Equals", "value": "get"}},
                   {"$.method": {"condition": "Equals", "value": "post"}}],
        "context": {}
    },
    "targets": {},
    "priority": 0
}
# OKE
patient_policy_json = {
    "uid": "1",
    "description": "Patients can get their own EHR (if their ID (cccd) when they login matchs with EHR ID (cccd))",
    "effect": "allow",
    "rules": {
        "subject": {"$.status": {"condition": "Equals", "value": "patient"}, 
                    "$.cccd": {"condition": "Exists"},
                    "$.cccd": {"condition": "NotEquals", "value": ""},
                    "$.cccd": {"condition": "EqualsAttribute", "ace" : "resource", "path": "$.cccd"}},
        "resource": {"$.source": {"condition": "Equals", "value": "HospitalData:EHR"},
                     "$.cccd": {"condition": "Exists"},
                     "$.cccd": {"condition": "NotEquals", "value": ""},
                    },
        "action": {"$.method": {"condition": "Equals", "value": "get"}},
        "context": {},
    },
    "targets": {},
    "priority": 0
}


# patient_policy_json = {
#     "uid": "1235798",
#     "description": "Patients can get their own EHR (if their ID (cccd) when they login matchs with EHR ID (cccd))",
#     "effect": "allow",
#     "rules": {
#         "subject": [{"$.name": {"condition": "Equals", "value": "patient"}}],
#         "resource": [{"$.name": {"condition": "Equals", "value": "HospitalData:EHR"}}],
#         "action": [{"$.method": {"condition": "Equals", "value": "get"}}],
#         "context": [{"$.requester_cccd": {"condition": "Equals", "value": "22521168"}},
#                     {"$.ehr_patient_cccd": {"condition": "Equals", "value": "22521168"}}]
#     },
#     "targets": {},
#     "priority": 0
# }

policy = Policy.from_json(patient_policy_json)

# Setup policy storage
client = MongoClient(connect_string)
storage = MongoStorage(client, db_name="policy_repository", collection="abac")
# Add policy to storage
# storage.add(policy)

# Create policy decision point
pdp = PDP(storage)

# A sample access request JSON
request_access_format = {
    "subject": {
        "id": "2",
        "attributes": {"status": "patient", "cccd" : "22521168"}
    },
    "resource": {
        "id": "2",
        "attributes": {"source": "HospitalData:EHR", "cccd" : "22521168"}
    },
    "action": {
        "id": "3",
        "attributes": {"method": "get"}
    },
    "context": {}
}

# request_access_format = {
#     "subject": {
#         "id": "2",
#         "attributes": {"status": "doctor", "specialty" : "dermatology"} # Attribute của bác sĩ (co cccd).
#     },
#     "resource": {
#         "id": "2",
#         "attributes": {"source": "HospitalData:EHR", "disease" : "dermatology"} # Filter bác sĩ gửi lên. nhưng chỉ quan tâm đến disease thôi.
#     },
#     "action": {
#         "id": "3",
#         "attributes": {"method": "get"}
#     },
#     "context": {}
# }



# Parse JSON and create access request object
request = Request.from_json(request_access_format)

# Check if access request is allowed. Evaluates to True since
# Max is allowed to get any resource when client IP matches.
if pdp.is_allowed(request):
    print("LMAO")
else:
    print("NOT OK")
