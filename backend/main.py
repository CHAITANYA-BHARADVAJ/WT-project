"""
Result Analysis API — FastAPI Application

Provides endpoints for:
- POST /api/upload   : Upload a PDF, Excel workbook, or CSV file
- POST /api/export   : Generate a downloadable PDF report
- GET  /api/health   : Health check

Stateless design: all processing in RAM, no files stored to disk.
"""

import io
import gc
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from engine.extraction import ExtractionEngine
from engine.spreadsheet import SpreadsheetExtractionEngine
from engine.analysis import AnalysisEngine
from engine.report import ReportGenerator
from models.schemas import UploadResponse, AnalysisResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Global engine instances (stateless, reusable)
extraction_engine = ExtractionEngine()
spreadsheet_engine = SpreadsheetExtractionEngine()
analysis_engine = AnalysisEngine()
report_generator = ReportGenerator()

SUPPORTED_EXTENSIONS = {".pdf": "PDF", ".xlsx": "Excel", ".xlsm": "Excel", ".csv": "CSV"}

# Temporary in-memory store for the last analysis
# (cleared after export or next upload)
_analysis_cache: dict[str, AnalysisResult] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Result Analysis API starting up...")
    yield
    logger.info("Shutting down, clearing memory...")
    _analysis_cache.clear()
    gc.collect()


app = FastAPI(
    title="Result Analysis API",
    description="Parse university result PDFs and spreadsheets, then generate statistical analysis reports.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "result-analysis-api"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF, Excel workbook, or CSV result sheet for analysis.

    Parses the file, performs statistical analysis, and returns JSON.
    Uploaded bytes are cleared from memory after processing.
    """
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    file_kind = SUPPORTED_EXTENSIONS.get(extension)

    if not file_kind:
        raise HTTPException(status_code=400, detail="Upload a PDF, Excel workbook (.xlsx/.xlsm), or CSV file.")

    logger.info(f"Received {file_kind} upload: {filename}")
    file_bytes = b""

    try:
        # Read file into memory
        file_bytes = await file.read()
        logger.info(f"Upload size: {len(file_bytes)} bytes")

        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file.")

        if len(file_bytes) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

        # Step 1: Extract data
        if extension == ".pdf":
            metadata, students = extraction_engine.parse(file_bytes)
        else:
            metadata, students = spreadsheet_engine.parse(file_bytes, filename)
        logger.info(f"Extracted {len(students)} student records")

        if not students:
            return UploadResponse(
                success=False,
                message="No student records found. Please check the file format.",
            )

        # Step 2: Analyze
        result = analysis_engine.analyze(metadata, students)
        logger.info(f"Analysis complete: avg SGPA={result.class_average_sgpa}, pass%={result.pass_percentage}")

        # Cache for export (keyed by a session token)
        _analysis_cache["latest"] = result

        return UploadResponse(
            success=True,
            message=f"Successfully analyzed {result.total_students} student records.",
            data=result,
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    finally:
        # PRIVACY: Clear uploaded bytes immediately.
        del file_bytes
        gc.collect()
        logger.info("Upload bytes cleared from memory")


@app.post("/api/export")
async def export_report():
    """
    Generate and download a PDF summary report.

    Uses the last uploaded analysis data to produce a comprehensive
    PDF report with charts and statistics.
    """
    result = _analysis_cache.get("latest")

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No analysis data available. Upload a result file first."
        )

    try:
        logger.info("Generating PDF report...")
        pdf_bytes = report_generator.generate(result)
        logger.info(f"Report generated: {len(pdf_bytes)} bytes")

        # Stream the PDF back
        buffer = io.BytesIO(pdf_bytes)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=result_analysis_report.pdf"
            },
        )

    except Exception as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    finally:
        # Clear report bytes
        gc.collect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
