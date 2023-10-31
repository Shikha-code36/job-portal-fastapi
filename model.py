from pydantic import BaseModel
from typing import List

# Pydantic Models
class Employer(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    company_name: str
    password: str

class Job(BaseModel):
    job_title: str
    job_description: str
    skills_required: List[str]
    experience_required: str