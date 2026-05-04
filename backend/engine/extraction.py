"""
ExtractionEngine: PDF parsing module for university result sheets.

Handles both text-based and image-based (scanned) PDFs.
For scanned PDFs, uses Tesseract OCR with fuzzy pattern matching
to handle OCR errors in USN recognition and grade extraction.
"""

import io
import re
import logging
import os
from typing import Optional

import pdfplumber
import pytesseract
from PIL import Image

from models.schemas import StudentRecord, SubjectResult

logger = logging.getLogger(__name__)

# Configure Tesseract path for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Grade to grade-point mapping
GRADE_MAP = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6,
    "C": 5, "P": 4, "F": 0, "AB": 0, "NE": 0,
}

# Regex patterns
SUBJECT_CODE_PATTERN = re.compile(r"\b(\d{2}[A-Z]{2,5}\d{3})\b")

# Grade patterns that occur in OCR output — grades appear as "O 10 3" or "A+ 9 4" etc.
# Format: GRADE GP CREDITS (or GRADE GP CE BL)
GRADE_TOKEN_RE = re.compile(
    r'(?:^|[\s\(\[\{|;:,])('
    r'O\s+10|'
    r'A\+?\s*\d|'
    r'At\s*[o0]\s*\d|'     # OCR reads A+ as "Ato" or "At9"
    r'B\+?\s*\d|'
    r'Bt?\s*[e+]?\s*\d|'   # OCR reads B+ as "Bt7", "Ber", "B+7", "Be7"
    r'C\s+\d|'
    r'P\s+\d|'
    r'F\s+0|'
    r'AB\s*\d?|'
    r'NE|NP|'
    r'[Ff]\s*[o0O]'         # OCR reads "F 0" as "Fo" sometimes
    r')'
)


