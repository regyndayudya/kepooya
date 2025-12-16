from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import json

app = Flask(__name__)
app.secret_key = '@o<j4AH*I+0qZ>4meUG;SuIq:1DK=Q'

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import string

# Load database.json content
def load_db():
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
            if 'pertanyaan_db' in data:
                data['pertanyaana_db'] = {str(k): v for k, v in data['pertanyaan_db'].items()}
            if 'jawaban_db' in data:
                 data['jawaban_db'] = {str(k): v for k, v in data['jawaban_db'].items()}
            return data
        
    except FileNotFoundError:
        return {"pertanyaan_db": {}, "jawaban_db": {}, "progress_db": {}}

# Save to database.json
def save_db(data):
    with open('database.json', 'w') as f:
        json.dump(data, f, indent=4)

# Route for the home page
@app.route('/')
def welcome():
   return render_template('welcome.html')

# Route for the home page after login
@app.route('/home')
def home():
    return render_template('home.html')

# Route to create a new question
@app.route('/buat', methods=['GET', 'POST'])
def buat_pertanyaan():
    if request.method == 'POST':
        # Menggunakan .get() untuk keamanan
        pertanyaan = request.form.get('tanyaInput', '').strip()
        if not pertanyaan:
            return "Pertanyaan tidak boleh kosong!", 400

        # Generate unique ID dan token
        kode_pertanyaan = str(random.randint(10000, 99999))
        temp_token = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        
        # Simpan token akses Lihat Jawaban ke sesi
        session[f'answers_token_{kode_pertanyaan}'] = temp_token

        db = load_db()

        db['pertanyaan_db'][kode_pertanyaan] = {
            'tanya': pertanyaan, 
            'jawaban': []
        }
        
        # =========================================================
        # LOGIKA PENGUNCI (CREATOR LOCK) DITAMBAHKAN DI SINI
        # Tandai browser ini sebagai 'pembuat' untuk mencegah menjawab
        # =========================================================
        session[f'creator_lock_{kode_pertanyaan}'] = True 

        save_db(db)
        
        # Redirect ke halaman share, membawa kode dan token sesi
        return redirect(url_for('share', kode=kode_pertanyaan, token=temp_token))

    return render_template('buat_pertanyaan.html')

# Route to share the question link
@app.route('/share/<string:kode>', methods=['GET'])
def share(kode):
    temp_token = request.args.get('token')
    db = load_db()
    kode = str(kode)
    if kode not in db['pertanyaan_db']:
        return "Pertanyaan tidak ditemukan", 404

    link = f"{request.url_root}jawab/{kode}"
    
    return render_template('share.html', 
                           link=link,
                           kode=kode, 
                           temp_token=temp_token)

# Route for answering a question
@app.route('/jawab/<string:kode>', methods=['GET', 'POST'])
def jawab_pertanyaan(kode):
    db = load_db()
    kode = str(kode)
    
    # =========================================================
    # 1. PEMERIKSAAN CREATOR LOCK
    # Mencegah pembuat pertanyaan menjawab pertanyaannya sendiri
    # =========================================================
    if session.get(f'creator_lock_{kode}'):
        return "Anda adalah pembuat pertanyaan ini. Silakan bagikan link ini kepada orang lain.", 403
    
    if kode not in db['pertanyaan_db']:
        return "Pertanyaan tidak ditemukan", 404
        
    pertanyaan_data = db['pertanyaan_db'][kode]

    if request.method == 'POST':
        # Ambil data jawaban dan validasi
        jawaban = request.form.get('jawabanInput', '').strip() 
        
        if not jawaban:
            return "Jawaban tidak boleh kosong!", 400

        # Simpan jawaban
        pertanyaan_data['jawaban'].append(jawaban)
        save_db(db)
        
        # 2. REDIRECT SETELAH BERHASIL (Memberikan efek 'keluar')
        return redirect(url_for('home'))

    # Metode GET: Tampilkan formulir jawaban
    # 3. PASTIKAN VARIABEL DIKIRIM KE TEMPLATE
    return render_template(
        'jawab_pertanyaan.html', 
        tanya=pertanyaan_data['tanya'],
        kode=kode
    )

    # Metode GET: Tampilkan formulir jawaban
    return render_template(
        'jawab_pertanyaan.html', 
        tanya=pertanyaan_data['tanya'], # <-- PERBAIKAN: Mengirimkan teks pertanyaan
        kode=kode                      # <-- Mengirimkan kode untuk action form HTML
    )

# Route to view answers to a question
# app.py

@app.route('/lihatjawaban/<string:kode>/<string:token>', methods=['GET'])
def lihat_jawaban(kode, token):
    
    db = load_db()
    
    session_key = f'answers_token_{kode}'

    if session.get(session_key) == token:
        if kode not in db['pertanyaan_db']: 
             return "Pertanyaan tidak ditemukan", 404
        
        pertanyaan_data = db['pertanyaan_db'][kode]

        return render_template(
            'lihat_jawaban.html', 
            tanya=pertanyaan_data['tanya'], 
            jawaban=pertanyaan_data['jawaban']
        )
        
    else:
        # Akses Ditolak (hanya jika token di sesi berbeda atau sesi sudah berakhir secara alami)
        return "Akses ditolak atau sesi telah berakhir. Anda harus membuat pertanyaan baru untuk mendapatkan akses.", 403
    
# Start the app
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0') 

