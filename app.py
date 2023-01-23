from flask import Flask, jsonify, request, Response
from bson import json_util
from passlib.hash import pbkdf2_sha256
import uuid

import pymongo
# Database
client = pymongo.MongoClient()
db = client.users_system

app = Flask(__name__)
app.secret_key = 'mysecretkey'


@app.route('/users', methods=['POST'])
def create_user():
    # Get data:
    try:
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        # Check for existing email address
        if db.users.find_one({'email': email}):
            return jsonify({'error': "email address already exists"}), 400

        if username and email and password:
            encrypted_password= pbkdf2_sha256.encrypt(password)
            _id = uuid.uuid4().hex

            # Add to database
            db.users.insert_one({'_id': _id,'username': username, 'password': encrypted_password,'email': email})

            response = jsonify({'_id': _id,'username': username,'password': password,'email': email})
            response.status_code = 201
            return response
    except:
        return not_enough_fields()

@app.route('/users', methods=['GET'])
def get_users():
    users = db.users.find()
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")

@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = db.users.find_one({'_id': id})
    if user:
        response = json_util.dumps(user)
        return Response(response, mimetype="application/json")
    else:
        return not_found(id)

@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    if db.users.find_one({'_id': id}):
        db.users.delete_one({'_id': id})
        response = jsonify({'message': 'User ' + id + ' was deleted successfully'})
        response.status_code = 200
        return response
    else:
        return not_found(id)

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    if db.users.find_one({'_id': id}):
        try:
            username = request.json['username']
            email = request.json['email']
            password = request.json['password']
            if username and email and password and id:
                encrypted_password= pbkdf2_sha256.encrypt(password)
                db.users.update_one({'_id': id}, {'$set': {'username': username, 'email': email, 'password': encrypted_password}})
                response = jsonify({'message': 'User ' + id + ' was Updated Successfuly'})
                response.status_code = 200
                return response
        except:
            not_enough_fields ()
    else:
      return not_found(id)

@app.errorhandler(404)
def not_found(id):
    message = {
        'message': 'User Id Not Found: ' + id,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response

def not_enough_fields ():
    message = {
                'message': 'not enough fields',
                'status': 404
            }
    response = jsonify(message)
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True, port=3000)