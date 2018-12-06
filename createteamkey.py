#!/usr/bin/python3

import nacl.signing
import nacl.encoding

signing_key = nacl.signing.SigningKey.generate()
pubkey = signing_key.verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
seed = signing_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
with open('private.key', 'w') as keyf:
    keyf.write(seed)

print("Key generated and written to private.key")