class ExtractionEngine:
    """
    Parses university result PDFs and extracts structured student records.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    def parse(self, pdf_bytes: bytes) -> tuple[dict, list[StudentRecord]]:
        """Parse PDF bytes and return metadata + student records."""
        buffer = io.BytesIO(pdf_bytes)
        students = []
        metadata = {"college_name": "", "program": "", "semester": "", "exam_date": ""}

        try:
            with pdfplumber.open(buffer) as pdf:
                first_page = pdf.pages[0]
                has_text = len(first_page.chars) > 20

                if has_text:
                    logger.info("Text-based PDF detected")
                    metadata, students = self._extract_text_based(pdf)
                else:
                    logger.info("Image-based PDF detected, using OCR")
                    metadata, students = self._extract_ocr_based(pdf)

        except Exception as e:
            logger.error(f"PDF parsing error: {e}", exc_info=True)
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        finally:
            buffer.close()

        return metadata, students

    # ─── OCR-BASED EXTRACTION ──────────────────────────────────────

    def _extract_ocr_based(self, pdf) -> tuple[dict, list[StudentRecord]]:
        """Extract data from scanned PDF using OCR."""
        metadata = {"college_name": "", "program": "", "semester": "", "exam_date": ""}
        all_students = []
        subject_codes = []

        for page_idx, page in enumerate(pdf.pages):
            logger.info(f"OCR page {page_idx + 1}/{len(pdf.pages)}")

            img = page.to_image(resolution=300).original
            ocr_text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
            lines = ocr_text.split("\n")

            # Extract metadata from first page
            if page_idx == 0:
                metadata = self._parse_metadata_from_lines(lines)

            # Find subject codes from header
            if not subject_codes:
                for line in lines[:10]:
                    codes = SUBJECT_CODE_PATTERN.findall(line)
                    if len(codes) >= 3:
                        subject_codes = codes
                        break

            # Parse student data lines
            for line in lines:
                line = line.strip()
                if not line or len(line) < 20:
                    continue

                student = self._parse_ocr_student_line(line, subject_codes, len(all_students) + 1)
                if student:
                    all_students.append(student)

            del img

        logger.info(f"Extracted {len(all_students)} students from OCR")
        return metadata, all_students

    def _parse_ocr_student_line(self, line: str, subject_codes: list[str], fallback_sl: int) -> Optional[StudentRecord]:
        """
        Parse a student data line from OCR output.
        
        OCR lines look like (with errors):
        "te zspzcsoot 101 (O to3 (A 8 4 TAtD 3 iA as 1A 83 O11 ... PP oo jars 20 20 ag"
        "17 espeecsooz 202 B+ 7 3 (GC 5s 4 'Ato 3 ..."
        
        Strategy: 
        1. Look for a line starting with a number (sl_no)
        2. Look for a USN-like pattern (digits+letters, ~10-11 chars)
        3. Extract grade+GP pairs using known patterns
        4. Extract SGPA/CGPA from the end
        """
        try:
            # Step 1: Check if line starts with a student serial number
            # OCR sometimes reads digits as letters: "te"→"16", "iv"→"10", "ao"→"40"
            sl_match = re.match(r'\s*(\d{1,3})\s+', line)
            if not sl_match:
                # Try fixing common OCR digit misreads at start of line
                fixed_start = line.lstrip()
                ocr_num_fixes = {
                    'o': '0', 'O': '0', 'D': '0', 
                    'i': '1', 'l': '1', 't': '1', 'I': '1',
                    'z': '2', 'Z': '2',
                    'e': '3', 'E': '3',
                    'a': '4', 'A': '4', 'h': '4',
                    's': '5', 'S': '5',
                    'G': '6', 'b': '6',
                    'T': '7', 'y': '7',
                    'B': '8',
                    'g': '9', 'q': '9', 'p': '9',
                }
                fixed_chars = []
                for ch in fixed_start[:4]:
                    if ch.isalpha() and ch in ocr_num_fixes:
                        fixed_chars.append(ocr_num_fixes[ch])
                    elif ch.isdigit():
                        fixed_chars.append(ch)
                    elif ch == ' ':
                        break
                    else:
                        break
                
                if fixed_chars:
                    fixed_line = ''.join(fixed_chars) + fixed_start[len(fixed_chars):]
                    sl_match = re.match(r'(\d{1,3})\s+', fixed_line)
                    if sl_match:
                        line = fixed_line  # use the fixed line going forward
                
                if not sl_match:
                    return None
            
            sl_no = int(sl_match.group(1))
            remaining = line[sl_match.end():]

            # Step 2: Extract USN-like token (should be ~10-11 chars, alphanumeric)
            # OCR mangles USNs: "2SD24CS001" → "zspzcsoot", "aspascsons", etc.
            usn_match = re.match(r'(\S{8,13})\s+', remaining)
            if not usn_match:
                return None
            
            raw_usn = usn_match.group(1)
            remaining = remaining[usn_match.end():]
            
            # Try to fix the USN using known patterns
            usn = self._fix_usn(raw_usn)
            if not usn:
                return None

            # Step 3: Extract roll number
            roll_match = re.match(r'(\d{2,4})\s+', remaining)
            roll_no = int(roll_match.group(1)) if roll_match else None
            if roll_match:
                remaining = remaining[roll_match.end():]

            # Step 4: Extract grades and grade points
            subjects = self._extract_grades_from_ocr(remaining, subject_codes)

            # Step 5: Extract SGPA, total, earned, CGPA from end of line
            sgpa, cgpa, total_credits, credits_earned = self._extract_tail_numbers(line)

            # Step 6: Determine status
            status = "P"
            if re.search(r'\bNP\b', line):
                status = "NP"
            elif re.search(r'\bNE\b', line) and not any(s.grade in ("O","A+","A","B+","B","C","P") for s in subjects):
                status = "NE"
            elif any(s.grade == "F" for s in subjects):
                status = "F"

            return StudentRecord(
                sl_no=sl_no,
                usn=usn,
                roll_no=roll_no,
                subjects=subjects,
                sgpa=sgpa,
                cgpa=cgpa,
                total_credits=total_credits,
                credits_earned=credits_earned,
                status=status,
            )

        except Exception as e:
            logger.debug(f"Failed to parse line: {e}")
            return None

    def _fix_usn(self, raw: str) -> Optional[str]:
        """
        Fix an OCR-mangled USN to the correct format.
        
        VTU USN format: XYYZZWWWNNN (10-11 chars)
        Where X=digit, YY=2 letters, ZZ=2 digits, WWW=2-3 letters, NNN=3 digits
        Example: 2SD22CS001
        
        This method is intentionally very lenient — it's better to accept a
        slightly wrong USN than miss an entire student record.
        """
        raw = raw.strip().rstrip('|').rstrip(':').strip()
        
        # Remove any non-alphanumeric chars
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', raw)
        
        if len(cleaned) < 8 or len(cleaned) > 14:
            return None
        
        # If it already matches the correct pattern, return uppercase
        strict = re.match(r'^(\d[A-Z]{2}\d{2}[A-Z]{2,3}\d{3})$', cleaned.upper())
        if strict:
            return strict.group(1).upper()
        
        # Comprehensive OCR character mappings
        # For positions that should be DIGITS:
        char_to_digit = {
            'o': '0', 'O': '0', 'D': '0', 'Q': '0',
            'i': '1', 'I': '1', 'l': '1', 'L': '1', 't': '1', '|': '1',
            'z': '2', 'Z': '2',
            'E': '3', 'e': '3', 'B': '8',
            'A': '4', 'a': '4', 'h': '4',
            's': '5', 'S': '5',
            'G': '6', 'b': '6',
            'T': '7', 'y': '7', 'Y': '7',
            'g': '9', 'q': '9', 'p': '9',
            'n': '7',  # OCR sometimes reads 7 as n
        }
        
        # For positions that should be LETTERS:
        digit_to_letter = {
            '0': 'O', '5': 'S', '1': 'I', '2': 'Z',
            '8': 'B', '6': 'G', '9': 'G',
        }
        
        # Position-aware fixing for VTU USN: D LL DD LL(L) DDD
        chars = list(cleaned)
        
        # Pos 0: DIGIT
        if chars[0].isalpha():
            chars[0] = char_to_digit.get(chars[0], '2')  # default to '2' for VTU
        
        # Pos 1-2: LETTERS
        for i in [1, 2]:
            if i < len(chars):
                if chars[i].isdigit():
                    chars[i] = digit_to_letter.get(chars[i], chars[i])
                chars[i] = chars[i].upper()
        
        # Pos 3-4: DIGITS (year)
        for i in [3, 4]:
            if i < len(chars):
                if chars[i].isalpha():
                    chars[i] = char_to_digit.get(chars[i], '2')
        
        # Determine dept length (2 or 3 letters)
        # Standard VTU depts: CS, IS, EC, ME, CV, EE, etc. (2 chars)
        # Some have 3: CSE, ISE, ECE
        remaining_len = len(chars) - 5  # after pos 0-4
        dept_len = 3 if remaining_len >= 6 else 2
        
        # Pos 5 to 5+dept_len-1: LETTERS (department)
        for i in range(5, min(5 + dept_len, len(chars))):
            if chars[i].isdigit():
                chars[i] = digit_to_letter.get(chars[i], chars[i])
            chars[i] = chars[i].upper()
        
        # Remaining positions: DIGITS (roll number, typically 3)
        digit_start = 5 + dept_len
        for i in range(digit_start, len(chars)):
            if chars[i].isalpha():
                chars[i] = char_to_digit.get(chars[i], '0')
        
        fixed = "".join(chars)
        
        # Validate
        if re.match(r'^\d[A-Z]{2}\d{2}[A-Z]{2,3}\d{2,4}$', fixed):
            # Pad roll number to 3 digits if needed
            m = re.match(r'^(\d[A-Z]{2}\d{2}[A-Z]{2,3})(\d+)$', fixed)
            if m:
                prefix = m.group(1)
                num = m.group(2).zfill(3)[-3:]  # take last 3 digits
                return prefix + num
            return fixed
        
        # LENIENT FALLBACK: If we can't fix it perfectly, still accept it
        # as long as it looks roughly like a USN (8+ alphanumeric chars
        # starting with a digit or common OCR-for-digit)
        # Use the best-effort fixed version
        if len(cleaned) >= 8:
            # Generate a best-effort USN
            fallback = cleaned.upper()
            # At minimum, try to fix the first char to a digit
            if fallback[0].isalpha():
                fallback = char_to_digit.get(cleaned[0], '2') + fallback[1:]
            
            # Accept it — imperfect USN is better than no student record
            return fallback[:12]  # cap length
        
        return None

    def _extract_grades_from_ocr(self, text: str, subject_codes: list[str]) -> list[SubjectResult]:
        """
        Extract grade/GP pairs from OCR text.
        
        OCR patterns for grades:
        - "O 10 3"  → Grade O, GP 10, Credits 3
        - "A+ 9 4" or "Ato 3" or "At9 3" → Grade A+, GP 9
        - "B+ 7 3" or "Bt7 3" or "Ber 3" → Grade B+, GP 7
        - "A 8 3" → Grade A, GP 8
        - "F 0" or "Fo" → Grade F, GP 0
        - "AB 0" or "ABo" → Grade AB, GP 0
        """
        subjects = []
        
        # Normalize common OCR artifacts
        text = text.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
        text = text.replace('|', ' ').replace(';', ' ').replace("'", '').replace('"', '')
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Pattern: Grade GradePoint (optional Credits)
        # Matching real OCR patterns observed:
        # "O 10 3", "O to3", "O103"
        # "A 8 4", "A 8 3"  
        # "At9 3", "Ato 3", "A+ 9 3", "AtD 3"
        # "B+ 7 3", "Bt7 3", "Be7 3", "Ber 3", "B+7 3"
        # "B 6 3", "B63"
        # "C 5 3", "C53"
        # "P 4 3", "P43", "P 4 2"
        # "F 0", "Fo", "F o"
        # "AB 0", "ABo", "AB o"
        # "NE"
        
        grade_patterns = [
            # (regex, grade, gp)
            # === O grade (GP=10) ===
            (r'O\s*1[o0]\s*\d?', 'O', 10),
            (r'O\s*[wm]\s*\d?', 'O', 10),       # "Ow1", "Om1" — OCR for "O 10 1"
            (r'[0O]\s+1[0o]\s*\d?', 'O', 10),
            (r'O\s*t[o0]\s*\d?', 'O', 10),       # "O to3" — OCR for "O 10 3"
            (r'[Oo][0O1]\s*\d?', 'O', 10),       # "O1", "O01"
            (r'(?:i|f)?O\s*[14w]\s*\d?', 'O', 10),  # "iOwi", "fOw1", "iO 1"
            (r'TO\s*1[0o]\s*\d?', 'O', 10),      # "TO 101" — OCR for "O 10 1"
            (r'SO\s*\d', 'O', 10),                # "SO 3" — OCR for "O 10 3"
            (r'o[12]\s*[14]', 'O', 10),           # "o21" — OCR for "O ? 1"
            # === A+ grade (GP=9) ===
            (r'A[t+][o0D9]\s*\d?', 'A+', 9),     # "Ato", "At9", "AtD" → A+
            (r'A\+\s*9\s*\d?', 'A+', 9),
            (r'At\s+[o0D9a]\s*\d?', 'A+', 9),    # "At 9 3", "At o 3"
            (r'A[rt]\s*\d\s*\d?', 'A+', 9),      # "Ar9", "At9"
            (r'(?:i|f)?At[oa]\s*\d?', 'A+', 9),  # "iAto", "fAto" 
            (r'Atrod', 'A+', 9),                  # "Atrod" — OCR artifact for A+
            (r'Asi', 'A+', 9),                    # "Asi" — OCR for A+
            (r'Aad', 'A+', 9),                    # "Aad" — OCR for A+ 
            (r'Arod', 'A+', 9),                   # "Arod" — OCR for A+
            # === A grade (GP=8) ===
            (r'A\s+[8B]\s*\d?', 'A', 8),          # "A 8 3", "A 8 4"
            (r'(?:i|1)?A\s+[a4]\s*[s5]?', 'A', 8),  # "iA as" — OCR for "A 8"
            (r'A[8B]\s*\d', 'A', 8),              # "A83", "A84"
            (r'A\s*B\s*1\s*4?', 'A', 8),          # "A B14" — OCR for "A 8 1 4"
            # === B+ grade (GP=7) ===
            (r'B\+\s*7\s*\d?', 'B+', 7),
            (r'B[t+][e+]?\s*7\s*\d?', 'B+', 7),  # "Bt7", "B+7", "Bte7"
            (r'B[oe]?\s*[r7]\s*\d?', 'B+', 7),   # "Ber", "Bo7", "B7"
            (r'B[Ee]?\s*[t7]\s*\d?', 'B+', 7),   # "Bet", "Be7"
            (r'(?:i|f)?B[+t]?\s*7\s*\d?', 'B+', 7),  # "iBt7", "iB+7"
            (r'Bea', 'B+', 7),                    # "Bea" — OCR for B+
            (r'Pada', 'P', 4),                    # "Pada" — OCR for P 4 
            # === B grade (GP=6) ===
            (r'B\s+6\s*\d?', 'B', 6),
            (r'B\s*6\s*\d', 'B', 6),              # "B63"
            (r'(?:i|f)?B\s+6\s*\d?', 'B', 6),
            # === C grade (GP=5) ===
            (r'[CG][CG]?\s*5\s*[s5]?\s*\d?', 'C', 5),  # "C 5 3", "C53", "GC 5s 4"
            (r'(?:i|f)?C\s*5\s*\d?', 'C', 5),
            # === P grade (GP=4) ===
            (r'P\s*4\s*[2-4]?\s*\d?', 'P', 4),    # "P 4 3", "P43", "P 4 2"
            (r'P\s+[42]\s', 'P', 4),
            (r'(?:i|f)?P\s*4\s*\d?', 'P', 4),
            (r'Pa[d24]\s*\d?', 'P', 4),           # "Pad4", "Pa2" — OCR for P 4
            (r'Paa\s*[xXy]?', 'P', 4),            # "Paax" — OCR for P 4
            # === F grade (GP=0) ===
            (r'F\s*[o0O]\s*[yY]?', 'F', 0),       # "F 0", "Fo", "F o", "F o Y"
            (r'F\s+0', 'F', 0),
            (r'(?:i|f|3)?F\s*[o0]\s*[yY]?', 'F', 0),  # "iF 0", "3F 0"
            # === AB grade (GP=0) ===
            (r'AB\s*[o0]?\s*[yY6]?', 'AB', 0),    # "AB 0", "ABo", "AB o Y"
            (r'(?:i|f)?AB\s*[o0]?\s*[yY]?', 'AB', 0),
            # === NE grade ===
            (r'\bNE\b', 'NE', 0),
            (r'ink\b', 'NE', 0),                   # OCR for NE
            (r'iNE\b', 'NE', 0),
            # === PP/Status markers (skip these) ===
        ]
        
        pos = 0
        while pos < len(text):
            best_match = None
            best_end = pos
            best_grade = None
            best_gp = None
            
            for pattern, grade, gp in grade_patterns:
                m = re.match(pattern, text[pos:], re.IGNORECASE if grade not in ('O', 'A', 'B', 'C', 'P', 'F') else 0)
                if m:
                    if best_match is None or m.end() > best_end - pos:
                        best_match = m
                        best_end = pos + m.end()
                        best_grade = grade
                        best_gp = gp
            
            if best_match:
                code = subject_codes[len(subjects)] if len(subjects) < len(subject_codes) else f"SUB{len(subjects)+1:02d}"
                subjects.append(SubjectResult(
                    code=code,
                    grade=best_grade,
                    grade_point=best_gp,
                ))
                pos = best_end
            else:
                pos += 1
        
        return subjects

    def _extract_tail_numbers(self, line: str) -> tuple[float, float, int, int]:
        """Extract SGPA, CGPA, total credits, earned credits from end of line."""
        sgpa = 0.0
        cgpa = 0.0
        total_credits = 0
        credits_earned = 0

        # Find decimal numbers (SGPA/CGPA candidates)
        # OCR sometimes reads "8.9" as "ag", "89", etc.
        # Look for patterns like X.XX or X XX (with space instead of dot)
        decimals = re.findall(r'(\d+\.\d{1,2})', line)
        
        if len(decimals) >= 2:
            # Usually the last two decimals are SGPA and CGPA
            try:
                val1 = float(decimals[-2])
                val2 = float(decimals[-1])
                if 0 < val1 <= 10:
                    sgpa = val1
                if 0 < val2 <= 10:
                    cgpa = val2
            except ValueError:
                pass
        elif len(decimals) == 1:
            try:
                val = float(decimals[0])
                if 0 < val <= 10:
                    sgpa = val
            except ValueError:
                pass

        # Find credit numbers (integers 15-30 range, near end of line)
        tail = line[-40:] if len(line) > 40 else line
        credit_nums = re.findall(r'\b(\d{2})\b', tail)
        credit_vals = [int(n) for n in credit_nums if 10 <= int(n) <= 30]
        
        if len(credit_vals) >= 2:
            total_credits = credit_vals[-2]
            credits_earned = credit_vals[-1]
        elif len(credit_vals) == 1:
            total_credits = credit_vals[0]
            credits_earned = credit_vals[0]

        return sgpa, cgpa, total_credits, credits_earned

    # ─── TEXT-BASED EXTRACTION ─────────────────────────────────────

    def _extract_text_based(self, pdf) -> tuple[dict, list[StudentRecord]]:
        """Extract from text-based PDF using pdfplumber word extraction."""
        metadata = {"college_name": "", "program": "", "semester": "", "exam_date": ""}
        all_students = []
        subject_codes = []

        for page_idx, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                continue

            words.sort(key=lambda w: (round(w["top"], 0), w["x0"]))
            lines = self._group_words_into_lines(words)

            if page_idx == 0:
                for line_words in lines[:15]:
                    line_text = " ".join(w["text"] for w in line_words)
                    self._match_metadata(line_text, metadata)

            if not subject_codes:
                for line_words in lines[:10]:
                    line_text = " ".join(w["text"] for w in line_words)
                    codes = SUBJECT_CODE_PATTERN.findall(line_text)
                    if len(codes) >= 3:
                        subject_codes = codes
                        break

            for line_words in lines:
                line_text = " ".join(w["text"] for w in line_words)
                student = self._parse_ocr_student_line(line_text, subject_codes, len(all_students) + 1)
                if student:
                    all_students.append(student)

        return metadata, all_students

    def _group_words_into_lines(self, words, tolerance=5.0):
        if not words:
            return []
        lines = []
        current_line = [words[0]]
        current_y = words[0]["top"]
        for w in words[1:]:
            if abs(w["top"] - current_y) <= tolerance:
                current_line.append(w)
            else:
                lines.append(sorted(current_line, key=lambda x: x["x0"]))
                current_line = [w]
                current_y = w["top"]
        if current_line:
            lines.append(sorted(current_line, key=lambda x: x["x0"]))
        return lines

    # ─── METADATA PARSING ─────────────────────────────────────────

    def _parse_metadata_from_lines(self, lines) -> dict:
        meta = {"college_name": "", "program": "", "semester": "", "exam_date": ""}
        for line in lines[:15]:
            line = line.strip()
            if line:
                self._match_metadata(line, meta)
        return meta

    def _match_metadata(self, line: str, meta: dict):
        upper = line.upper()
        if ("COLLEGE" in upper or "INSTITUTE" in upper) and not meta["college_name"]:
            meta["college_name"] = line.strip()
        elif "PROGRAM" in upper or "B.E" in upper:
            m = re.search(r'Program\s*[:\-]\s*(.*)', line, re.I)
            meta["program"] = m.group(1).strip() if m else line.strip()
        elif "EXAM" in upper or "SEMESTER END" in upper:
            m = re.search(r'Exam\s*[:\-]\s*(.*)', line, re.I)
            meta["semester"] = m.group(1).strip() if m else line.strip()
        elif "DATE" in upper:
            m = re.search(r'Date\s*[:\-]\s*([\d\-/\.]+)', line, re.I)
            if m:
                meta["exam_date"] = m.group(1).strip()
