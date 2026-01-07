from pydantic import BaseModel

class ResumeInput(BaseModel):
    full_name: str
    Email_Address:str
    Phone_Number:str
    job_title: str
    skills: str
    experience: str
    education: str
    certifications:str
    projects: str
    

    
class UserQuery(BaseModel):
    prompt: str
