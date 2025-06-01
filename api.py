from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://localhost:27017/')
db = client['uhome']
collectionUser = db['user']

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    resultuser = collectionUser.find_one({'email': email})

    if resultuser:
        if bcrypt.checkpw(password.encode(), resultuser['password'].encode()):
            return {
                'status': 'success',
                'data_user': {
                    'id_user': str(resultuser['_id']),
                    'nama': resultuser['nama'],
                    'email': resultuser['email'],
                    'telepon': resultuser['telepon'],
                }
            }
        else:
            return {'status': 'error', 'msg': 'email atau password salah'}
    else:
        return {'status': 'error', 'msg': 'email atau password salah'}

    
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
    
    