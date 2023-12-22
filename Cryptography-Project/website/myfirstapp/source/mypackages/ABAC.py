from pymongo import MongoClient
from py_abac import PDP, Policy, Request
from py_abac.storage.mongo import MongoStorage

# from CA import CentralizedAuthority
# server_CA = CentralizedAuthority()
# Policy definition in JSON
connect_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
policy_json = {
    "uid": "3",
    "description": "Max and Nina are allowed to create, delete, get any "
                   "resources only if the client IP matches.",
    "effect": "allow",
    "rules": {
        "subject": [{"$.name": {"condition": "Equals", "value": "Max"}},
                    {"$.name": {"condition": "Equals", "value": "Nina"}}],
        "resource": {"$.name": {"condition": "RegexMatch", "value": ".*"}},
        "action": [{"$.method": {"condition": "Equals", "value": "create"}},
                   {"$.method": {"condition": "Equals", "value": "delete"}},
                   {"$.method": {"condition": "Equals", "value": "get"}}],
        "context": {"$.ip": {"condition": "CIDR", "value": "127.0.0.1/32"}}
    },
    "targets": {},
    "priority": 0
}
# Parse JSON and create policy object
policy = Policy.from_json(policy_json)

# Setup policy storage
client = MongoClient(connect_string)
storage = MongoStorage(client)
# Add policy to storage
# storage.add(policy)

# Create policy decision point
pdp = PDP(storage)

# A sample access request JSON
request_json = {
    "subject": {
        "id": "2",
        "attributes": {"name": "Max"}
    },
    "resource": {
        "id": "2",
        "attributes": {"name": "myrn:example.com:resource:123"}
    },
    "action": {
        "id": "3",
        "attributes": {"method": "get"}
    },
    "context": {
        "ip": "127.0.0.1"
    }
}
# Parse JSON and create access request object
request = Request.from_json(request_json)

# Check if access request is allowed. Evaluates to True since
# Max is allowed to get any resource when client IP matches.
if pdp.is_allowed(request):
    print("LMAO")
else:
    print("NOT OK")