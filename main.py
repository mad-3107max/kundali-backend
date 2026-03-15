from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from typing import Optional
import os
import json
from datetime import date

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_groq(prompt: str) -> str:
    r = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
    return r.choices[0].message.content

def ask_groq_json(prompt: str) -> dict:
    raw = ask_groq(prompt)
    try:
        s = raw.find('{')
        e = raw.rfind('}') + 1
        return json.loads(raw[s:e])
    except:
        return {"error": "parse_failed", "raw": raw}

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

class HoroscopeRequest(BaseModel):
    rashi: str

class NumerologyRequest(BaseModel):
    name: str
    dob: str

class MangalRequest(BaseModel):
    name: str
    date: str
    time: str
    place: str

class MuhuratRequest(BaseModel):
    event_type: str
    start_date: str
    end_date: str
    location: Optional[str] = "India"

class GemstoneRequest(BaseModel):
    name: str
    date: str
    time: str
    place: str

class AstrologerRequest(BaseModel):
    question: str
    context: Optional[str] = ""

class PanchangRequest(BaseModel):
    date: Optional[str] = ""
    location: Optional[str] = "India"

@app.get("/")
def root():
    return {"message": "Kundali API is running"}

@app.post("/generate")
def generate_kundali(data: KundaliRequest):
    prompt = f"""Act as a professional Vedic astrologer. Person: {data.name}, DOB: {data.date}, Time: {data.time}, Place: {data.place}. Provide detailed kundali analysis: Personality, Career, Marriage, Health, Strengths and weaknesses."""
    return {"kundali": ask_groq(prompt)}

@app.post("/match")
def match_kundali(data: MatchRequest):
    prompt = f"""You are an expert Vedic astrologer. Analyze Kundali compatibility (Ashtakoota Milan) for:
Person 1 (Boy): Name: {data.person1.name}, DOB: {data.person1.date}, Time: {data.person1.time}, Place: {data.person1.place}
Person 2 (Girl): Name: {data.person2.name}, DOB: {data.person2.date}, Time: {data.person2.time}, Place: {data.person2.place}
Return ONLY valid JSON: {{"score":<0-36>,"verdict":"<Highly Compatible|Compatible|Needs Consideration>","overall":"<summary>","gunas":[{{"name":"Varna","description":"<text>","score":<n>,"maxScore":1}},{{"name":"Vashya","description":"<text>","score":<n>,"maxScore":2}},{{"name":"Tara","description":"<text>","score":<n>,"maxScore":3}},{{"name":"Yoni","description":"<text>","score":<n>,"maxScore":4}},{{"name":"Graha Maitri","description":"<text>","score":<n>,"maxScore":5}},{{"name":"Gana","description":"<text>","score":<n>,"maxScore":6}},{{"name":"Bhakoot","description":"<text>","score":<n>,"maxScore":7}},{{"name":"Nadi","description":"<text>","score":<n>,"maxScore":8}}],"mangalDosha":"<text>"}}"""
    return ask_groq_json(prompt)

@app.post("/horoscope")
def daily_horoscope(data: HoroscopeRequest):
    today = date.today().strftime("%B %d, %Y")
    prompt = f"""You are a Vedic astrologer. Give today's ({today}) detailed horoscope for {data.rashi} rashi. Return ONLY valid JSON: {{"rashi":"{data.rashi}","date":"{today}","overall":"<2-3 sentences>","love":"<1-2 sentences>","career":"<1-2 sentences>","health":"<1-2 sentences>","finance":"<1-2 sentences>","lucky_number":<number>,"lucky_color":"<color>","lucky_direction":"<direction>","tip":"<daily tip>"}}"""
    return ask_groq_json(prompt)

