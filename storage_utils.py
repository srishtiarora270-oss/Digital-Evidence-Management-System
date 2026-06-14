import base64
import json

STORAGE_KEY = b"dems_secret_key_2026"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def encrypt_text(plaintext: str, key: bytes = STORAGE_KEY) -> str:
    raw_bytes = plaintext.encode("utf-8")
    encrypted = _xor_bytes(raw_bytes, key)
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_text(ciphertext: str, key: bytes = STORAGE_KEY) -> str:
    encrypted = base64.b64decode(ciphertext.encode("utf-8"))
    raw_bytes = _xor_bytes(encrypted, key)
    return raw_bytes.decode("utf-8")


def save_encrypted_json(filename: str, data, key: bytes = STORAGE_KEY):
    json_text = json.dumps(data, indent=4)
    encrypted_text = encrypt_text(json_text, key)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(encrypted_text)


def load_encrypted_json(filename: str, key: bytes = STORAGE_KEY):
    with open(filename, "r", encoding="utf-8") as file:
        encrypted_text = file.read()
    json_text = decrypt_text(encrypted_text, key)
    return json.loads(json_text)
