from cryptography.fernet import Fernet
import mysql.connector, aiofiles
from pydantic import BaseModel

class encrypt_token(BaseModel):
    token_path: str
    token: str
    key_path: str
class decrypt_token(BaseModel):
    encrypted_token_path: str
    encrypted_key_path: str
class write_to_file(BaseModel):
    filename: str
    content: str
class read_from_file(BaseModel):
    filename: str
class check_username_exists(BaseModel):
    db_host: str
    db_database: str
    db_user: str
    db_passwd: str
    username: str

def encrypt_token(token_path: str, token: str, key_path: str):
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode())
    with open(token_path, "wb") as enc_token:
        enc_token.write(encrypted_token)

def decrypt_token(encrypted_token_path: str, encrypted_key_path: str):
    with open(encrypted_key_path, "rb") as key_file:
        key = key_file.read()
    with open(encrypted_token_path, "rb") as token_file:
        token = token_file.read()
    f = Fernet(key)
    decrypted_token = f.decrypt(token).decode()
    return decrypted_token

async def write_to_file(filename: str, content: str):
    async with aiofiles.open(filename, 'w') as file:
        await file.write(content)

def read_from_file(filename: str):
    with open(filename, 'r') as file:
        content = file.read()
        return content

def check_username_exists(db_host: str, db_database: str, db_user: str, db_passwd: str, username: str):
    conn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s;", (username,))
    count = cursor.fetchone()
    cursor.close()
    conn.close()
    return count
