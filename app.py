from fastapi import FastAPI, File, UploadFile
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import google.generativeai as genai
import torch
import io

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")


genai.configure(api_key="KEY")
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

@app.post("/generate-captions/")
async def generate_captions(file: UploadFile = File(...)):

    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    prompt = f"""
    Generate five unique and engaging Instagram captions for the following description. 
    Each caption should be fun, include emojis, and use relevant hashtags with GenZ attitude. Keep them under 20 words.

    Caption: "{caption}"

    Format: 
    1. [caption]
    2. [caption]
    3. [caption]
    4. [caption]
    5. [caption]
    """
    response = gemini_model.generate_content(prompt)
    
    return {
        "original_caption": caption,
        "instagram_captions": response.text.split("\n")
    }
