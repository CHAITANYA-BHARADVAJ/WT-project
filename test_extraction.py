"""Test the improved extraction engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from engine.extraction import ExtractionEngine

with open("CS - III Semester_SEE_Results Jan 2026.pdf", "rb") as f:
    pdf_bytes = f.read()

engine = ExtractionEngine()
metadata, students = engine.parse(pdf_bytes)

print("=== METADATA ===")
for k, v in metadata.items():
    print(f"  {k}: {v}")

print(f"\n=== STUDENTS ({len(students)}) ===")
for s in students[:10]:
    grades = ", ".join(f"{sub.grade}({sub.grade_point})" for sub in s.subjects)
    print(f"  #{s.sl_no:3d} {s.usn:<14s} SGPA={s.sgpa:.2f} Status={s.status} [{len(s.subjects)} subj] {grades[:80]}")

print(f"\n=== STATS ===")
print(f"Total: {len(students)}")
sgpas = [s.sgpa for s in students if s.sgpa > 0]
subj_counts = [len(s.subjects) for s in students]
print(f"Pass: {sum(1 for s in students if s.status=='P')}, Fail: {sum(1 for s in students if s.status in ('F','NP'))}")
if sgpas:
    print(f"SGPA: avg={sum(sgpas)/len(sgpas):.2f}, max={max(sgpas):.2f}, min={min(sgpas):.2f}")
print(f"Subjects per student: avg={sum(subj_counts)/len(subj_counts):.1f}, max={max(subj_counts)}, min={min(subj_counts)}")
print(f"Students with 0 subjects: {sum(1 for c in subj_counts if c == 0)}")
print(f"Students with 5+ subjects: {sum(1 for c in subj_counts if c >= 5)}")
