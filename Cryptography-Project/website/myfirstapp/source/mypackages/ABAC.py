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
    def inform_request(self, request, requester_id):
        patient_attribute = server_CA.GetSubjectAttribute(request.GET.get('patient_id'))
        requester_attribute = server_CA.GetSubjectAttribute(requester_id)
        request_access_format = {
                                    "subject": {
                                        "id": "",
                                        "attributes": {"name": f"{requester_attribute['status'].lower()}"}
                                    },
                                    "resource": {
                                        "id": "",
                                        # "attributes": {"name": f"{request.GET.get('database')}:{request.GET.get('collection')}:{request.GET.get('patient_id')}:{request.GET.get('source')}"}
                                        "attributes": {"name": f"data:ehr:{request.GET.get('patient_id').lower()}:{request.GET.get('source').lower()}"}
                                    },
                                    "action": {
                                        "id": "",
                                        "attributes": {"method": f"{request.method.lower()}"}
                                    },
                                    "context": {
                                        "specialty" : f"{requester_attribute['specialty'].lower()}",
                                        "disease" : f"{patient_attribute['specialty'].lower()}",
                                    }
                                }
        return request_access_format
        

    def request_access(self, request, requester_id):
        request_access_json = self.inform_request(request, requester_id)
        rqst = Request.from_json(request_access_json)
        print("REQUEST", request_access_json)
        if self.pdp.is_allowed(rqst):
            return True
        else:
            return False



        

# {'subject': {'id': '', 'attributes': {'name': 'doctor'}}, 'resource': {'id': '', 'attributes': {'name': 'data:ehr:6587d0795d62f74e3aced841:medical_history'}}, 'action': {'id': '', 'attributes': {'method': 'GET'}}, 'context': {'specialty': 'dermatology', 'disease': 'dermatology'}}



