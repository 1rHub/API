from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import bcrypt

app = Flask(__name__)
CORS(app)

# Konfigurasi koneksi MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/uhome'  # sesuaikan password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    nama = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    telepon = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')



class Home(db.Model):
    id = db.Column(db.String(24), primary_key=True) 
    NO = db.Column(db.String(255))
    NAMA_RUMAH = db.Column(db.String(255))
    HARGA = db.Column(db.String(100))
    LB = db.Column(db.String(50))
    LT = db.Column(db.String(50))
    KT = db.Column(db.String(10))
    KM = db.Column(db.String(10))
    GRS = db.Column(db.String(10))


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
                'NO': home.NO,
                'NAMA RUMAH': home.NAMA_RUMAH,
                'HARGA': home.HARGA,
                'LB': home.LB,
                'LT': home.LT,
                'KT': home.KT,
                'KM': home.KM,
                'GRS': home.GRS
        })
    return jsonify(result)

# Endpoint: Get daftar favorit
@app.route('/favorites/<user_email>', methods=['GET'])
def get_user_favorites(user_email):
    favorites = Favorite.query.filter_by(user_email=(user_email)).all()
    result = []
    for fav in favorites:
        home = Home.query.get(fav.home_id)
        if home:
            result.append({
                'id': home.id,
                'NO': home.NO,
                'NAMA RUMAH': home.NAMARUMAH,
                'HARGA': home.HARGA,
                'LB': home.LB,
                'LT': home.LT,
                'KT': home.KT,
                'KM': home.KM,
                'GRS': home.GRS
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

# Endpoint: Login untuk user & admin (dengan bcrypt, tanpa JWT)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return {
            'status': 'success',
            'msg': f'Login berhasil sebagai {user.role}',
            'user': {
                'id': user.id,
                'nama': user.nama,
                'email': user.email,
                'role': user.role
            }
        }

    return {'status': 'error', 'msg': 'Email atau password salah'}, 401


# Endpoint: Register untuk user dan admin
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nama = data.get('nama')
    email = data.get('email')
    password = data.get('password')
    telepon = data.get('telepon')
    role = data.get('role', 'user')  # Default ke 'user'

    # Cek apakah email sudah digunakan
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'status': 'error', 'msg': 'Email sudah terdaftar'}, 400

    # Enkripsi password dengan bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Buat user baru
    user = User(
        nama=nama,
        email=email,
        password=hashed_password,
        telepon=telepon,
        role=role
    )

    # Simpan ke database
    db.session.add(user)
    db.session.commit()

    return {'status': 'success', 'msg': f'Registrasi berhasil sebagai {role}'}, 201

# Jalankan server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

