from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
from bson import ObjectId

app = Flask(__name__)
CORS(app)
sdasdsadadads

# Koneksi ke MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['uhome']
collectionUser = db['user']
collectionHome = db['home']
collectionFavorite = db['favorite']

# Endpoint Get Data Home
@app.route('/home', methods=['GET'])
def get_homes():
    homes_cursor = collectionHome.find()
    homes = []
    for home in homes_cursor:
        homes.append({
            'id': str(home['_id']),
            'judul': home.get('judul'),
            'lokasi': home.get('lokasi'),
            'harga': home.get('harga'),
            'gambar': home.get('gambar')
        })
    return jsonify(homes)

# Endpoint: Get daftar favorit user
@app.route('/favorites/<user_email>', methods=['GET'])
def get_user_favorites(user_email):
    fav_cursor = collectionFavorite.find({'user_email': user_email})
    favorites = []
    for fav in fav_cursor:
        # Ambil detail properti dari koleksi `home`
        home = collectionHome.find_one({'_id': ObjectId(fav['home_id'])})
        if home:
            favorites.append({
                'id': str(home['_id']),
                'judul': home.get('judul'),
                'lokasi': home.get('lokasi'),
                'harga': home.get('harga'),
                'gambar': home.get('gambar')
            })
    return jsonify(favorites)

# Endpoint: Tambah favorit dari klik icon di Home
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_email = data.get('user_email')
    home_id = data.get('home_id')

    # Cek duplikat
    existing = collectionFavorite.find_one({
        'user_email': user_email,
        'home_id': home_id
    })
    if existing:
        return jsonify({'status': 'error', 'msg': 'Sudah difavoritkan'}), 400

    collectionFavorite.insert_one({
        'user_email': user_email,
        'home_id': home_id
    })
    return jsonify({'status': 'success', 'msg': 'Ditambahkan ke favorit'}), 201

# Endpoint: Hapus favorit dari klik ulang icon di Home
@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.json
    user_email = data.get('user_email')
    home_id = data.get('home_id')

    result = collectionFavorite.delete_one({
        'user_email': user_email,
        'home_id': home_id
    })

    if result.deleted_count > 0:
        return jsonify({'status': 'success', 'msg': 'Favorit dihapus'}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'Data tidak ditemukan'}), 404

# Endpoint Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    resultuser = collectionUser.find_one({'email': email})

    if resultuser:
        if bcrypt.checkpw(password.encode(), resultuser['password'].encode()):
            return {'status': 'success'}
        else:
            return {'status': 'error', 'msg': 'email atau password salah'}
    else:
        return {'status': 'error', 'msg': 'email atau password salah'}

# Endpoint Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = collectionUser.find_one({'email': data['email']})
    
    if existing_user:
        return {
            'status': 'error',
            'msg': 'Email sudah terdaftar'
        }

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = {
        'nama': data['nama'],
        'email': data['email'],
        'password': hashed_password.decode('utf-8'),
        'telepon': data['telepon'],
    }
    collectionUser.insert_one(new_user)

    return {
        'status': 'success',
        'msg': 'Registrasi berhasil'
    }

# Jalankan server
if __name__ == '__main__':
    app.run(debug=True)
    