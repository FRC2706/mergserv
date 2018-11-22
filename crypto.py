import json
import base64
import nacl.signing
import nacl.encoding

# Returns signature for row
def sign_row(row, private):
	jstr = json.dumps(obj)
	signing_key = nacl.signing.SigningKey(private, nacl.encoding.Base64Encoder)
	signature = signing_key.sign(jstr.encode('utf-8'))
	return base64.b64encode(signature.signature).decode('utf-8')

# Returns true or false
def verify_row(row, public, signature):
	obj = oobj.copy()
	signature = base64.b64decode(signature.encode('utf-8'))
	jstr = json.dumps(obj)
	verify_key = nacl.signing.VerifyKey(public, encoder=nacl.encoding.Base64Encoder)
	try:
		verify_key.verify(jstr.encode('utf-8'), signature)
		return True
	except:
		return False

