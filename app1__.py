from flask import Flask, render_template, request, url_for, redirect, session,jsonify
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token,  get_jwt
import bcrypt
from waitress import serve
import os
from flask_cors import CORS
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
app = Flask(__name__)
cors = CORS(app, origins='*', supports_credentials=True, expose_headers=['Content-Type'])
app.secret_key = APP_SECRET_KEY

# Connect to your MongoDB database
def MongoDB():
    client = MongoClient(MONGODB_URL)
    db_records = client.get_database('records')
    employer_records = db_records.employer
    applicant_records = db_records.applicant
    jd_records = db_records.jd
    result_records = db_records.result
    return employer_records, applicant_records, jd_records, result_records

employer_records, applicant_records, jd_records, result_records = MongoDB()

# Configure Flask JWT Extended
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

# Routes

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    message = ''
    if request.method == "POST":
        data = request.get_json()
        user = data.get("fullname")
        email = data.get("email")
        employer = data.get("employer")
        password1 = data.get("password1")
        password2 = data.get("password2")
        if not user or not email or not employer or not password1 or not password2:            
            return {'message': 'Please fill in all the fields'}
        if password1 != password2:        
            return {'message': 'Passwords do not match'}
        email_found = employer_records.find_one({"email": email})        
        if email_found:
            return {'message': 'This email already exists in the database'}
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'employer': employer, 'email': email, 'password': hashed}
            r_id = employer_records.insert_one(user_input).inserted_id
            # user_data = employer_records.find_one({"email": email})
            # new_email = user_data['email']
            access_token = create_access_token(identity=email, fresh=True)
            return jsonify(access_token, str(r_id))

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        email_found = employer_records.find_one({"email": email})
        if email_found != None:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            r_data = employer_records.find_one({},{"_id":1 , "email": email})
            r_id = str(r_data['_id'])
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                access_token = create_access_token(identity=email, fresh=True)            
                return jsonify(access_token, r_id)
        else:
            message = 'Email not found'
            return  {'message': 'This email does not exists in the database'}, 401

@app.route('/dashboard/<r_id>', methods=["POST", "GET"])
# @jwt_required(fresh=True)  
def dashboard(r_id):
    if request.method == "POST":
        data = request.get_json()
        j_id = jd_records.insert_one(data).inserted_id
        return str(j_id)
    if request.method == 'GET':
        jds = []
        for x in jd_records.find({"r_id": r_id},{"jd":1, "weights":1, "job_title":1, 'status':1}):
            x['_id'] = str(x['_id'])
            jds.append(x) 
        return { 'data' : jds}
    
@app.route('/job/<j_id>', methods=["POST", "GET"])
# @jwt_required(fresh=True)  
def job(j_id):
    if request.method == 'GET':
        try:
            job_details = jd_records.find_one({"_id":ObjectId(j_id)},{"jd":1, "weights":1, "job_title":1, 'status':1})
        except Exception as e:
            return {'message': 'Invalid Job id'}, 404
        if job_details == None:
            return {'message': 'Invalid Job id'}
        applicant_details = []
        for x in applicant_records.find({"j_id":str(j_id)}, {"name":1, "email":1, "phone":1, "candidate_score":1, "status":1, 'Achievements':1,\
                'Skills':1, "Projects":1, 'Coding Profile(s)':1, 'Education':1, 'Test Score':1, 'Experience':1}):
            del x['_id']
            applicant_details.append(x) 
        del job_details['_id']
        job_details['candidates'] = applicant_details
        return jsonify(job_details)
    
if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
    # app.run(port=5001)
