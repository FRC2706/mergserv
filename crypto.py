import json
import base64
import nacl.signing
import nacl.encoding
import log

# Returns signature for row
def sign_row(row):
	jstr = json.dumps(row, separators=(',', ':'))
	jstr = "".join(jstr.split())
	signing_key = nacl.signing.SigningKey(seed, nacl.encoding.URLSafeBase64Encoder)
	signature = signing_key.sign(jstr.encode('utf-8'))
	return base64.urlsafe_b64encode(signature.signature).decode('utf-8')

# Returns true or false
def verify_row(row, public, signature):
	obj = row.copy()
	signature = base64.urlsafe_b64decode(signature.encode('utf-8'))
	jstr = json.dumps(obj, separators=(',', ':'))
	jstr = "".join(jstr.split())
	verify_key = nacl.signing.VerifyKey(public, encoder=nacl.encoding.URLSafeBase64Encoder)
	try:
		verify_key.verify(jstr.encode('utf-8'), signature)
		return True
	except:
		return False

# Load the private key
seed = None
pubkey = None
try:
        with open('private.key') as keyf:
                seed = keyf.read().strip()
        signing_key = nacl.signing.SigningKey(seed=seed, encoder=nacl.encoding.URLSafeBase64Encoder)
        pubkey = signing_key.verify_key.encode(encoder=nacl.encoding.URLSafeBase64Encoder).decode('utf-8')
except:
        log.warn("CRYPTO", "Failed to load private key, generating new key...")
        signing_key = nacl.signing.SigningKey.generate()
        pubkey = signing_key.verify_key.encode(encoder=nacl.encoding.URLSafeBase64Encoder).decode('utf-8')
        seed = signing_key.encode(encoder=nacl.encoding.URLSafeBase64Encoder).decode('utf-8')
        with open('private.key', 'w') as keyf:
                keyf.write(seed)
log.info("CRYPTO", "Loaded key: " + pubkey)
