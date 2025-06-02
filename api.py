from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
CORS(app)

# Konfigurasi koneksi MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/uhome'  # sesuaikan password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    telepon = db.Column(db.String(20))

class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200))
    lokasi = db.Column(db.String(200))
    harga = db.Column(db.String(100))
    gambar = db.Column(db.String(300))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    home_id = db.Column(db.Integer, db.ForeignKey('home.id'))

# Endpoint: Get data Home
@app.route('/home', methods=['GET'])
def get_homes():
    homes = Home.query.all()
    result = []
    for home in homes:
        result.append({
            'id': home.id,
            'judul': home.judul,
            'lokasi': home.lokasi,
            'harga': home.harga,
            'gambar': home.gambar
        })
    return jsonify(result)

# Endpoint: Get daftar favorit
@app.route('/favorites/<user_email>', methods=['GET'])
def get_user_favorites(user_email):
    favorites = Favorite.query.filter_by(user_email=user_email).all()
    result = []
    for fav in favorites:
        home = Home.query.get(fav.home_id)
        if home:
            result.append({
                'id': home.id,
                'judul': home.judul,
                'lokasi': home.lokasi,
                'harga': home.harga,
                'gambar': home.gambar
            })
    return jsonify(result)

# Endpoint: Tambah favorit
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_email = data.get('user_email')
    home_id = data.get('home_id')

    # Cek duplikat
    existing = Favorite.query.filter_by(user_email=user_email, home_id=home_id).first()
    if existing:
        return jsonify({'status': 'error', 'msg': 'Sudah difavoritkan'}), 400

    fav = Favorite(user_email=user_email, home_id=home_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': 'Ditambahkan ke favorit'}), 201

# Endpoint: Hapus favorit
@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.json
    user_email = data.get('user_email')
    home_id = data.get('home_id')

    fav = Favorite.query.filter_by(user_email=user_email, home_id=home_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Favorit dihapus'}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'Data tidak ditemukan'}), 404

# Endpoint: Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return {'status': 'success'}
    return {'status': 'error', 'msg': 'Email atau password salah'}

# Endpoint: Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return {'status': 'error', 'msg': 'Email sudah terdaftar'}

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        nama=data['nama'],
        email=data['email'],
        password=hashed_password,
        telepon=data['telepon']
    )
    db.session.add(user)
    db.session.commit()
    return {'status': 'success', 'msg': 'Registrasi berhasil'}

# Jalankan server
if __name__ == '__main__':
    app.run(debug=True)
