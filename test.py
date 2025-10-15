from wm import encode, decode

code = """
def check_user(user, role):
    is_admin = user.role == 'admin'
    is_editor = user.role == 'editor'
    if is_admin and not is_editor:
        return True
    if user.id == 1 and user.name == "root":
        return True
    return False
"""

payload = 10

print("--- Original Code ---")
print(code)

print(f"--- Encoding Payload: {payload} ---")
watermarked_code = encode(code, payload)
print(watermarked_code)

print("--- Decoding ---")
decoded_payload = decode(watermarked_code)
print(f"Decoded Payload: {decoded_payload}")

assert payload == decoded_payload
print("\n✅ Verification Successful!")
