import csv
import os
import glob
import pandas as pd
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.conf import settings
from .forms import CSVUploadForm
from .models import CSVFile, StudentResult

@login_required  # Restricts access to logged-in users only
def csv_upload(request):
    uploaded_data = None  # Store uploaded data for display

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded file using the ModelForm
            csv_instance = form.save(commit=False)
            csv_instance.user = request.user  # Set the current user
            csv_instance.save()

            # File path to the uploaded CSV
            csv_file = csv_instance.file

            # Ensure the file is a CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a valid CSV file.')
                return render(request, 'csv_upload.html', {'form': form})

            try:
                # Process the CSV
                file_path = csv_file.path  # Full path to the file
                with open(file_path, 'r') as file:
                    header_line = file.readline().strip()
                    headers = header_line.replace('"', '').split(';')

                    # Read CSV using chunks for better performance
                    chunks = pd.read_csv(file, delimiter=',', names=headers, skiprows=1, chunksize=1000)
                    data = pd.concat(chunks, ignore_index=True)

                uploaded_data = []
                created_count = 0

                for index, row in data.iterrows():
                    if pd.isnull(row['Register No']) or pd.isnull(row['Student Name']):
                        continue  # Skip rows with missing critical data

                    # Convert 'NaN' values to False for Boolean fields
                    is_withheld = False if pd.isnull(row['Withheld']) else bool(row['Withheld'])
                    is_approved = False if pd.isnull(row['Result']) else bool(row['Result'])
                    is_internal = 0 if pd.isnull(row['IMark']) else row['IMark']

                    # Append row data to display in the template
                    uploaded_data.append({
                        'Register_No': row['Register No'],
                        'Student_Name': row['Student Name'],
                        'Branch': row['Branch'],
                        'Semester': row['Semester'],
                        'Course': row['Course'],
                        'Exam_Type': row['Exam Type'],
                        'Attendance': row['Attendance'],
                        'Withheld': is_withheld,
                        'IMark': is_internal,
                        'Grade': row['Grade'],
                        'Result': is_approved,
                    })

                    try:
                        StudentResult.objects.create(
                            csv_file=csv_instance,
                            register_no=row['Register No'],
                            student_name=row['Student Name'],
                            branch=row['Branch'],
                            semester=row['Semester'],
                            course=row['Course'],
                            exam_type=row['Exam Type'],
                            attendance=row['Attendance'],
                            withheld=is_withheld,
                            internal_marks=is_internal,
                            grade=row['Grade'],
                            result=is_approved
                        )
                        created_count += 1
                    except Exception as e:
                        print(f"Error creating instance: {e}")
                        continue

                messages.success(request, f"{created_count} student results created successfully!")

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'csv_upload.html', {'form': form})

    else:
        form = CSVUploadForm()

    return render(request, 'csv_upload.html', {'form': form, 'uploaded_data': uploaded_data})


@login_required
def download_excel(request):
    # Generate the file path dynamically based on user ID and latest timestamp
    excel_file_path = os.path.join(settings.MEDIA_ROOT, f'Result_Analysis_{request.user.id}_*.xlsx')
    files = sorted(glob.glob(excel_file_path), reverse=True)  # Find the latest file for the user

    if files:
        latest_file = files[0]
        return FileResponse(
            open(latest_file, 'rb'),
            as_attachment=True,
            filename=os.path.basename(latest_file)
        )
    else:
        messages.error(request, "No Excel file exists for download.")
        return render(request, 'csv_upload.html', {'form': CSVUploadForm()})
