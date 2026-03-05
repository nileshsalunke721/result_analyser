import pdfplumber
import pandas as pd
import re


def extract_be(pdf_file):

    students_data = []

    subjects = {
        "414441_INFO_STORAGE_RETRIEVAL": "414441",
        "414442_SOFTWARE_PROJECT_MANAGEMENT": "414442",
        "414443_DEEP_LEARNING": "414443",
        "414444A_MOBILE_COMPUTING": "414444A",
        "414445D_WIRELESS_COMMUNICATION": "414445D",
        "414446_LAB_PRACTICE_III": "414446",
        "414447_LAB_PRACTICE_IV": "414447",
        "414448_PROJECT_STAGE_I": "414448"
    }

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            students = re.split(r"SEAT NO\.:", text)[1:]

            for student in students:

                record = {}

                # Seat No
                record["Seat No"] = student.split()[0]

                # Name
                name = re.search(r"NAME\s*:\s*(.*?)\s*MOTHER", student)
                record["Name"] = name.group(1).strip() if name else ""

                # PRN
                prn = re.search(r"PRN\s*:(\S+)", student)
                record["PRN"] = prn.group(1) if prn else ""

                # SGPA
                sgpa = re.search(r"SGPA1\s*:\s*([\d\.]+|--)", student)

                if sgpa:
                    sgpa_val = sgpa.group(1)
                    if sgpa_val == "--":
                        record["SGPA"] = "ATKT"
                    else:
                        record["SGPA"] = sgpa_val
                else:
                    record["SGPA"] = "ATKT"

                lines = student.split("\n")

                for line in lines:

                    for subject_name, code in subjects.items():

                        if code in line:

                            mark_match = re.search(r"(\d{2,3})/100|(\d{2,3})/025|(\d{2,3})/050", line)

                            if mark_match:
                                mark = [x for x in mark_match.groups() if x][0]
                                record[subject_name] = int(mark)
                            else:
                                record[subject_name] = None

                            grade_match = re.search(r"\s(O|A\+|A|B\+|B|C|P|F|IC)\s", line)

                            if grade_match:
                                record[f"{code}_grade"] = grade_match.group(1)
                            else:
                                record[f"{code}_grade"] = None

                students_data.append(record)

    df = pd.DataFrame(students_data)

    # ✅ Serial Number start from 1
    df.insert(0, "Sr No", range(1, len(df) + 1))

    return df




def generate_analysis(df):

    subjects = {
        "414441_ISR": "414441",
        "414442_SPM": "414442",
        "414443_DL": "414443",
        "414444A_MC": "414444A",
        "414445D_WC": "414445D",
        "414446_LPIII": "414446",
        "414447_LPIV": "414447",
        "414448_PS1": "414448"
    }

    grades = ["O","A+","A","B+","B","C","P","F","IC"]

    analysis = {}

    for label, code in subjects.items():

        col = f"{code}_grade"

        total = len(df)

        counts = {}

        for g in grades:
            counts[g] = (df[col] == g).sum()

        # Fail logic
        fail_students = counts["F"] + counts["IC"]

        pass_students = total - fail_students

        result = round((pass_students / total) * 100, 2)

        analysis[label] = [
            total,
            counts["O"],
            counts["A+"],
            counts["A"],
            counts["B+"],
            counts["B"],
            counts["C"],
            counts["P"],
            counts["F"],
            counts["IC"],
            pass_students,
            result
        ]

    index = [
        "Total No. of Students Present",
        "No. of Students with O Grade",
        "No. of Students with A+ Grade",
        "No. of Students with A Grade",
        "No. of Students with B+ Grade",
        "No. of Students with B Grade",
        "No. of Students with C Grade",
        "No. of Students with P Grade",
        "No. of Students with F Grade",
        "No. of Students with IC Grade",
        "Total No. of Students Pass",
        "% Result"
    ]

    analysis_df = pd.DataFrame(analysis, index=index)

    return analysis_df