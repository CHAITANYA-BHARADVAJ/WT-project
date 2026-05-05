from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import io
import pdfplumber

app = FastAPI()

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- HEALTH CHECK --------
@app.get("/")
def home():
    return {"message": "API running"}

# -------- UPLOAD ENDPOINT --------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # =========================
        # 📄 FILE TYPE HANDLING
        # =========================
        if file.filename.endswith(".pdf"):
            rows = []
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        rows.extend(table)

            if not rows:
                raise HTTPException(status_code=400, detail="No table found in PDF")

            df = pd.DataFrame(rows)

        else:
            # Excel
            df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")

        # =========================
        # 🧹 CLEAN DATA
        # =========================
        df = df.dropna(how="all")
        df = df.astype(str)

        # =========================
        # 🎯 FIND SGPA COLUMN
        # =========================
        sgpa = None
        sgpa_col_index = None

        for col in range(len(df.columns)):
            temp = pd.to_numeric(df.iloc[:, col], errors='coerce').dropna()

            # SGPA must be realistic
            if len(temp) > 10 and temp.max() <= 10:
                sgpa = temp
                sgpa_col_index = col
                break

        if sgpa is None:
            raise HTTPException(status_code=400, detail="SGPA column not found")

        sgpa = sgpa.astype(float)

        # =========================
        # 👨‍🎓 STUDENT ANALYSIS
        # =========================
        students = []

        for val in sgpa:
            students.append({
                "sgpa": val,
                "status": "PASS" if val >= 5 else "FAIL",
                "category":
                    "Elite" if val > 9 else
                    "Distinction" if val >= 7.5 else
                    "First Class" if val >= 6.5 else
                    "Second Class" if val >= 5 else
                    "Fail"
            })

        # =========================
        # 📚 SUBJECT ANALYSIS
        # =========================
        subject_cols = []

        for col in range(sgpa_col_index):
            temp = pd.to_numeric(df.iloc[:, col], errors='coerce').dropna()

            # GP columns usually 0–10
            if len(temp) > 20 and temp.max() <= 10:
                subject_cols.append(col)

        subjects = []

        for col in subject_cols:
            gp = pd.to_numeric(df[col], errors='coerce').dropna()

            if len(gp) < 10:
                continue

            subjects.append({
                "averageGP": round(float(gp.mean()), 2),
                "passCount": int((gp >= 5).sum()),
                "failCount": int((gp < 5).sum()),
                "passRate": round((gp >= 5).sum() / len(gp) * 100, 2)
            })

        # =========================
        # 📊 OVERALL ANALYSIS
        # =========================
        total_students = len(sgpa)

        passed = int((sgpa >= 5).sum())
        failed = int((sgpa < 5).sum())

        result = {
            "totalStudents": total_students,
            "passed": passed,
            "failed": failed,
            "passRate": round((passed / total_students) * 100, 2),

            "averageSGPA": round(float(sgpa.mean()), 2),
            "highestSGPA": round(float(sgpa.max()), 2),
            "lowestSGPA": round(float(sgpa.min()), 2),

            "elite": int((sgpa > 9).sum()),
            "distinction": int(((sgpa >= 7.5) & (sgpa <= 9)).sum()),
            "firstClass": int(((sgpa >= 6.5) & (sgpa < 7.5)).sum()),
            "secondClass": int(((sgpa >= 5) & (sgpa < 6.5)).sum()),
            "belowAvg": int((sgpa < 5).sum()),

            "students": students,
            "subjects": subjects
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))