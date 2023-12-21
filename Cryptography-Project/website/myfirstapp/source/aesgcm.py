from Crypto.Cipher import AES
import hashlib

secret = b'LanPnjhbkjahddddddddddddddddddddddddddddddv kalsdngjalnfvjkandkag huong'
msg = b'Toiyeumatmahochuhuthatrataokhongthichmatmahocddd'

key = hashlib.sha256(secret).digest()

aes = AES.new(key, AES.MODE_GCM)

ciphertext, authTag = aes.encrypt_and_digest(msg)

print(f"Key length: {len(key)}")
print(f"Ciphertext: {ciphertext} - {len(ciphertext)}")
print(f"AuthTag: {authTag} - {len(authTag)}")

nonce = aes.nonce
print(f"Nonce: {nonce} - {len(nonce)}")

decryptor = AES.new(key, AES.MODE_GCM, nonce)

decrypt = decryptor.decrypt_and_verify(ciphertext, authTag)
print(decrypt) 


