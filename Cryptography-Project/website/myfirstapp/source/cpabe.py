# Import Charm-Crypto
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.ac17 import AC17CPABE
from flatten_json import flatten, unflatten
import json
from charm.core.engine.util import objectToBytes, bytesToObject
from pymongo import MongoClient
from Crypto.Cipher import AES 
import hashlib
from mypackages.SerializeCTXT import SerializeCTXT
from bson import ObjectId
connection_string = 'mongodb+srv://lanphuongnt:keandk27@cluster0.hfwbqyp.mongodb.net/'
client = MongoClient(connection_string)


serialize_encoder = SerializeCTXT()

def encrypttest(): 

    msg = {'database' : 'data',
           'collection' : 'ehr',
           '_id' : '658696add564fb6fdf9ff0f2',
           'status' : 'patient',
           'set' : {
                'name' : 'Nguyen Tran Lan Phuong',
                'email' : '22521168@gm.uit.edu.vn',   
                'specialty' : 'stomach',
            }
           }


    groupObj = PairingGroup('SS512')
    ac17 = AC17CPABE(groupObj, 2)
    (public_key, master_key) = ac17.setup()

    attibute = ['DOCTOR', 'STOMATCH']
    key = ac17.keygen(public_key, master_key, attibute)
    # print("public_key:", public_key)
    # print("master_key:", master_key)
    # random_key = groupObj.random(GT)
    # print(f"random_key : {random_key}")
    # policy = "((DOCTOR and STOMATCH) or PATIENT)"
    # ctxt = ac17.encrypt(public_key, random_key, policy)
    # print(f"ctxt : {ctxt}")
    # ctxt_b = serialize_encoder.jsonify_ctxt(ctxt)
    # print(f"ctxt_b : {ctxt_b}")
    
    # js = {'encrypted_key' : ctxt_b}
    col = client['CA']['key']
    # col.insert_one(js)
    lmao = col.find_one({'_id' : ObjectId('6586a05af5501fe0ee1b8747')})
    enc_key = lmao['encrypted_key']
    ctxt = serialize_encoder.unjsonify_ctxt(enc_key)
    rec = ac17.decrypt(public_key, ctxt, key)

    print(rec)

    # if random_key == rec:
        # print("Successfully")
    # else:
        # print("Failed")
    # print(f"ctxt : {ctxt}")
    # # print("public key", public_key)
    # # print("key", key)
        
    # # Encrypt random_key using CP-ABES
    
    # # Create key for AES by random_key

    # hash = hashlib.sha256(str(random_key).encode())
    # key = hash.digest()
    # message = message.encode('utf-8')
    # aes = AES.new(key, AES.MODE_GCM)
    # ciphertext, authTag = aes.encrypt_and_digest(message)
    # nonce = aes.nonce

    # # Final ciphertext that will be sent to database
    # ciphertext = nonce + ciphertext + authTag
    # encrypted_data = {'encrypted_key' : ctxt, 'ciphertext' : ciphertext.hex()}

encrypttest()
