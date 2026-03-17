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

LANG_INSTRUCTION = {
    "en": "Respond in English.",
    "hi": "Respond entirely in Hindi (Devanagari script). All text values in the JSON must be in Hindi.",
}

def get_lang_instruction(language: str) -> str:
    return LANG_INSTRUCTION.get(language, LANG_INSTRUCTION["en"])

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
    language: Optional[str] = "en"

class PersonDetails(BaseModel):
    name: str
    date: str
    time: str
    place: str

class MatchRequest(BaseModel):
    person1: PersonDetails
    person2: PersonDetails
    language: Optional[str] = "en"

class HoroscopeRequest(BaseModel):
    rashi: str
    language: Optional[str] = "en"
        period: Optional[str] = "daily"

class NumerologyRequest(BaseModel):
    name: str
    dob: str
    language: Optional[str] = "en"

class MangalRequest(BaseModel):
    name: str
    date: str
    time: str
    place: str
    language: Optional[str] = "en"

class MuhuratRequest(BaseModel):
    occasion: Optional[str] = ""
    event_type: Optional[str] = ""
    month: Optional[str] = ""
    year: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    location: Optional[str] = "India"
    language: Optional[str] = "en"

class GemstoneRequest(BaseModel):
    rashi: Optional[str] = ""
    name: Optional[str] = ""
    date: Optional[str] = ""
    time: Optional[str] = ""
    place: Optional[str] = ""
    language: Optional[str] = "en"

class AstrologerRequest(BaseModel):
    question: str
    name: Optional[str] = ""
    dob: Optional[str] = ""
    context: Optional[str] = ""
    language: Optional[str] = "en"

class PanchangRequest(BaseModel):
    date: Optional[str] = ""
    location: Optional[str] = "India"
    language: Optional[str] = "en"

@app.get("/")
def root():
    return {"message": "Kundali API is running"}

@app.post("/generate")
def generate_kundali(data: KundaliRequest):
    lang = get_lang_instruction(data.language)
    prompt = f"""Act as a professional Vedic astrologer. {lang} Person: {data.name}, DOB: {data.date}, Time: {data.time}, Place: {data.place}. Provide detailed kundali analysis: Personality, Career, Marriage, Health, Strengths and weaknesses."""
    return {"kundali": ask_groq(prompt)}

@app.post("/match")
def match_kundali(data: MatchRequest):
    lang = get_lang_instruction(data.language)
    prompt = f"""You are an expert Vedic astrologer. {lang} Analyze Kundali compatibility (Ashtakoota Milan) for:
Person 1 (Boy): Name: {data.person1.name}, DOB: {data.person1.date}, Time: {data.person1.time}, Place: {data.person1.place}
Person 2 (Girl): Name: {data.person2.name}, DOB: {data.person2.date}, Time: {data.person2.time}, Place: {data.person2.place}
Return ONLY valid JSON: {{"score":<0-36>,"verdict":"<text>","overall":"<summary>","gunas":[{{"name":"<guna>","description":"<text>","score":<n>,"maxScore":<n>}}],"mangalDosha":"<text>"}}"""
    return ask_groq_json(prompt)

@app.post("/horoscope")
def daily_horoscope(data: HoroscopeRequest):
    today = date.today().strftime("%B %d, %Y")
    year = date.today().year
    lang = get_lang_instruction(data.language)
    
    # Define period-specific prompts
    if data.period == "daily":
        time_ref = f"today ({today})"
        scope = "detailed"
    elif data.period == "weekly":
        time_ref = "this week"
        scope = "weekly overview"
    elif data.period == "monthly":
        time_ref = "this month"
        scope = "monthly forecast"
    elif data.period == "yearly":
        time_ref = f"the year {year}"
        scope = "yearly predictions"
    else:
        time_ref = f"today ({today})"
        scope = "detailed"
    
    prompt = f"""You are a Vedic astrologer. {lang} Give {time_ref} {scope} horoscope for {data.rashi} rashi. Return ONLY valid JSON: {{"rashi":"{data.rashi}","date":"{today}","overall":"<2-3 sentences>","love":"<1-2 sentences>","career":"<1-2 sentences>","health":"<1-2 sentences>","finance":"<1-2 sentences>","lucky_number":<number>,"lucky_color":"<color>","lucky_direction":"<direction>","tip":"<{data.period} tip>"}}"""
    return ask_groq_json(prompt)
