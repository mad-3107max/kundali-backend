from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class KundaliRequest(BaseModel):
    name: str
    date: str
    time: str
    place: str

class PersonDetails(BaseModel):
    name: str
    date: str
    time: str
    place: str

class MatchRequest(BaseModel):
    person1: PersonDetails
    person2: PersonDetails

@app.get("/")
def root():
    return {"message": "Kundali API is running"}

@app.post("/generate")
def generate_kundali(data: KundaliRequest):
    prompt = f"""Act as a professional Vedic astrologer.
Person Details:
Name: {data.name}
Date of Birth: {data.date}
Time of Birth: {data.time}
Place of Birth: {data.place}
Provide detailed kundali analysis including:
Personality
Career
Marriage
Health
Strengths and weaknesses"""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    result = chat_completion.choices[0].message.content
    return {"kundali": result}

@app.post("/match")
def match_kundali(data: MatchRequest):
    prompt = f"""You are an expert Vedic astrologer specializing in Kundali matching (Ashtakoota Milan).

Person 1 (Boy):
Name: {data.person1.name}
Date of Birth: {data.person1.date}
Time of Birth: {data.person1.time}
Place of Birth: {data.person1.place}

Person 2 (Girl):
Name: {data.person2.name}
Date of Birth: {data.person2.date}
Time of Birth: {data.person2.time}
Place of Birth: {data.person2.place}

Analyze their Kundali compatibility using Ashtakoota Milan (8 Gunas). Return ONLY a valid JSON object with this exact structure, no other text:
{{
  "score": <total score out of 36 as a number>,
  "verdict": "<Highly Compatible or Compatible or Needs Consideration>",
  "overall": "<2-3 sentence overall compatibility summary>",
  "gunas": [
    {{"name": "Varna", "description": "<analysis>", "score": <score>, "maxScore": 1}},
    {{"name": "Vashya", "description": "<analysis>", "score": <score>, "maxScore": 2}},
    {{"name": "Tara", "description": "<analysis>", "score": <score>, "maxScore": 3}},
    {{"name": "Yoni", "description": "<analysis>", "score": <score>, "maxScore": 4}},
    {{"name": "Graha Maitri", "description": "<analysis>", "score": <score>, "maxScore": 5}},
    {{"name": "Gana", "description": "<analysis>", "score": <score>, "maxScore": 6}},
    {{"name": "Bhakoot", "description": "<analysis>", "score": <score>, "maxScore": 7}},
    {{"name": "Nadi", "description": "<analysis>", "score": <score>, "maxScore": 8}}
  ],
  "mangalDosha": "<Mangal Dosha analysis for both persons>"
}}"""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    result = chat_completion.choices[0].message.content
    try:
        start = result.find('{')
        end = result.rfind('}') + 1
        json_str = result[start:end]
        return json.loads(json_str)
    except:
        return {"error": "Failed to parse response", "raw": result}
