import os
import json
import base64

def generate_secret_key(length=128):
    # Generate random bytes and encode them into a base64 string
    random_bytes = os.urandom(length)
    secret_key = base64.urlsafe_b64encode(random_bytes).decode('utf-8')

    # Trim the key to ensure it's exactly `length` characters long
    return secret_key[:length]

# Create dictionary
data = {"SECRET_KEY": generate_secret_key(128)}

# Convert to JSON
json_output = json.dumps(data, indent=2)
print(json_output)

