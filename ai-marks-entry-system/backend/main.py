from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import subprocess
import sys
import os

app = FastAPI(
    title="AI Marks Entry System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# REGISTERED STUDENTS
# --------------------------------------------------

students = [
    {
        "enrollment_no": "202300101",
        "name": "Rahul Sharma",
        "marks": 24
    },
    {
        "enrollment_no": "202300102",
        "name": "Priya Singh",
        "marks": 27
    },
    {
        "enrollment_no": "202300103",
        "name": "Aman Kumar",
        "marks": 19
    },
    {
        "enrollment_no": "202300104",
        "name": "Neha Gupta",
        "marks": 25
    }
]


# --------------------------------------------------
# BASIC ROUTES
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Marks Entry System API is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/students")
def get_students():
    return students


# --------------------------------------------------
# EXCEL UPLOAD + VALIDATION
# --------------------------------------------------

@app.post("/api/upload")
async def upload_marks(file: UploadFile = File(...)):

    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not read Excel file: {str(e)}"
        }

    required_columns = {
        "Enrollment No.",
        "Student Name",
        "Marks"
    }

    # Check required columns
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        return {
            "success": False,
            "error": "Missing required columns",
            "missing_columns": list(missing_columns)
        }

    # Find duplicate enrollment numbers
    duplicate_enrollments = (
        df[
            df["Enrollment No."].duplicated(keep=False)
        ]["Enrollment No."]
        .astype(str)
        .unique()
        .tolist()
    )

    # Registered enrollment numbers
    registered_enrollments = {
        str(student["enrollment_no"])
        for student in students
    }

    records = []

    for index, row in df.iterrows():

        enrollment = str(row["Enrollment No."]).strip()
        name = str(row["Student Name"]).strip()
        marks = row["Marks"]

        issues = []

        # ------------------------------------------
        # MISSING ENROLLMENT
        # ------------------------------------------

        if (
            pd.isna(row["Enrollment No."])
            or enrollment == ""
            or enrollment == "nan"
        ):
            issues.append("MISSING ENROLLMENT")

        # ------------------------------------------
        # MISSING NAME
        # ------------------------------------------

        if (
            pd.isna(row["Student Name"])
            or name == ""
            or name == "nan"
        ):
            issues.append("MISSING NAME")

        # ------------------------------------------
        # MISSING MARKS
        # ------------------------------------------

        if pd.isna(marks) or str(marks).strip() == "":
            issues.append("MISSING MARKS")

        # ------------------------------------------
        # INVALID MARKS
        # Valid range = 0 to 40
        # ------------------------------------------

        if not pd.isna(marks):

            try:
                numeric_marks = float(marks)

                if numeric_marks < 0 or numeric_marks > 40:
                    issues.append("INVALID MARKS")

            except (ValueError, TypeError):
                issues.append("INVALID MARKS")

        # ------------------------------------------
        # DUPLICATE ENROLLMENT
        # ------------------------------------------

        if enrollment in duplicate_enrollments:
            issues.append("DUPLICATE")

        # ------------------------------------------
        # ENROLLMENT MATCHING
        # ------------------------------------------

        if enrollment not in registered_enrollments:
            issues.append("UNMATCHED")

        # ------------------------------------------
        # DETERMINE STATUS
        # ------------------------------------------

        if "MISSING MARKS" in issues:
            status = "MISSING MARKS"

        elif "INVALID MARKS" in issues:
            status = "INVALID MARKS"

        elif "DUPLICATE" in issues:
            status = "DUPLICATE"

        elif "UNMATCHED" in issues:
            status = "UNMATCHED"

        elif issues:
            status = "REVIEW"

        else:
            status = "MATCHED"

        # ------------------------------------------
        # ADD RECORD
        # ------------------------------------------

        records.append({
            "row": index + 2,
            "enrollment_no": enrollment,
            "name": name,
            "marks": "" if pd.isna(marks) else marks,
            "status": status,
            "issues": issues
        })

    # ------------------------------------------
    # SUMMARY COUNTS
    # ------------------------------------------

    matched_count = sum(
        1
        for record in records
        if record["status"] == "MATCHED"
    )

    review_count = sum(
        1
        for record in records
        if record["status"] != "MATCHED"
    )

    unmatched_count = sum(
        1
        for record in records
        if record["status"] == "UNMATCHED"
    )

    return {
        "success": True,
        "filename": file.filename,
        "total_records": len(records),
        "matched": matched_count,
        "review": review_count,
        "unmatched": unmatched_count,
        "records": records
    }


# --------------------------------------------------
# CONFIRM MARKS
# --------------------------------------------------

confirmed_marks = []


@app.post("/api/confirm")
async def confirm_marks(data: dict):

    global confirmed_marks

    records = data.get("records", [])

    # Only completely valid records can be confirmed
    invalid_records = [
        record
        for record in records
        if record.get("status") != "MATCHED"
    ]

    if invalid_records:

        return {
            "success": False,
            "message": "Cannot confirm records requiring review.",
            "invalid_count": len(invalid_records)
        }

    confirmed_marks = records

    return {
        "success": True,
        "message": "Marks confirmed successfully.",
        "total_records": len(confirmed_marks)
    }


# --------------------------------------------------
# GET CONFIRMED MARKS
# --------------------------------------------------

@app.get("/api/confirmed-marks")
async def get_confirmed_marks():

    return {
        "success": True,
        "records": confirmed_marks
    }


# --------------------------------------------------
# START AUTOMATION
# --------------------------------------------------

@app.post("/api/submit")
async def submit_confirmed_marks():

    global confirmed_marks

    if not confirmed_marks:

        return {
            "success": False,
            "message": "No confirmed marks available."
        }

    try:

        automation_path = os.path.join(
            os.path.dirname(__file__),
            "automation.py"
        )

        if not os.path.exists(automation_path):

            return {
                "success": False,
                "message": "automation.py was not found."
            }

        process = subprocess.Popen(
            [sys.executable, automation_path]
        )

        return {
            "success": True,
            "message": "Marks submission automation started.",
            "total_records": len(confirmed_marks),
            "process_id": process.pid
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Failed to start automation: {str(e)}"
        }