@app.post("/numerology")
def numerology(data: NumerologyRequest):
    prompt = f"""You are a numerology expert. Analyze numerology for Name: {data.name}, DOB: {data.dob}. Return ONLY valid JSON: {{"name":"{data.name}","dob":"{data.dob}","life_path_number":<n>,"destiny_number":<n>,"soul_number":<n>,"personality_number":<n>,"life_path_meaning":"<text>","destiny_meaning":"<text>","personality":"<text>","career":"<text>","love":"<text>","strengths":"<text>","challenges":"<text>","lucky_numbers":[<n>,<n>,<n>],"lucky_years":[<year>,<year>]}}"""
    return ask_groq_json(prompt)

@app.post("/panchang")
def panchang(data: PanchangRequest):
    target_date = data.date if data.date else date.today().strftime("%B %d, %Y")
    prompt = f"""You are a Vedic astrologer. Give the Panchang for {target_date} for location {data.location}. Return ONLY valid JSON: {{"date":"{target_date}","location":"{data.location}","tithi":"<tithi name>","nakshatra":"<nakshatra>","yoga":"<yoga>","karan":"<karan>","var":"<weekday>","sunrise":"<time>","sunset":"<time>","rahukaal":"<time range>","yamaganda":"<time range>","gulika":"<time range>","abhijit_muhurat":"<time range>","shubh_muhurat":"<time range>","inauspicious":"<time range>","festival":"<festival name or empty>","special_notes":"<any special notes>"}}"""
    return ask_groq_json(prompt)

@app.post("/mangal")
def mangal_dosha(data: MangalRequest):
    prompt = f"""You are a Vedic astrologer. Check Mangal Dosha for: Name: {data.name}, DOB: {data.date}, Time: {data.time}, Place: {data.place}. Return ONLY valid JSON: {{"name":"{data.name}","has_mangal_dosha":<true|false>,"severity":"<None|Mild|Moderate|Severe>","mars_position":"<house number and sign>","explanation":"<detailed explanation>","effects":"<effects on marriage and life>","remedies":["<remedy 1>","<remedy 2>","<remedy 3>","<remedy 4>"],"compatible_with":"<who they are compatible with>","cancellation":"<if dosha is cancelled, explain why>"}}"""
    return ask_groq_json(prompt)

@app.post("/gemstone")
def gemstone(data: GemstoneRequest):
    prompt = f"""You are a Vedic astrologer and gemstone expert. Recommend gemstones for: Name: {data.name}, DOB: {data.date}, Time: {data.time}, Place: {data.place}. Return ONLY valid JSON: {{"name":"{data.name}","primary_gemstone":{{"name":"<stone>","planet":"<planet>","finger":"<which finger>","metal":"<gold/silver>","weight":"<carats>","benefits":"<benefits>","wearing_ritual":"<how to wear>"}},"secondary_gemstones":[{{"name":"<stone>","planet":"<planet>","benefits":"<benefits>"}}],"gemstones_to_avoid":["<stone1>","<stone2>"],"rudraksha":"<recommended rudraksha beads>","lucky_metal":"<gold/silver/copper>","lucky_yantra":"<yantra name>"}}"""
    return ask_groq_json(prompt)

@app.post("/muhurat")
def muhurat(data: MuhuratRequest):
    prompt = f"""You are a Vedic astrologer. Find auspicious Muhurat for {data.event_type} between {data.start_date} and {data.end_date} in {data.location}. Return ONLY valid JSON: {{"event_type":"{data.event_type}","best_dates":[{{"date":"<date>","time":"<time range>","nakshatra":"<nakshatra>","tithi":"<tithi>","why_auspicious":"<reason>"}}],"dates_to_avoid":[{{"date":"<date>","reason":"<reason>"}}],"general_tips":"<general muhurat tips for this event>","special_considerations":"<any special Vedic considerations>"}}"""
    return ask_groq_json(prompt)

@app.post("/astrologer")
def ask_astrologer(data: AstrologerRequest):
    prompt = f"""You are an expert Vedic astrologer with 30 years of experience. Answer this astrology question clearly and helpfully: {data.question}. Context: {data.context}. Give a detailed, practical answer based on Vedic astrology principles."""
    return {"answer": ask_groq(prompt)}
