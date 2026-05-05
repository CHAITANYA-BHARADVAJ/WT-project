from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# CORS (for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API running"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_like = io.BytesIO(contents)

        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_like)
        else:
            df = pd.read_excel(file_like)

        return {
            "rows": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))