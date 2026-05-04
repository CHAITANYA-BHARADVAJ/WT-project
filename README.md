# ResultAnalyzer

Full-stack result analysis app for university result sheets.

## Features

- Upload PDF, Excel workbook (`.xlsx`/`.xlsm`), or CSV result sheets.
- Extract student records and subject grades.
- Analyze SGPA, CGPA, pass rate, grade distribution, toppers, and subject performance.
- Export a generated PDF report.
- Processes uploads in memory; no uploaded file is stored.

## Expected Spreadsheet Columns

Use common headers such as:

- `USN`, `Name`, `Roll No`, `SGPA`, `CGPA`, `Status`
- Subject grade columns like `22CS301`, `22CS302`, etc.
- Optional: `Total Credits`, `Credits Earned`

Long format CSV/Excel is also supported with columns like:

- `USN`, `Name`, `Subject Code`, `Grade`, `SGPA`, `CGPA`, `Status`

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Host It

Host the backend on a Python service such as Render, Railway, Azure App Service, or a VPS.

Backend settings:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Host the frontend on Vercel, Netlify, or any static hosting service.

Frontend build:

```bash
cd frontend
npm install
npm run build
```

Set this frontend environment variable to your hosted backend URL:

```bash
VITE_API_URL=https://your-backend-domain.com
```

Then deploy the `frontend/dist` folder.