@app.post("/numerology")
def numerology(data: NumerologyRequest):
    lang = get_lang_instruction(data.language)
    prompt = f"""You are a numerology expert. {lang} Analyze numerology for Name: {data.name}, DOB: {data.dob}. Return ONLY valid JSON: {{"name":"{data.name}","dob":"{data.dob}","life_path_number":<n>,"destiny_number":<n>,"soul_number":<n>,"personality_number":<n>,"life_path_meaning":"<text>","destiny_meaning":"<text>","personality":"<text>","career":"<text>","love":"<text>","strengths":"<text>","challenges":"<text>","lucky_numbers":[<n>,<n>,<n>],"lucky_years":[<year>,<year>]}}"""
    return ask_groq_json(prompt)

@app.post("/panchang")
def panchang(data: PanchangRequest):
    target_date = data.date if data.date else date.today().strftime("%B %d, %Y")
    lang = get_lang_instruction(data.language)
    prompt = f"""You are a Vedic astrologer. {lang} Give the Panchang for {target_date} for location {data.location}. Return ONLY valid JSON: {{"date":"{target_date}","location":"{data.location}","tithi":"<tithi name>","nakshatra":"<nakshatra>","yoga":"<yoga>","karan":"<karan>","var":"<weekday>","sunrise":"<time>","sunset":"<time>","rahukaal":"<time range>","yamaganda":"<time range>","gulika":"<time range>","abhijit_muhurat":"<time range>","shubh_muhurat":"<time range>","inauspicious":"<time range>","festival":"<festival name or empty>","special_notes":"<any special notes>"}}"""
    return ask_groq_json(prompt)

@app.post("/mangal")
def mangal_dosha(data: MangalRequest):
    lang = get_lang_instruction(data.language)
    prompt = f"""You are a Vedic astrologer. {lang} Check Mangal Dosha for: Name: {data.name}, DOB: {data.date}, Time: {data.time}, Place: {data.place}. Return ONLY valid JSON: {{"name":"{data.name}","has_mangal_dosha":<true|false>,"severity":"<None|Mild|Moderate|Severe>","mars_position":"<house number and sign>","explanation":"<detailed explanation>","effects":"<effects on marriage and life>","remedies":["<remedy 1>","<remedy 2>","<remedy 3>","<remedy 4>"],"compatible_with":"<who they are compatible with>","cancellation":"<if dosha is cancelled, explain why>"}}"""
    return ask_groq_json(prompt)

@app.post("/gemstone-recommendation")
def gemstone(data: GemstoneRequest):
    subject = data.rashi if data.rashi else f"{data.name}, DOB: {data.date}"
    lang = get_lang_instruction(data.language)
    prompt = f"""You are a Vedic astrologer and gemstone expert. {lang} Recommend gemstones for Rashi/person: {subject}. Return ONLY valid JSON: {{"primary_gemstone":"<stone name>","benefits":"<benefits text>","alternative_gemstones":["<stone1>","<stone2>","<stone3>"],"wearing_instructions":"<how and when to wear>","lucky_metal":"<gold/silver/copper>"}}"""
    return ask_groq_json(prompt)

@app.post("/muhurat")
def muhurat(data: MuhuratRequest):
    occasion = data.occasion or data.event_type or "General"
    period = f"{data.month} {data.year}" if data.month else f"{data.start_date} to {data.end_date}"
    lang = get_lang_instruction(data.language)
    prompt = f"""You are a Vedic astrologer. {lang} Find auspicious Muhurat for {occasion} in {period} in {data.location}. Return ONLY valid JSON: {{"auspicious_dates":[{{"date":"<date>","timing":"<time range>","nakshatra":"<nakshatra>","tithi":"<tithi>"}}],"general_advice":"<general tips>"}}"""
    return ask_groq_json(prompt)

@app.post("/astrologer-chat")
def ask_astrologer(data: AstrologerRequest):
    lang = get_lang_instruction(data.language)
    context = f"Name: {data.name}, DOB: {data.dob}" if data.name else data.context
    prompt = f"""You are an expert Vedic astrologer with 30 years of experience. {lang} Answer this astrology question: {data.question}. Context: {context}. Return ONLY valid JSON: {{"answer":"<detailed answer>","remedies":["<remedy 1>","<remedy 2>","<remedy 3>"]}}"""
    return ask_groq_json(prompt)

@app.post("/astrologer")
def ask_astrologer_legacy(data: AstrologerRequest):
    return ask_astrologer(data)
