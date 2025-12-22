import os
import json
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = '@o<j4AH*I+0qZ>4meUG;SuIq:1DK=Q'

# CONFIGURATION
# This folder will hold all your individual question files
DB_FOLDER = 'db_data'

# Ensure the database folder exists when the app starts
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# --- HELPER FUNCTIONS (The "Sharding" Logic) ---

def get_question(kode):
    """
    O(1) Operation: Loads ONLY the specific question file needed.
    Returns the dictionary data or None if file doesn't exist.
    """
    filepath = os.path.join(DB_FOLDER, f"{kode}.json")
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)

def save_question(kode, data):
    """
    O(1) Operation: Saves ONLY the specific question file.
    """
    filepath = os.path.join(DB_FOLDER, f"{kode}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---

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

        # Generate unique ID
        kode_pertanyaan = str(random.randint(10000, 99999))
        
        # Check for collision (ensure we don't overwrite an existing file)
        # This is very fast (O(1)) check
        while os.path.exists(os.path.join(DB_FOLDER, f"{kode_pertanyaan}.json")):
             kode_pertanyaan = str(random.randint(10000, 99999))

        temp_token = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        
        # Save session data
        session[f'answers_token_{kode_pertanyaan}'] = temp_token
        session[f'creator_lock_{kode_pertanyaan}'] = True 

        # Prepare the data structure for THIS specific question
        question_data = {
            'tanya': pertanyaan, 
            'jawaban': []
        }
        
        # SAVE: Creates a new file like 'db_data/12345.json'
        save_question(kode_pertanyaan, question_data)
        
        return redirect(url_for('share', kode=kode_pertanyaan, token=temp_token))

    return render_template('buat_pertanyaan.html')

@app.route('/share/<string:kode>', methods=['GET'])
def share(kode):
    temp_token = request.args.get('token')
    
    # Check if file exists (O(1) lookup)
    if not os.path.exists(os.path.join(DB_FOLDER, f"{kode}.json")):
        return "Pertanyaan tidak ditemukan", 404

    link = f"{request.url_root}jawab/{kode}"
    
    return render_template('share.html', 
                           link=link,
                           kode=kode, 
                           temp_token=temp_token)

@app.route('/jawab/<string:kode>', methods=['GET', 'POST'])
def jawab_pertanyaan(kode):
    # Check Creator Lock
    if session.get(f'creator_lock_{kode}'):
        return "Anda adalah pembuat pertanyaan ini. Silakan bagikan link ini kepada orang lain.", 403
    
    # LOAD: Read specific file
    data = get_question(kode)
    if not data:
        return "Pertanyaan tidak ditemukan", 404

    if request.method == 'POST':
        jawaban = request.form.get('jawabanInput', '').strip()
        if not jawaban:
            return "Jawaban tidak boleh kosong!", 400

        # Update data in memory
        data['jawaban'].append(jawaban)
        
        # SAVE: Rewrite only this specific file
        save_question(kode, data)
        
        return redirect(url_for('welcome'))
    return render_template('jawab_pertanyaan.html', tanya=data['tanya'], kode=kode)

@app.route('/lihatjawaban/<string:kode>/<string:token>', methods=['GET'])
def lihat_jawaban(kode, token):
    session_key = f'answers_token_{kode}'

    if session.get(session_key) == token:
        # LOAD: Read specific file
        data = get_question(kode)
        
        if not data:
             return "Pertanyaan tidak ditemukan", 404
        
        return render_template('lihat_jawaban.html', 
                               tanya=data['tanya'], 
                               jawaban=data['jawaban'])
    else:
        return "Akses ditolak atau sesi telah berakhir. Anda harus membuat pertanyaan baru untuk mendapatkan akses.", 403

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
    