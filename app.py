from flask import Flask, request, render_template, send_file, flash
from Crypto.Cipher import Salsa20
from Crypto.Hash import BLAKE2b
import nacl.secret
import nacl.utils
import os
import io
from google.cloud import storage
from pymongo import MongoClient
import time

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Google Cloud Storage Configuration
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'shobi12345')
GCS_CLIENT = storage.Client()

# MongoDB Atlas Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://shobithkamisetty:1234@cluster0.15vnf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(MONGODB_URI)
db = client['mydb']
collection = db['image']

def encrypt_image(image_data, key, algorithm='xchacha20'):
    if algorithm == 'salsa20':
        nonce = os.urandom(8)
        cipher = Salsa20.new(key=key, nonce=nonce)
        encrypted_data = cipher.encrypt(image_data)
    else:  # Use XChaCha20 from PyNaCl
        key = key.ljust(32, b'\0')[:32]  # Ensure key is 32 bytes
        box = nacl.secret.SecretBox(key)
        encrypted_data = box.encrypt(image_data)

    # Use BLAKE2b for authentication
    mac = BLAKE2b.new(key=key, digest_bytes=32)
    mac.update(encrypted_data)
    mac_digest = mac.digest()

    return mac_digest + encrypted_data

def decrypt_image(encrypted_data, key, algorithm='xchacha20'):
    mac_digest = encrypted_data[:32]
    cipher_text = encrypted_data[32:]

    if algorithm == 'salsa20':
        nonce = cipher_text[:8]
        cipher_data = cipher_text[8:]
        cipher = Salsa20.new(key=key, nonce=nonce)
        decrypted_data = cipher.decrypt(cipher_data)
    else:  # Use XChaCha20 from PyNaCl
        key = key.ljust(32, b'\0')[:32]  # Ensure key is 32 bytes
        box = nacl.secret.SecretBox(key)
        decrypted_data = box.decrypt(cipher_text)

    # Verify the MAC
    mac = BLAKE2b.new(key=key, digest_bytes=32)
    mac.update(cipher_text)
    if mac.digest() != mac_digest:
        raise ValueError("MAC verification failed: data may have been tampered with")

    return decrypted_data

def upload_to_gcs(file_data, file_name):
    bucket = GCS_CLIENT.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_data)
    blob.make_public()
    return blob.public_url

def store_url_in_mongodb(url):
    collection.insert_one({"image_url": url})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files['file']
    key = request.form['key'].encode('utf-8')[:32]
    algorithm = request.form.get('algorithm', 'xchacha20')
    file_format = request.form.get('format', 'enc')
    image_data = file.read()

    encrypted_data = encrypt_image(image_data, key, algorithm)
    file_name = f"encrypted_image_{int(time.time())}.{file_format}"
    url = upload_to_gcs(encrypted_data, file_name)
    store_url_in_mongodb(url)

    flash('Image encrypted and uploaded successfully!', 'success')
    return send_file(io.BytesIO(encrypted_data), mimetype='application/octet-stream', as_attachment=True,
                     download_name=f'encrypted_image.{file_format}')

@app.route('/decrypt', methods=['POST'])
def decrypt():
    file = request.files['file']
    key = request.form['key'].encode('utf-8')[:32]
    algorithm = request.form.get('algorithm', 'xchacha20')
    encrypted_data = file.read()

    decrypted_data = decrypt_image(encrypted_data, key, algorithm)
    return send_file(io.BytesIO(decrypted_data), mimetype='image/png', as_attachment=True,
                     download_name='decrypted_image.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
