# Import Charm-Crypto
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.ac17 import AC17CPABE
from pymongo import MongoClient
from charm.core.engine.util import objectToBytes, bytesToObject
from .CPABE import CPABE
import pickle
from bson import ObjectId
from flatten_json import flatten, unflatten

class CentralizedAuthority:
    def __init__(self):
        self.connection_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
        self.client = MongoClient(self.connection_string)
        self.cpabe = CPABE("AC17")

    '''
        Setup is called when admin adds a new user.
        User ID = sha256(Username || Random(32)), in Database: UserID is primary key. To get userID, we need username and password
        Json {'uid' : userID, 'publickey' : public_key, 'masterkey' : masterkey} will be stored on Cloud (MongoDB) and only CA can acess this database
        Users can view their uid and public key
    '''

    def Setup(self, userID):
        (public_key, master_key) = self.cpabe.ac17.setup()
        db = self.client['CA']
        collection = db['key']
        new_key = {
            '_id' : ObjectId(userID),
            'public_key' : objectToBytes(public_key, self.cpabe.ac17.group),
            'master_key' : objectToBytes(master_key, self.cpabe.ac17.group)
        }
        collection.insert_one(new_key)
        return

    def GetKey(self, keyname):
        '''
            Key name is either 'public_key' or 'master_key'
        '''
        db = self.client['CA']
        collection = db['key']
        valid_key = collection.find({'valid' : True})[0]
        key = bytesToObject(valid_key[keyname], self.cpabe.groupObj)
        return key


    def GetPrivateKey(self, userID): # Attribute of user as dict
        attribute = self.GetSubjectAttribute(userID)
        # Convert to list attribute
        attribute = flatten(attribute, ".")
        list_attribute = []
        # list_attribute = list(attribute.values())
        for x in attribute.items():
            value = x[1]
            if type(value) is not str:
                value = str(value)
            value = value.upper()
            list_attribute.append(value)

        # DEBUG
        # list_attribute = ['PATIENT', 'STOMACH', 'STOMATCH', 'ABE']

        public_key = self.GetKey('public_key')
        master_key = self.GetKey('master_key')

        private_key = self.cpabe.ac17.keygen(public_key, master_key, list_attribute)
        return private_key

    def AddPolicy(self): # Call by admin
        policy1 = '(DOCTOR or NURSE or PATIENT)'
        policy2 = '(DOCTOR and DERMATOLOGY)'
        db = self.client['policy_repository']
        collection = db['abe']
        collection.insert_one({'policy' : policy1})
        collection.insert_one({'policy' : policy2})
        return 
    
    def GetSubjectAttribute(self, userID): # attribute name is a list string 
        CA_db = self.client['CA']
        attribute_col = CA_db['subject_attribute']
        user_attribute = attribute_col.find_one({'_id' : ObjectId(userID)})    
        user_attribute['_id'] = str(user_attribute['_id'])
        print("ATTRIBUTE:", user_attribute)
        return user_attribute

    