"""
ReportGenerator: PDF report generation module.

Generates a professional summary PDF including:
- Header with college and exam metadata
- Summary statistics table
- Grade distribution charts (bar + pie)
- SGPA bracket distribution
- Top performers list
- Subject-wise breakdown
- All generated in-memory via io.BytesIO — zero disk footprint.
"""

import io
import logging
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from fpdf import FPDF

from models.schemas import AnalysisResult

logger = logging.getLogger(__name__)

# Color palette
COLORS = {
    "O": "#10B981",     # Emerald
    "A+": "#3B82F6",    # Blue
    "A": "#6366F1",     # Indigo
    "B+": "#8B5CF6",    # Violet
    "B": "#F59E0B",     # Amber
    "C": "#EF4444",     # Red
    "P": "#F97316",     # Orange
    "F": "#DC2626",     # Deep red
    "AB": "#6B7280",    # Gray
    "NE": "#9CA3AF",    # Light gray
}

BRACKET_COLORS = {
    "Elite": "#10B981",
    "Distinction": "#3B82F6",
    "First Class": "#F59E0B",
    "Second Class": "#F97316",
    "Below Average": "#EF4444",
}


class ReportGenerator:
    """
    Generates a comprehensive PDF report from analysis results.

    Usage:
        gen = ReportGenerator()
        pdf_bytes = gen.generate(analysis_result)
    """

    def generate(self, result: AnalysisResult) -> bytes:
        """
        Generate a PDF report from analysis results.

        Args:
            result: AnalysisResult containing all computed statistics.

        Returns:
            PDF file content as bytes.
        """
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)

        # Page 1: Summary
        self._add_summary_page(pdf, result)

        # Page 2: Charts
        self._add_charts_page(pdf, result)

        # Page 3: Subject-wise analysis
        self._add_subject_page(pdf, result)

        # Page 4: Toppers
        self._add_toppers_page(pdf, result)

        # Export to bytes
        buffer = io.BytesIO()
        pdf_content = pdf.output()
        buffer.write(pdf_content)
        buffer.seek(0)
        return buffer.read()

    def _add_summary_page(self, pdf: FPDF, result: AnalysisResult):
        """Add the summary statistics page."""
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 12, "Result Analysis Report", ln=True, align="C")

        # Subtitle
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(100, 116, 139)
        if result.college_name:
            pdf.cell(0, 7, result.college_name, ln=True, align="C")
        info_parts = [p for p in [result.program, result.semester, result.exam_date] if p]
        if info_parts:
            pdf.cell(0, 7, " | ".join(info_parts), ln=True, align="C")

        pdf.ln(8)

        # Summary stats in a grid
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "Overview Statistics", ln=True)
        pdf.ln(3)

        stats = [
            ("Total Students", str(result.total_students)),
            ("Class Average SGPA", f"{result.class_average_sgpa:.2f}"),
            ("Median SGPA", f"{result.median_sgpa:.2f}"),
            ("Highest SGPA", f"{result.max_sgpa:.2f}"),
            ("Lowest SGPA", f"{result.min_sgpa:.2f}"),
            ("Pass Rate", f"{result.pass_percentage:.1f}%"),
            ("Total O Grades", str(result.total_o_grades)),
            ("All-O Students", str(result.students_with_all_o)),
        ]

        col_width = 65
        row_height = 8
        pdf.set_font("Helvetica", "", 10)

        for i, (label, value) in enumerate(stats):
            if i % 4 == 0 and i > 0:
                pdf.ln(row_height)

            pdf.set_text_color(100, 116, 139)
            pdf.cell(30, row_height, label + ":", 0, 0)
            pdf.set_text_color(30, 41, 59)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(35, row_height, value, 0, 0)
            pdf.set_font("Helvetica", "", 10)

        pdf.ln(12)

        # SGPA Brackets
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "Performance Brackets", ln=True)
        pdf.ln(3)

        brackets = [
            ("Elite (SGPA > 9.0)", result.elite_count),
            ("Distinction (7.5 - 9.0)", result.distinction_count),
            ("First Class (6.5 - 7.5)", result.first_class_count),
            ("Second Class (5.0 - 6.5)", result.second_class_count),
            ("Below Average (< 5.0)", result.below_count),
        ]

        # Table header
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(80, 8, "Bracket", 1, 0, "C", fill=True)
        pdf.cell(40, 8, "Count", 1, 0, "C", fill=True)
        pdf.cell(50, 8, "Percentage", 1, 1, "C", fill=True)

        pdf.set_font("Helvetica", "", 10)
        for bracket_name, count in brackets:
            pct = f"{(count / result.total_students * 100):.1f}%" if result.total_students > 0 else "0%"
            pdf.cell(80, 7, bracket_name, 1, 0)
            pdf.cell(40, 7, str(count), 1, 0, "C")
            pdf.cell(50, 7, pct, 1, 1, "C")

    def _add_charts_page(self, pdf: FPDF, result: AnalysisResult):
        """Add the charts page with grade distribution and SGPA bars."""
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "Visual Analysis", ln=True, align="C")
        pdf.ln(5)

        # Generate grade distribution bar chart
        grade_chart = self._generate_grade_bar_chart(result)
        if grade_chart:
            pdf.image(grade_chart, x=10, y=30, w=130, h=80)
            grade_chart.close()

        # Generate SGPA bracket pie chart
        bracket_chart = self._generate_bracket_pie_chart(result)
        if bracket_chart:
            pdf.image(bracket_chart, x=150, y=30, w=130, h=80)
            bracket_chart.close()

        # Generate SGPA distribution histogram
        sgpa_hist = self._generate_sgpa_histogram(result)
        if sgpa_hist:
            pdf.image(sgpa_hist, x=40, y=115, w=200, h=75)
            sgpa_hist.close()

    def _add_subject_page(self, pdf: FPDF, result: AnalysisResult):
        """Add subject-wise analysis page."""
        if not result.subject_stats:
            return

        pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "Subject-wise Analysis", ln=True, align="C")
        pdf.ln(5)

        # Table header
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(241, 245, 249)
        headers = ["Subject", "Students", "O", "A+", "A", "B+", "B", "C", "P", "F",
                    "Pass%", "Avg GP"]
        widths = [30, 18, 14, 14, 14, 14, 14, 14, 14, 14, 20, 20]

        for h, w in zip(headers, widths):
            pdf.cell(w, 7, h, 1, 0, "C", fill=True)
        pdf.ln()

        # Table body
        pdf.set_font("Helvetica", "", 8)
        for stat in result.subject_stats:
            row = [
                stat.code,
                str(stat.total_students),
                str(stat.o_grade_count),
                str(stat.a_plus_count),
                str(stat.a_count),
                str(stat.b_plus_count),
                str(stat.b_count),
                str(stat.c_count),
                str(stat.p_count),
                str(stat.f_count),
                f"{stat.pass_percentage:.1f}%",
                f"{stat.avg_grade_point:.1f}",
            ]
            for val, w in zip(row, widths):
                pdf.cell(w, 6, val, 1, 0, "C")
            pdf.ln()

    def _add_toppers_page(self, pdf: FPDF, result: AnalysisResult):
        """Add top performers page."""
        if not result.toppers:
            return

        pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "Top Performers", ln=True, align="C")
        pdf.ln(5)

        # Table
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(15, 8, "Rank", 1, 0, "C", fill=True)
        pdf.cell(40, 8, "USN", 1, 0, "C", fill=True)
        pdf.cell(25, 8, "SGPA", 1, 0, "C", fill=True)
        pdf.cell(25, 8, "CGPA", 1, 0, "C", fill=True)
        pdf.cell(30, 8, "O Grades", 1, 0, "C", fill=True)
        pdf.cell(30, 8, "Bracket", 1, 1, "C", fill=True)

        pdf.set_font("Helvetica", "", 10)
        for i, student in enumerate(result.toppers):
            o_count = sum(1 for s in student.subjects if s.grade == "O")
            pdf.cell(15, 7, str(i + 1), 1, 0, "C")
            pdf.cell(40, 7, student.usn, 1, 0, "C")
            pdf.cell(25, 7, f"{student.sgpa:.2f}", 1, 0, "C")
            pdf.cell(25, 7, f"{student.cgpa:.2f}", 1, 0, "C")
            pdf.cell(30, 7, str(o_count), 1, 0, "C")
            pdf.cell(30, 7, student.bracket, 1, 1, "C")

    # ─── CHART GENERATORS ─────────────────────────────────────────────

    def _generate_grade_bar_chart(self, result: AnalysisResult) -> Optional[io.BytesIO]:
        """Generate grade distribution bar chart."""
        if not result.grade_distribution:
            return None

        try:
            fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
            sns.set_style("whitegrid")

            grades = [g for g in result.grade_distribution if result.grade_distribution[g] > 0]
            counts = [result.grade_distribution[g] for g in grades]
            colors = [COLORS.get(g, "#94A3B8") for g in grades]

            bars = ax.bar(grades, counts, color=colors, edgecolor="white", linewidth=0.5)

            # Add count labels
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                        str(count), ha="center", va="bottom", fontsize=8, fontweight="bold")

            ax.set_title("Grade Distribution", fontsize=12, fontweight="bold", pad=10)
            ax.set_xlabel("Grade", fontsize=9)
            ax.set_ylabel("Count", fontsize=9)
            ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

            plt.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception as e:
            logger.error(f"Failed to generate grade bar chart: {e}")
            return None

    def _generate_bracket_pie_chart(self, result: AnalysisResult) -> Optional[io.BytesIO]:
        """Generate SGPA bracket pie chart."""
        bracket_data = {
            "Elite": result.elite_count,
            "Distinction": result.distinction_count,
            "First Class": result.first_class_count,
            "Second Class": result.second_class_count,
            "Below Avg": result.below_count,
        }

        # Filter zero values
        labels = [k for k, v in bracket_data.items() if v > 0]
        sizes = [bracket_data[k] for k in labels]
        colors = [BRACKET_COLORS.get(k.replace(" Avg", " Average"), "#94A3B8") for k in labels]

        if not sizes:
            return None

        try:
            fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=colors,
                autopct="%1.1f%%", startangle=90,
                textprops={"fontsize": 8}
            )

            for autotext in autotexts:
                autotext.set_fontsize(7)
                autotext.set_color("white")
                autotext.set_fontweight("bold")

            ax.set_title("SGPA Brackets", fontsize=12, fontweight="bold", pad=10)

            plt.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception as e:
            logger.error(f"Failed to generate bracket pie chart: {e}")
            return None

    def _generate_sgpa_histogram(self, result: AnalysisResult) -> Optional[io.BytesIO]:
        """Generate SGPA distribution histogram."""
        sgpas = [s.sgpa for s in result.students if s.sgpa > 0]
        if not sgpas:
            return None

        try:
            fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
            sns.set_style("whitegrid")

            ax.hist(sgpas, bins=20, color="#6366F1", edgecolor="white",
                    linewidth=0.5, alpha=0.85)

            ax.axvline(result.class_average_sgpa, color="#EF4444",
                       linestyle="--", linewidth=1.5,
                       label=f"Average: {result.class_average_sgpa:.2f}")

            ax.set_title("SGPA Distribution", fontsize=12, fontweight="bold", pad=10)
            ax.set_xlabel("SGPA", fontsize=9)
            ax.set_ylabel("Students", fontsize=9)
            ax.legend(fontsize=8)
            ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

            plt.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception as e:
            logger.error(f"Failed to generate SGPA histogram: {e}")
            return None
