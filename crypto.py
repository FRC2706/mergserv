import Crypto.Signature.PKCS1_PSS
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

def verify_signature(data, public_key, signature):
	m_hash = SHA.new(data)
	key = RSA.importKey(public_key)
	cipher = PKCS1_PSS.new(key)
	return cipher.verify(m_hash, signature)

def create_signature(data, private_key):
	m_hash = SHA.new(data)
	key = RSA.importKey(private_key)
	cipher = PKCS1_PSS.new(key)
	return cipher.sign(data)
