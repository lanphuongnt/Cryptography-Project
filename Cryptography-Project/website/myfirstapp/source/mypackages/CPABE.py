# Import Charm-Crypto
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.ac17 import AC17CPABE
from Crypto.Cipher import AES
import hashlib
import json

class CPABE:
    def __init__(self, scheme):
        if scheme == "AC17":
            self.groupObj = PairingGroup("SS512")
            self.ac17 = AC17CPABE(self.groupObj, 2)
    def encrypt(self, public_key, message, policy):
        random_key = self.groubObj.random(GT)
        
        # Encrypt random_key using CP-ABE
        encrypted_key = self.ac17.encrypt(public_key, random_key, policy)
        
        # Create key for AES by random_key
        key = hashlib.sha256(str(random_key)).digets()
        aes = AES.new(key, AES.MODE_GCM)
        ciphertext, authTag = aes.encrypt_and_digest(message)
        nonce = aes.nonce

        # Final ciphertext that will be sent to database
        ciphertext = nonce + ciphertext + authTag
        encrypted_data = {'encrypted_data' : {'encrypted_key' : encrypted_key, 'ciphertext' : ciphertext}}
        return encrypted_data
    
    def decrypt(self, public_key, encrypted_data, private_key): # encrypted_data is dict type (not json)
        
        encrypted_key = encrypted_data['encrypted_data']['encrypted_key']
        recovered_random_key = self.decrypt(public_key, encrypted_key, private_key)
        
        if recovered_random_key:
            ciphertext = encrypted_data['encrypted_data']['ciphertext']
            nonce = ciphertext[:16]
            authTag = ciphertext[-16:]
            ciphertext = ciphertext[16:-16]
        
            key = hashlib.sha256(str(recovered_random_key)).digest()
        
            aes = AES.new(key, AES.MODE_GCM, nonce)
            recovered_message = aes.decrypt_and_verify(ciphertext, authTag)
        
            return recovered_message
        else:
            return None
        