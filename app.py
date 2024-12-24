import json
import os
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# İzin verilen IP'ler
ALLOWED_IPS = ['127.0.0.1']

# Kaydedilecek paste dosyası
DATA_FILE = 'data/pastes.json'

# Eğer paste dosyası yoksa oluştur ve boş bir liste yaz
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.before_request
def limit_remote_addr():
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_IPS:
        return "403 Forbidden: IP adresiniz izinli değil.", 403

# Anasayfa: Tüm paste'leri listele
@app.route('/')
def index():
    with open(DATA_FILE, 'r') as f:
        pastes = json.load(f)
    return render_template('index.html', pastes=pastes)

@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            # Yeni paste'i JSON dosyasına kaydet
            with open(DATA_FILE, 'r') as f:
                pastes = json.load(f)
            new_paste = {
                'id': len(pastes) + 1,
                'title': title,
                'content': content
            }
            pastes.append(new_paste)
            with open(DATA_FILE, 'w') as f:
                json.dump(pastes, f, indent=4)
            
            flash('Paste başarıyla oluşturuldu!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Başlık ve içerik boş bırakılamaz!', 'error')
    return render_template('paste.html', content=None)

# Tüm paste'leri görüntüleme sayfası
@app.route('/all_pastes')
def all_pastes():
    with open(DATA_FILE, 'r') as f:
        pastes = json.load(f)
    return render_template('all_pastes.html', pastes=pastes)

# Belirli bir paste'i görüntüleme sayfası
@app.route('/paste/<int:paste_id>')
def view_paste(paste_id):
    with open(DATA_FILE, 'r') as f:
        pastes = json.load(f)
    paste = next((p for p in pastes if p['id'] == paste_id), None)
    if paste:
        return render_template('view_paste.html', paste=paste)
    else:
        return "404 Not Found: Paste bulunamadı.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
