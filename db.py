from pymongo import MongoClient
import os
MONGODB_URL = os.getenv('MONGODB_URL')
def MongoDB():
    client = MongoClient(MONGODB_URL)
    db_records = client.get_database('records')
    employer_records = db_records.employer
    applicant_records = db_records.applicant
    jd_records = db_records.jd
    result_records = db_records.result
    return employer_records, applicant_records, jd_records, result_records

employer_records, applicant_records, jd_records, result_records = MongoDB()
