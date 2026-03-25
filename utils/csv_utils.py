import csv
from io import StringIO


def attendance_to_csv(records):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student Name", "Email", "Subject", "Date", "Status"])

    for row in records:
        writer.writerow(
            [
                row["student_name"],
                row["student_email"],
                row["subject"],
                row["date"],
                row["status"],
            ]
        )

    return output.getvalue()
