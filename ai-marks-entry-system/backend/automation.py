import requests
from playwright.sync_api import sync_playwright


PORTAL_URL = "http://localhost:9000"

API_URL = "http://127.0.0.1:8000/api/confirmed-marks"

MARKS_FILE = r"C:\Users\rawat\OneDrive\Desktop\marks.xlsx"


def get_confirmed_marks():

    print("Fetching confirmed marks from FastAPI...")

    response = requests.get(API_URL)

    if response.status_code != 200:
        raise Exception(
            "Could not fetch confirmed marks."
        )

    data = response.json()

    if not data.get("success"):
        raise Exception(
            "FastAPI did not return successful data."
        )

    records = data.get("records", [])

    if not records:
        raise Exception(
            "No confirmed marks available."
        )

    print(
        f"Received {len(records)} confirmed records."
    )

    return records


def automate_marks_entry():

    # --------------------------------
    # GET CONFIRMED DATA
    # --------------------------------

    records = get_confirmed_marks()

    print("\nConfirmed Marks:")

    for student in records:

        print(
            f"{student['enrollment_no']} | "
            f"{student['name']} | "
            f"{student['marks']}"
        )


    # --------------------------------
    # START PLAYWRIGHT
    # --------------------------------

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        page = browser.new_page()

        print(
            "\nOpening examination portal..."
        )

        page.goto(PORTAL_URL)


        # --------------------------------
        # LOGIN
        # --------------------------------

        print("Logging in...")

        page.fill(
            "#username",
            "faculty"
        )

        page.fill(
            "#password",
            "demo123"
        )

        page.click(
            "button:has-text('Login')"
        )


        # --------------------------------
        # SELECT COURSE
        # --------------------------------

        print(
            "Selecting ARM210..."
        )

        page.select_option(
            "#course",
            "ARM210"
        )


        # --------------------------------
        # INJECT CONFIRMED DATA
        # --------------------------------

        print(
            "Sending confirmed marks to portal..."
        )

        page.evaluate(
            """
            (records) => {
                window.confirmedMarks = records;
            }
            """,
            records
        )


        # --------------------------------
        # SELECT FILE
        # --------------------------------

        print(
            "Selecting marks file..."
        )

        page.set_input_files(
            "#marksFile",
            MARKS_FILE
        )


        # --------------------------------
        # IMPORT
        # --------------------------------

        page.click(
            "button:has-text('Import Marks')"
        )


        # --------------------------------
        # WAIT FOR TABLE
        # --------------------------------

        page.wait_for_selector(
            "#studentCard:not(.hidden)"
        )

        print(
            "Student table loaded."
        )


        rows = page.locator(
            "#studentTable tr"
        )

        print(
            f"Portal contains "
            f"{rows.count()} students."
        )


        # --------------------------------
        # VERIFY ENROLLMENTS + MARKS
        # --------------------------------

        for student in records:

            enrollment = str(
                student["enrollment_no"]
            )

            marks = str(
                student["marks"]
            )

            row = page.locator(
                "#studentTable tr"
            ).filter(
                has_text=enrollment
            )


            if row.count() == 0:

                raise Exception(
                    f"Student {enrollment} "
                    f"not found in portal."
                )


            marks_input = row.locator(
                "input.marks-input"
            )


            portal_marks = (
                marks_input
                .input_value()
                .strip()
            )


            print(
                f"{enrollment}: "
                f"expected={marks}, "
                f"portal={portal_marks}"
            )


            if portal_marks != marks:

                raise Exception(
                    f"Marks mismatch for "
                    f"{enrollment}"
                )


        print(
            "\n✓ All confirmed marks "
            "verified in portal."
        )


        # --------------------------------
        # SUBMIT
        # --------------------------------

        print(
            "Submitting marks..."
        )

        page.click(
            "#submitButton"
        )


        page.wait_for_selector(
            "#successMessage",
            state="visible"
        )


        print(
            "\n================================"
        )

        print(
            "✓ MARKS SUBMITTED SUCCESSFULLY"
        )

        print(
            "================================"
        )


        # Keep browser open for demo
        page.wait_for_timeout(
            30000
        )


        browser.close()


if __name__ == "__main__":

    automate_marks_entry()