from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

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

        # Read without assuming header
        df = pd.read_excel(io.BytesIO(contents), header=None)

        # 🔍 Try multiple possible SGPA positions (robust)
        possible_cols = [-3, -2, -4]

        sgpa = None
        for col in possible_cols:
            temp = pd.to_numeric(df.iloc[:, col], errors='coerce').dropna()
            if len(temp) > 10:  # valid column must have enough values
                sgpa = temp
                break

        if sgpa is None or sgpa.empty:
            raise HTTPException(status_code=400, detail="SGPA column not detected")

        total_students = len(sgpa)
        passed = len(sgpa[sgpa >= 5])
        failed = len(sgpa[sgpa < 5])

        pass_rate = (passed / total_students) * 100 if total_students else 0

        return {
            "totalStudents": int(total_students),
            "passed": int(passed),
            "failed": int(failed),
            "passRate": round(pass_rate, 2),

            "averageSGPA": round(float(sgpa.mean()), 2),
            "highestSGPA": round(float(sgpa.max()), 2),
            "lowestSGPA": round(float(sgpa.min()), 2),

            "elite": int((sgpa > 9).sum()),
            "distinction": int(((sgpa >= 7.5) & (sgpa <= 9)).sum()),
            "firstClass": int(((sgpa >= 6.5) & (sgpa < 7.5)).sum()),
            "secondClass": int(((sgpa >= 5) & (sgpa < 6.5)).sum()),
            "belowAvg": int((sgpa < 5).sum())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))