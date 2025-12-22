import os
import json
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from cryptography.fernet import Fernet  # <--- NEW: Import Encryption Library

app = Flask(__name__)
app.secret_key = '@o<j4AH*I+0qZ>4meUG;SuIq:1DK=Q'

# CONFIGURATION
DB_FOLDER = 'db_data'
KEY_FILE = 'file_key.key'  # <--- NEW: File to store the encryption key

# 1. SETUP: Create DB folder
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# 2. SETUP: encryption Key Management
# We need a key to lock/unlock files. 
# If it doesn't exist, we generate it once and save it.
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()

# Initialize the Cipher Suite
cipher = Fernet(key)

# --- HELPER FUNCTIONS (Now with Encryption!) ---

def get_question(kode):
    """
    O(1) Operation: Loads and DECRYPTS the specific question file.
    """
    filepath = os.path.join(DB_FOLDER, f"{kode}.json")
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'rb') as f:  # Read as Bytes ('rb')
            encrypted_data = f.read()
        
        # DECRYPT: Turn gibberish back into JSON string
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Parse JSON
        return json.loads(decrypted_data)
    except Exception as e:
        print(f"Error decrypting file {kode}: {e}")
        return None

def save_question(kode, data):
    """
    O(1) Operation: ENCRYPTS and saves the specific question file.
    """
    filepath = os.path.join(DB_FOLDER, f"{kode}.json")
    
    # Convert Dictionary -> JSON String -> Bytes
    json_string = json.dumps(data)
    data_bytes = json_string.encode('utf-8')
    
    # ENCRYPT: Turn bytes into gibberish
    encrypted_data = cipher.encrypt(data_bytes)
    
    with open(filepath, 'wb') as f:  # Write as Bytes ('wb')
        f.write(encrypted_data)

# --- ROUTES (Logic remains exactly the same) ---

@app.route('/')
def welcome():
   return render_template('welcome.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/buat', methods=['GET', 'POST'])
def buat_pertanyaan():
    if request.method == 'POST':
        pertanyaan = request.form.get('tanyaInput', '').strip()
        if not pertanyaan:
            return "Pertanyaan tidak boleh kosong!", 400

        kode_pertanyaan = str(random.randint(10000, 99999))
        
        while os.path.exists(os.path.join(DB_FOLDER, f"{kode_pertanyaan}.json")):
             kode_pertanyaan = str(random.randint(10000, 99999))

        temp_token = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        
        session[f'answers_token_{kode_pertanyaan}'] = temp_token
        session[f'creator_lock_{kode_pertanyaan}'] = True 

        question_data = {
            'tanya': pertanyaan, 
            'jawaban': []
        }
        
        save_question(kode_pertanyaan, question_data)
        
        return redirect(url_for('share', kode=kode_pertanyaan, token=temp_token))

    return render_template('buat_pertanyaan.html')

@app.route('/share/<string:kode>', methods=['GET'])
def share(kode):
    temp_token = request.args.get('token')
    
    if not os.path.exists(os.path.join(DB_FOLDER, f"{kode}.json")):
        return "Pertanyaan tidak ditemukan", 404

    link = f"{request.url_root}jawab/{kode}"
    return render_template('share.html', link=link, kode=kode, temp_token=temp_token)

@app.route('/jawab/<string:kode>', methods=['GET', 'POST'])
def jawab_pertanyaan(kode):
    if session.get(f'creator_lock_{kode}'):
        return "Anda adalah pembuat pertanyaan ini. Silakan bagikan link ini kepada orang lain.", 403
    
    data = get_question(kode)
    if not data:
        return "Pertanyaan tidak ditemukan", 404

    if request.method == 'POST':
        jawaban = request.form.get('jawabanInput', '').strip()
        if not jawaban:
            return "Jawaban tidak boleh kosong!", 400

        data['jawaban'].append(jawaban)
        save_question(kode, data)
        
        return redirect(url_for('welcome'))

    return render_template('jawab_pertanyaan.html', tanya=data['tanya'], kode=kode)

@app.route('/lihatjawaban/<string:kode>/<string:token>', methods=['GET'])
def lihat_jawaban(kode, token):
    session_key = f'answers_token_{kode}'

    if session.get(session_key) == token:
        data = get_question(kode)
        if not data:
             return "Pertanyaan tidak ditemukan", 404
        
        return render_template('lihat_jawaban.html', tanya=data['tanya'], jawaban=data['jawaban'])
    else:
        return "Akses ditolak atau sesi telah berakhir.", 403

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')