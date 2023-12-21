# Import Charm-Crypto
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.ac17 import AC17CPABE
from pymongo import MongoClient
from charm.core.engine.util import objectToBytes, bytesToObject
from .CPABE import CPABE
import pickle

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
            'userID' : str(userID),
            'public_key' : objectToBytes(public_key, self.cpabe.ac17.group),
            'master_key' : objectToBytes(master_key, self.cpabe.ac17.group)
        }
        collection.insert_one(new_key)
        return

    def GetSubjectAttribute(self, userID, attribute_name): # attribute name is a list string 
        # Load public key 
        attribute = {} 
        return attribute

    def GeneratePrivateKey(self, userID, attribute):
        db = self.client['CA']
        collection = db['key']
        key_info = collection.find_one({'userID' : userID})
        master_key = bytesToObject(key_info['master_key'])
        public_key = bytesToObject(key_info['public_key'])
        private_key = self.cpabe.ac17.keygen(public_key, master_key, attribute)
        return private_key

    def AddPolicy(self): # Call by admin
        policy1 = '(DOCTOR or NURSE or PATIENT)'
        policy2 = '(DOCTOR and DERMATOLOGY)'
        db = self.client['policy_repository']
        collection = db['abe']
        collection.insert_one({'policy' : policy1})
        collection.insert_one({'policy' : policy2})
        return 
    


    