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
from mypackages.CA import CentralizedAuthority
import base64
from charm.core.engine.util import objectToBytes, bytesToObject

serialize_encoder = SerializeCTXT()
server_CA = CentralizedAuthority()
def encrypttest(): 





    groupObj = PairingGroup('SS512')
    ac17 = AC17CPABE(groupObj, 2)
    (public_key1, master_key1) = ac17.setup()

    attibute1 = ['DOCTOR']
    key1 = ac17.keygen(public_key1, master_key1, attibute1)
    # print("public_key:", public_key)
    # print("master_key:", master_key)

    (public_key2, master_key2) = ac17.setup()

    attibute2 = ['PATIENT']
    key2 = ac17.keygen(public_key1, master_key1, attibute2)

    random_key = groupObj.random(GT)
    print(f"random_key : {random_key}")
    policy = "(DOCTOR or PATIENT)"
    ctxt = ac17.encrypt(public_key1, random_key, policy)
    print(f"ctxt : {ctxt}")
    # ctxt_b = serialize_encoder.jsonify_ctxt(ctxt)
    # print(f"ctxt_b : {ctxt_b}")
    
    # b64e = base64.b64encode(ctxt_b.encode()).decode()
    # js = {'encrypted_key' : b64e}
    # print(js)
    # col = client['CA']['key']
    # col.update_one({'_id' : ObjectId('6586a05af5501fe0ee1b8747')}, {'$set' : js})
    # lmao = col.find_one({'_id' : ObjectId('6586a05af5501fe0ee1b8747')})
    # enc_key = lmao['encrypted_key']

    # ctxt_b_a= base64.b64decode(b64e.encode())

    # ctxt = serialize_encoder.unjsonify_ctxt(ctxt_b_a.decode())
    rec = ac17.decrypt(public_key1, ctxt, key2)
    rec1 = ac17.decrypt(public_key1, ctxt, key1)
    hu1 = objectToBytes(rec, groupObj)
    hu = objectToBytes(rec1, groupObj)
    hu2 = objectToBytes(random_key, groupObj)
    print(hu1)
    print(hu2)
    if hu1 == hu2 and hu == hu1:
        print("Successfully")
    else:
        print("Failed")
    if random_key == rec:
        print("Successfully")
    else:
        print("Failed")
    # print(f"ctxt : {ctxt}")
    # # print("public key", public_key)
    # # print("key", key)
        
    # # Encrypt random_key using CP-ABES
    
    # # # Create key for AES by random_key

    # # hash = hashlib.sha256(str(random_key).encode())
    # # key = hash.digest()
    # # message = message.encode('utf-8')
    # # aes = AES.new(key, AES.MODE_GCM)
    # # ciphertext, authTag = aes.encrypt_and_digest(message)
    # # nonce = aes.nonce

    # # # Final ciphertext that will be sent to database
    # # ciphertext = nonce + ciphertext + authTag
    # # encrypted_data = {'encrypted_key' : ctxt, 'ciphertext' : ciphertext.hex()}
    # print("\n\nHEHEHE\n\n")
    # message = 'NguyenTranLanPhuong'
    # random_key = groupObj.random(GT)
        
    # # Encrypt random_key using CP-ABES
    # encrypted_key = ac17.encrypt(public_key, random_key, policy)
    # # Serialize to save to database
    # encrypted_key_b = serialize_encoder.jsonify_ctxt(encrypted_key)
    # # Create key for AES by random_key
    # hash = hashlib.sha256(str(random_key).encode())
    # key = hash.digest()
    # aes = AES.new(key, AES.MODE_GCM)

    # if type(message) != bytes:
    #     if type(message) != str:
    #         message = str(message)

    # ciphertext, authTag = aes.encrypt_and_digest(message.encode())
    # nonce = aes.nonce

    # # Final ciphertext that will be sent to database
    # ciphertext = nonce + ciphertext + authTag
    
    # # 
    # len_encrypted_data = len(encrypted_key_b)
    # encrypted_data = len_encrypted_data.to_bytes(8, byteorder='big') + encrypted_key_b.encode() + ciphertext
    # # Encode Base64 for encrypted_key and ciphertext

    # encrypted_data = base64.b64encode(encrypted_data).decode()


    # col = client['data']['ehr']
    # userID = '6586d65c166fecd4a676ea51'
    # usr = col.find_one({'_id' : ObjectId(userID)})

    # encrypted_data = usr['patient_info']['ID']
    # print(f"Encrypted data: {encrypted_data}")

    # CA_db = client['CA']
    # attribute_col = CA_db['subject_attribute']
    # user_attribute = attribute_col.find_one({'_id' : ObjectId(userID)})    
    # user_attribute['_id'] = str(user_attribute['_id'])
    # private_key, public_key = server_CA.GeneratePrivateKey(userID, user_attribute)

    # # private_key = ac17.keygen(public_key, master_key, attibute)
    # print(f"private key : {private_key}")
    # encrypted_data = base64.b64decode(encrypted_data.encode())
    # len_encrypted_key = int.from_bytes(encrypted_data[:8], byteorder='big')
    # encrypted_key_b = encrypted_data[8:8 + len_encrypted_key]
    # ciphertext = encrypted_data[8 + len_encrypted_key:]

    # encrypted_key = serialize_encoder.unjsonify_ctxt(encrypted_key_b.decode('utf-8'))
    # print("type type :", type(encrypted_key['policy']))
    # print("type type private key :", type(private_key['attr_list']))

    # recovered_random_key = ac17.decrypt(public_key, encrypted_key, private_key)
    # print(recovered_random_key)
    # if recovered_random_key:
    #     nonce = ciphertext[:16]
    #     authTag = ciphertext[-16:]
    #     ciphertext = ciphertext[16:-16]
    
    #     key = hashlib.sha256(str(recovered_random_key).encode()).digest()
    
    #     aes = AES.new(key, AES.MODE_GCM, nonce)
    #     recovered_message = aes.decrypt_and_verify(ciphertext, authTag)
    #     print(recovered_message.decode())
    # else:
    #     print("Failded")
    #     return None

encrypttest()
