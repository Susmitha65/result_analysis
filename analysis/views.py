import csv
import os
import pandas as pd
import datetime
from time import sleep
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.conf import settings
from .forms import CSVUploadForm
from .models import CSVFile  # Ensure this matches your actual model import

# @login_required  # Restricts access to logged-in users only
# def csv_upload(request):
#     if request.method == 'POST':
#         form = CSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Save the uploaded file using the ModelForm
#             csv_instance = form.save(commit=False)
#             csv_instance.user = request.user  # Set the current user
#             csv_instance.save()

#             # File path to the uploaded CSV
#             csv_file = csv_instance.file

#             # Ensure the file is a CSV
#             if not csv_file.name.endswith('.csv'):
#                 messages.error(request, 'This is not a valid CSV file.')
#                 return render(request, 'csv_upload.html', {'form': form})

#             try:
#                 print(csv_file.name)
#                 # Open the uploaded CSV file
#                 file_path = csv_file.path  # This provides the full path to the file
#                 with open(file_path, 'r') as file:
#                     # Read the first line (header) using ';' as the delimiter
#                     header_line = file.readline().strip()
#                     headers = header_line.replace('\"', '').split(';')

#                     # Step 2: Read the rest of the file with ',' as the delimiter using chunks
#                     chunks = pd.read_csv(file, delimiter=',', names=headers, skiprows=1, chunksize=1000)
#                     data = pd.concat(chunks, ignore_index=True)

#                 uploaded_data = []
#                 for index, row in data.iterrows():
#                     # Append row data to uploaded_data, matching exact CSV header names
#                     uploaded_data.append({
#                         'Register_No': row['Register No'],  # Match exact header
#                         'Student_Name': row['Student Name'],
#                         'Branch': row['Branch'],
#                         'Semester': row['Semester'],
#                         'Course': row['Course'],
#                         'Exam_Type': row['Exam Type'],
#                         'Attendance': row['Attendance'],
#                         'Withheld': row['Withheld'],
#                         'IMark': row['IMark'],
#                         'Grade': row['Grade'],
#                         'Result': row['Result'],
#                     })

#                 # Convert uploaded data to a DataFrame
#                 df_uploaded_data = pd.DataFrame(uploaded_data)

#                 # Define a unique file path for the Excel file
#                 timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#                 excel_file_path = os.path.join(settings.MEDIA_ROOT, f'Result_Analysis_{request.user.id}_{timestamp}.xlsx')

#                 # Ensure the target directory exists
#                 os.makedirs(os.path.dirname(excel_file_path), exist_ok=True)

#                 # Save the DataFrame to Excel with retry logic
#                 attempt = 0
#                 max_attempts = 3
#                 while attempt < max_attempts:
#                     try:
#                         df_uploaded_data.to_excel(excel_file_path, index=False)
#                         print(f"Data saved to {excel_file_path} successfully!")
#                         break
#                     except Exception as e:
#                         attempt += 1
#                         print(f"Attempt {attempt} failed: {e}")
#                         sleep(1)
#                         if attempt == max_attempts:
#                             raise e

#                 # Pass uploaded_data to the template for display
#                 messages.success(request, 'File uploaded, analyzed, and saved as Excel successfully!')
#                 return render(request, 'csv_upload.html', {
#                     'form': form,
#                     'uploaded_data': uploaded_data,
#                     'excel_file_path': excel_file_path
#                 })

#             except Exception as e:
#                 messages.error(request, f'Error processing file: {str(e)}')
#                 return render(request, 'csv_upload.html', {'form': form})

#     else:
#         form = CSVUploadForm()

#     return render(request, 'csv_upload.html', {'form': form})

import csv
import os
import pandas as pd
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CSVUploadForm
from .models import CSVFile, StudentResult
from django.conf import settings

@login_required  # Restricts access to logged-in users only
def csv_upload(request):
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
                    # messages.success(request, f'{headers}')
                    # Read CSV using chunks for better performance
                    chunks = pd.read_csv(file, delimiter=',', names=headers, skiprows=1, chunksize=1000)
                    data = pd.concat(chunks, ignore_index=True)

                # Create model instances
                created_count = 0
                for index, row in data.iterrows():
                    if pd.isnull(row['Register No']) or pd.isnull(row['Student Name']):
                        # messages.success(request, f'{data}')
                        continue  # Skip rows with missing critical data

                    # Convert 'NaN' values to False for Boolean fields
                    is_withheld = False if pd.isnull(row['Withheld']) else bool(row['Withheld'])
                    is_approved = False if pd.isnull(row['Result']) else bool(row['Result'])
                    is_internal = 0 if pd.isnull(row['IMark']) else row['IMark']
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
                            withheld=is_withheld,  # Make sure NaN is replaced with False
                            internal_marks=is_internal,
                            grade=row['Grade'],
                            result=is_approved  # Make sure NaN is replaced with False
                        )
                        created_count += 1
                    except Exception as e:
                        print(f"Error creating instance: {e}")
                        # messages.success(request, f"{e}")
                        continue

                messages.success(request, f"{created_count} student results created successfully!")
                return render(request, 'csv_upload.html', {'form': form})

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'csv_upload.html', {'form': form})

    else:
        form = CSVUploadForm()

    return render(request, 'csv_upload.html', {'form': form})



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
