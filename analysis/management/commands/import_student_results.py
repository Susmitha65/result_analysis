import csv
from django.core.management.base import BaseCommand
from analysis.models import StudentResult

class Command(BaseCommand):
    help = "Import student results from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                # Specify the delimiter as semicolon and skip unnecessary quotes around headers
                raw_header = csvfile.readline()
                cleaned_header = [h.strip().strip('"') for h in raw_header.strip().split(';')]


                reader = csv.DictReader(csvfile, fieldnames=cleaned_header, delimiter=';', skipinitialspace=True, quoting=csv.QUOTE_NONE)

                # Print the headers to confirm they are correctly read
                headers = reader.fieldnames
                self.stdout.write(self.style.SUCCESS(f"CSV Headers: {headers}"))

                for row in reader:
                    # Print each row to verify data
                    print(row)

                    # Create the student result from the CSV data
                    StudentResult.objects.create(
                        register_no=row['Register No'],
                        student_name=row['Student Name'],
                        branch=row['Branch'],
                        semester=row['Semester'],
                        course=row['Course'],
                        exam_type=row['Exam Type'],
                        attendance=row['Attendance'],
                        withheld=row['Withheld'].lower() == 'true',  # Ensure correct boolean conversion
                        internal_marks=row['IMark'],
                        grade=row['Grade'],
                        result=row['Result']
                    )
            self.stdout.write(self.style.SUCCESS("Data imported successfully!"))
        except Exception as e:
            self.stderr.write(f"Error: {e}")
