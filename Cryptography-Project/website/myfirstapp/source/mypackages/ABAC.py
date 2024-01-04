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
        resource["source"] = f"{handled_request['database']}:{handled_request['collection']}"

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
        