from flask import Flask, render_template, request, session, redirect, url_for, redirect, jsonify
from bson import ObjectId
from flask_cors import CORS
import json
from pymongo import MongoClient
import asyncio
from utils import scrape, data_cleaning
from utils import data_extraction
import threading
import multiprocessing
import os
import sys
from dotenv import load_dotenv
from waitress import serve

load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
def scraping(links):
    print('Scraping the coding profiles!')
    while links['fetched'] == False:
        pass
    print(links['links'])
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        codingData = loop.run_until_complete(scrape(links['links']))
        loop.close()
    except Exception as e:
        links['process_error'] = e
        links['links'] = (None, None, None, None)
        return
    links['links'] = (None, None, None, None)
    dc = data_cleaning()
    print(codingData)
    if len(codingData) > 0:
        try:
            cleaned_data = dc.clean_data(codingData)
            # print(cleaned_data)
        except Exception as e:    
            links['process_error'] = e
            return
        try:
            links['Coding Profile(s)'] = dc.grade_coding_profiles(cleaned_data)
        except Exception as e:
            links['process_error'] = e
            return
        
class app_class:
    def __init__(self) -> None:
        self.resume = None
        self.correct_answer = 0
        self.result = {'Education':0, 'Experience':'Very Bad', 'Skills':'Very Bad', 'Projects':'Very Bad', 'Achievements':'Very Bad', 'Coding Profile(s)':0, 'Test Score':0}  
        self.thread_error = None
        self.applicant_details = None
        self.job_details = None
    def final_verdict(self, weights=[1, 1, 1, 1, 1, 1, 1], threshold=60):
        gradestoscore = {'Very Bad':0, 'Bad':1, 'Moderate':2, 'Good':3, 'Very Good':4, 'Excellent':5}
        score_result = self.result.copy() 
        for key in self.result.keys():
            if not (key == 'Test Score' or key == 'Coding Profile(s)' or key == 'Education'):
                score_result[key] = gradestoscore[self.result[key]]          
        final_grade = score_result['Education']*weights[0] + score_result['Experience']*weights[1] + score_result['Skills']*weights[2] + score_result['Projects']*weights[3] + score_result['Achievements']*weights[4] + score_result['Coding Profile(s)']*weights[5] + score_result['Test Score']*weights[6]
        final_grade=round((final_grade/40)*100, 2)
        try:
            assert 0 <= threshold <= 100, "Value must be between 0 and 100(inclusive)"
        except Exception as e:
            print(e)
            return False, -1
        if final_grade>=threshold:
            return True, final_grade 
        else:
            return False, final_grade 
    def run_flask_app(self):
        app = Flask(__name__)
        cors = CORS(app, origins='*', supports_credentials=True, expose_headers=['Content-Type'])
        app.secret_key = APP_SECRET_KEY
        mongodb_url = MONGODB_URL
        try:
            client = MongoClient(mongodb_url)
        except Exception as e:
            print(e)
            return
        db_test = client['test']
        db_records = client.get_database('records')
        applicant_records = db_records.applicant
        jd_records = db_records.jd
        manager = multiprocessing.Manager()
        links = manager.dict()
        links['links'] = (None, None, None, None)
        links['fetched'] = False
        links['process_error'] = None
        links['Coding Profile(s)'] = 0
        def resume_print():
            print('Parsing resume!')
            try:
                de = data_extraction(self.resume.filename)
            except Exception as e:
                self.thread_error = e
                links['fetched'] = True
                thread_id = threading.get_ident()
                sys.exit(thread_id)
            links['links'] = de.links
            links['fetched'] = True
            jd = self.job_details['jd']
            self.thread_error = de.jd_comparator(jd)
            if self.thread_error:
                thread_id = threading.get_ident()
                sys.exit(thread_id)
            try:
                self.result = de.output_grade()
                # print(self.result)
            except Exception as e:
                self.thread_error = e
                thread_id = threading.get_ident()
                sys.exit(thread_id)
        global thread1 
        global p
        @app.route('/job/<j_id>', methods=['GET', 'POST'])
        def details(j_id):
            if request.method == 'GET':
                try:
                    self.job_details = jd_records.find_one({"_id":ObjectId(j_id)},{"jd":1, 'weights':1, "job_title":1, "status":1})
                except Exception as e:
                    return {'message': 'Invalid Job id'}, 404
                # print(self.job_details)
                if(self.job_details==None):
                    return {'message': 'Invalid Job Id'}, 404
                del self.job_details['_id']
                return jsonify(self.job_details)
            if request.method == 'POST':
                self.applicant_details = request.get_json()
                return {'message': 'Details submitted successfully'}

        @app.route('/job/<j_id>/upload', methods=['GET', 'POST'])
        def upload(j_id):
            if request.method == 'POST':
                self.resume = request.files['resume']
                self.resume.save(self.resume.filename)
                global thread1
                thread1 = threading.Thread(target=resume_print)
                global p
                p = multiprocessing.Process(target=scraping, args=(links,))
                thread1.start()
                p.start()
                return {'message': 'Resume uploaded successfully.'}
        def get_questions_from_collection(collection_name, limit):
            collection = db_test[collection_name]
            total_questions = collection.count_documents({})
            if total_questions <= limit:
                questions = list(collection.find())
            else:
                questions = list(collection.aggregate([{'$sample': {'size': limit}}]))
            return questions[:limit]
        aptitude_questions = get_questions_from_collection('aptitude', 10)
        questions =  aptitude_questions
        @app.route('/job/<j_id>/quiz', methods=['GET', 'POST'])
        def quiz(j_id):
            if request.method == 'POST':
                score = request.get_json()['score']
                self.correct_answer = int(score)
                return jsonify({'score': score})
            if request.method == 'GET':
                serialized_questions = [json.loads(json.dumps(q, default=str)) for q in questions]
                return jsonify(serialized_questions)
        @app.route('/job/<j_id>/result', methods=['GET'])
        def result(j_id):
            global thread1
            thread1.join()
            global p
            p.join()
            # thread error is in self.thread_error 
            if self.thread_error:
                print(self.thread_error)
            # process error is in links['process_error]    
            if links['process_error']:
                print(links['process_error'])
            self.result['Test Score'] = self.correct_answer
            self.result['Coding Profile(s)'] = links['Coding Profile(s)']
            selection, candidate_score = self.final_verdict(self.job_details['weights'])
            if candidate_score>0:
                print(candidate_score, '%\n', selection)
            result_data = {'score': self.correct_answer,'selection':selection,'candidate_score':candidate_score}
            status = 'Rejected'
            if selection:
                status = 'Interview'
            applicant_data = {'j_id': str(j_id), 'name': self.applicant_details['name'], 'email': self.applicant_details['email'], 'phone': self.applicant_details['phone'], 'status': status, 'candidate_score':candidate_score \
                               ,'Achievements':self.result['Achievements'], 'Skills':self.result['Skills'], "Projects":self.result['Projects'], 'Coding Profile(s)':self.result['Coding Profile(s)'], 'Education':self.result['Education'], 'Test Score':self.result['Test Score'], 'Experience':self.result['Experience']}
            print(applicant_data)
            applicant_records.insert_one(applicant_data)
            return jsonify(result_data)
        # app.run(debug=False, port=5000)
        serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    ap = app_class()
    ap.run_flask_app()
