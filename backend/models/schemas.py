"""
Pydantic schemas for the Result Analysis API.
Defines data models for student records, subjects, and analysis results.
"""

from pydantic import BaseModel, Field
from typing import Optional


class SubjectResult(BaseModel):
    """Individual subject result for a student."""
    code: str = Field(..., description="Subject code, e.g. '22UCSC300'")
    name: str = Field(default="", description="Subject name if available")
    grade: str = Field(..., description="Grade: O, A+, A, B+, B, C, P, F, AB, NE")
    grade_point: int = Field(..., description="Grade point (0-10)")
    credits: int = Field(default=0, description="Subject credits")
    earned: Optional[int] = Field(default=None, description="Credits earned")


class StudentRecord(BaseModel):
    """Complete result record for a single student."""
    sl_no: int = Field(..., description="Serial number")
    usn: str = Field(..., description="University Seat Number, e.g. '2SD21CS001'")
    roll_no: Optional[int] = Field(default=None, description="Roll number")
    name: str = Field(default="", description="Student name if available")
    subjects: list[SubjectResult] = Field(default_factory=list)
    sgpa: float = Field(default=0.0, description="Semester GPA")
    total_credits: int = Field(default=0, description="Total credits")
    credits_earned: int = Field(default=0, description="Credits earned")
    cgpa: float = Field(default=0.0, description="Cumulative GPA")
    status: str = Field(default="P", description="P=Pass, F=Fail, NE=Not Eligible, AB=Absent")
    bracket: str = Field(default="", description="Performance bracket")


class SubjectStats(BaseModel):
    """Statistics for a single subject."""
    code: str
    name: str = ""
    total_students: int = 0
    o_grade_count: int = 0
    a_plus_count: int = 0
    a_count: int = 0
    b_plus_count: int = 0
    b_count: int = 0
    c_count: int = 0
    p_count: int = 0
    f_count: int = 0
    ab_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    pass_percentage: float = 0.0
    avg_grade_point: float = 0.0
    max_grade_point: int = 0
    min_grade_point: int = 0


class AnalysisResult(BaseModel):
    """Complete analysis output."""
    # Metadata
    college_name: str = ""
    program: str = ""
    semester: str = ""
    exam_date: str = ""

    # Student data
    students: list[StudentRecord] = Field(default_factory=list)
    total_students: int = 0

    # Overall stats
    class_average_sgpa: float = 0.0
    median_sgpa: float = 0.0
    max_sgpa: float = 0.0
    min_sgpa: float = 0.0
    overall_pass_count: int = 0
    overall_fail_count: int = 0
    pass_percentage: float = 0.0

    # O-grade stats
    total_o_grades: int = 0
    students_with_all_o: int = 0

    # Subject-wise
    subject_stats: list[SubjectStats] = Field(default_factory=list)

    # Brackets
    elite_count: int = 0           # SGPA > 9.0
    distinction_count: int = 0     # 7.5 < SGPA <= 9.0
    first_class_count: int = 0     # 6.5 < SGPA <= 7.5
    second_class_count: int = 0    # 5.0 < SGPA <= 6.5
    below_count: int = 0           # SGPA <= 5.0 (including fails)

    # Toppers
    toppers: list[StudentRecord] = Field(default_factory=list)

    # Grade distribution for charts
    grade_distribution: dict[str, int] = Field(default_factory=dict)


class UploadResponse(BaseModel):
    """API response for PDF upload."""
    success: bool
    message: str
    data: Optional[AnalysisResult] = None
