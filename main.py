from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

class KundaliRequest(BaseModel):
    name: str
    date: str
    time: str
    place: str


@app.post("/generate")
def generate_kundali(data: KundaliRequest):

    prompt = f"""
    Act as a professional Vedic astrologer.

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
    Strengths and weaknesses
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    result = chat_completion.choices[0].message.content

    return {"kundali": result}