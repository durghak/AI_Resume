from fastapi import FastAPI ,HTTPException
from pydantic import BaseModel
from resume.schemas import ResumeInput,UserQuery
import os
from dotenv import load_dotenv
import requests,httpx
from openai import OpenAI
# from resume.ai_services import generate_resume
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app=FastAPI(title="AI Resume Builder API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],           # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],           # Allows all headers
)

@app.get("/health")
def health_check():
    return {"status": "Backend is running 🚀"}
@app.post("/resume")
def submit_resume(data:ResumeInput):
    return {
        "message": "Resume data received successfully",
        "data": data
    }

@app.post("/ask")
async def ask_ai(query: UserQuery):
    print(f"Sending to Ollama: {query.prompt}") # Debug print
    
    async with httpx.AsyncClient() as client:
        try:
            # timeout=None is key! It prevents the 'loading' hang from timing out early.
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "tinyllama",
                    "prompt": query.prompt,
                    "stream": False
                },
                timeout=300.0
            )
            
            result = response.json()
            # print(f"response from Ollama: {result}")
            print(f"response text from Ollama: {result.get('response')}")   
            return {"answer": result.get("response")}

        except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))
  

@app.post("/openai")
async def ask_aii(query: UserQuery):
    try:
        # Standard OpenAI Chat Completion call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Best for resumes: fast and very cheap
            messages=[
                # {"role": "system", "content": "You are a professional resume expert."},
                {"role": "user", "content": query.prompt}
            ],
            temperature=0.7
        )
        
        # The library parses the JSON for you!
        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        # This will catch things like 'insufficient credits' or 'invalid key'
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/ai/generate")
# def generate_ai_resume(data: ResumeInput):
#     ai_text = generate_resume(data.dict())
#     return {"ai_content": ai_text}

@app.post("/ai/generate")
async def generate_resume_endpoint(data: ResumeInput):
    user_info = data.model_dump()
    prompt = f"""
    You are a professional HR recruiter.
    Create a clean, professional resume using the details below:
    Name: {user_info['full_name']}
    Email: {user_info['Email_Address']}
    Phone: {user_info['Phone_Number']}
    Title: {user_info['job_title']}
    Skills: {user_info['skills']}
    Experience: {user_info['experience']}
    Education: {user_info['education']}
    Certifications: {user_info['certifications']}
    Projects: {user_info['projects']}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return {"answer": response.choices[0].message.content}