"""
AnalysisEngine: Statistical analysis module for student result data.

Takes extracted student records and produces comprehensive statistics
including grade distributions, SGPA brackets, toppers, and subject-wise analysis.
"""

import logging
from collections import Counter

import pandas as pd

from models.schemas import (
    StudentRecord, SubjectStats, AnalysisResult
)

logger = logging.getLogger(__name__)

# SGPA bracket boundaries
BRACKETS = {
    "Elite": (9.0, 10.0),
    "Distinction": (7.5, 9.0),
    "First Class": (6.5, 7.5),
    "Second Class": (5.0, 6.5),
    "Below Average": (0.0, 5.0),
}

PASSING_GRADES = {"O", "A+", "A", "B+", "B", "C", "P"}
ALL_GRADES = ["O", "A+", "A", "B+", "B", "C", "P", "F", "AB", "NE"]


class AnalysisEngine:
    """
    Performs statistical analysis on extracted student records.

    Usage:
        engine = AnalysisEngine()
        result = engine.analyze(metadata, students)
    """

    def analyze(self, metadata: dict, students: list[StudentRecord]) -> AnalysisResult:
        """
        Analyze student records and return comprehensive statistics.

        Args:
            metadata: Dict with college_name, program, semester, exam_date.
            students: List of StudentRecord objects.

        Returns:
            AnalysisResult with all computed statistics.
        """
        if not students:
            return AnalysisResult(**metadata)

        # Build DataFrame for efficient computation
        df = self._build_dataframe(students)

        # Assign performance brackets
        students = self._assign_brackets(students)

        # Compute all stats
        result = AnalysisResult(
            college_name=metadata.get("college_name", ""),
            program=metadata.get("program", ""),
            semester=metadata.get("semester", ""),
            exam_date=metadata.get("exam_date", ""),
            students=students,
            total_students=len(students),
        )

        # SGPA stats — only for students with valid SGPA
        valid_sgpa = df[df["sgpa"] > 0]["sgpa"]
        if not valid_sgpa.empty:
            result.class_average_sgpa = round(float(valid_sgpa.mean()), 2)
            result.median_sgpa = round(float(valid_sgpa.median()), 2)
            result.max_sgpa = round(float(valid_sgpa.max()), 2)
            result.min_sgpa = round(float(valid_sgpa.min()), 2)

        # Pass/Fail
        result.overall_pass_count = int((df["status"] == "P").sum())
        result.overall_fail_count = int((df["status"].isin(["F", "NP", "NE", "AB"])).sum())
        total_valid = result.overall_pass_count + result.overall_fail_count
        result.pass_percentage = round(
            (result.overall_pass_count / total_valid * 100) if total_valid > 0 else 0, 1
        )

        # O-grade analysis
        result.total_o_grades = self._count_total_o_grades(students)
        result.students_with_all_o = self._count_all_o_students(students)

        # Subject-wise stats
        result.subject_stats = self._compute_subject_stats(students)

        # SGPA brackets
        bracket_counts = self._compute_brackets(df)
        result.elite_count = bracket_counts.get("Elite", 0)
        result.distinction_count = bracket_counts.get("Distinction", 0)
        result.first_class_count = bracket_counts.get("First Class", 0)
        result.second_class_count = bracket_counts.get("Second Class", 0)
        result.below_count = bracket_counts.get("Below Average", 0)

        # Toppers (top 5 by SGPA)
        result.toppers = self._find_toppers(students, n=5)

        # Grade distribution
        result.grade_distribution = self._compute_grade_distribution(students)

        return result

    def _build_dataframe(self, students: list[StudentRecord]) -> pd.DataFrame:
        """Convert student records to a Pandas DataFrame."""
        records = []
        for s in students:
            records.append({
                "sl_no": s.sl_no,
                "usn": s.usn,
                "roll_no": s.roll_no,
                "sgpa": s.sgpa,
                "cgpa": s.cgpa,
                "total_credits": s.total_credits,
                "credits_earned": s.credits_earned,
                "status": s.status,
                "num_subjects": len(s.subjects),
                "num_o_grades": sum(1 for sub in s.subjects if sub.grade == "O"),
            })
        return pd.DataFrame(records)

    def _assign_brackets(self, students: list[StudentRecord]) -> list[StudentRecord]:
        """Assign performance brackets based on SGPA."""
        for student in students:
            if student.sgpa <= 0 or student.status in ("NE", "AB", "NP"):
                student.bracket = "N/A"
                continue
            if student.status == "F":
                student.bracket = "Fail"
                continue

            for bracket_name, (low, high) in BRACKETS.items():
                if bracket_name == "Elite" and student.sgpa > low:
                    student.bracket = bracket_name
                    break
                elif bracket_name != "Elite" and low < student.sgpa <= high:
                    student.bracket = bracket_name
                    break
            else:
                student.bracket = "Below Average"

        return students

    def _count_total_o_grades(self, students: list[StudentRecord]) -> int:
        """Count total O grades across all students and subjects."""
        return sum(
            1 for s in students
            for sub in s.subjects
            if sub.grade == "O"
        )

    def _count_all_o_students(self, students: list[StudentRecord]) -> int:
        """Count students with O grade in ALL subjects."""
        count = 0
        for s in students:
            if s.subjects and all(sub.grade == "O" for sub in s.subjects):
                count += 1
        return count

    def _compute_subject_stats(self, students: list[StudentRecord]) -> list[SubjectStats]:
        """Compute statistics per subject."""
        subject_data: dict[str, list[SubjectResult]] = {}

        for s in students:
            for sub in s.subjects:
                if sub.code not in subject_data:
                    subject_data[sub.code] = []
                subject_data[sub.code].append(sub)

        stats = []
        for code, results in subject_data.items():
            grade_counts = Counter(r.grade for r in results)
            gps = [r.grade_point for r in results if r.grade in PASSING_GRADES or r.grade == "F"]

            passing = sum(1 for r in results if r.grade in PASSING_GRADES)
            failing = sum(1 for r in results if r.grade == "F")
            total = len(results)

            stats.append(SubjectStats(
                code=code,
                total_students=total,
                o_grade_count=grade_counts.get("O", 0),
                a_plus_count=grade_counts.get("A+", 0),
                a_count=grade_counts.get("A", 0),
                b_plus_count=grade_counts.get("B+", 0),
                b_count=grade_counts.get("B", 0),
                c_count=grade_counts.get("C", 0),
                p_count=grade_counts.get("P", 0),
                f_count=grade_counts.get("F", 0),
                ab_count=grade_counts.get("AB", 0),
                pass_count=passing,
                fail_count=failing,
                pass_percentage=round((passing / total * 100) if total > 0 else 0, 1),
                avg_grade_point=round(sum(gps) / len(gps), 2) if gps else 0,
                max_grade_point=max(gps) if gps else 0,
                min_grade_point=min(gps) if gps else 0,
            ))

        return sorted(stats, key=lambda s: s.code)

    def _compute_brackets(self, df: pd.DataFrame) -> dict[str, int]:
        """Compute student counts per SGPA bracket."""
        counts = {}
        valid = df[df["sgpa"] > 0]

        counts["Elite"] = int((valid["sgpa"] > 9.0).sum())
        counts["Distinction"] = int(((valid["sgpa"] > 7.5) & (valid["sgpa"] <= 9.0)).sum())
        counts["First Class"] = int(((valid["sgpa"] > 6.5) & (valid["sgpa"] <= 7.5)).sum())
        counts["Second Class"] = int(((valid["sgpa"] > 5.0) & (valid["sgpa"] <= 6.5)).sum())
        counts["Below Average"] = int((valid["sgpa"] <= 5.0).sum())

        return counts

    def _find_toppers(self, students: list[StudentRecord], n: int = 5) -> list[StudentRecord]:
        """Find top N students by SGPA."""
        eligible = [s for s in students if s.sgpa > 0 and s.status == "P"]
        eligible.sort(key=lambda s: s.sgpa, reverse=True)
        return eligible[:n]

    def _compute_grade_distribution(self, students: list[StudentRecord]) -> dict[str, int]:
        """Compute overall grade distribution across all subjects."""
        dist = Counter()
        for s in students:
            for sub in s.subjects:
                dist[sub.grade] += 1

        # Ensure all grades are represented
        return {g: dist.get(g, 0) for g in ALL_GRADES}
