from fastapi import FastAPI, HTTPException
from typing import List
from pymongo import MongoClient
from model import *
import bcrypt
import uuid

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["job_portal_db"]
employers_collection = db["employers"]
jobs_collection = db["jobs"]

@app.post("/register/")
def register_employer(employer: Employer):
    try:
        # Check if the username already exists in the database
        existing_user = employers_collection.find_one({"username": employer.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        employer_id = str(uuid.uuid4())

        # Hash the password before saving
        hashed_password = bcrypt.hashpw(employer.password.encode('utf-8'), bcrypt.gensalt())
        employer.password = hashed_password.decode('utf-8')
        emp_details = employer.dict()
        emp_details["employer_id"] = employer_id
        # Save employer data to MongoDB
        employers_collection.insert_one(emp_details)
        return {"message": "Registration successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login/")
def employer_login(username: str, password: str):
    try:
        # Retrieve hashed password from MongoDB based on username
        stored_password = employers_collection.find_one({"username": username})["password"]
        # Check if the entered password matches the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post-job/")
def post_job(job: Job):
    try:
        # Save job data to MongoDB
        jobs_collection.insert_one(job.dict())
        return {"message": "Job posted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/edit-profile/{employer_id}/")
def edit_profile(employer_id: str, employer_data: dict):
    try:
        # Construct the update document with non-null values from employer_data
        update_document = {
            "$set": {key: value for key, value in employer_data.items() if value is not None}
        }

        # Update employer profile in MongoDB based on employer_id
        updated_profile = employers_collection.update_one(
            {"employer_id": employer_id},
            update_document
        )

        if updated_profile.modified_count == 1:
            return {"message": "Profile updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Employer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job-list/")
def get_job_list():
    try:
        # Retrieve job list from MongoDB and convert ObjectId to string
        job_list = list(jobs_collection.find())
        for job in job_list:
            job["_id"] = str(job["_id"])  # Convert ObjectId to string
        return job_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/job-count/")
def get_job_count():
    try:
        # Get count of jobs from MongoDB
        job_count = jobs_collection.count_documents({})
        return {"job_count": job_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
