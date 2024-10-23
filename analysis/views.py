import csv
import os
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CSVUploadForm
from .models import CSVFile  # Ensure you have the correct import for your model
from django.conf import settings
from django.http import HttpResponse

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
                print(csv_file.name)
                # Open the uploaded CSV file
                file_path = csv_file.path  # This provides the full path to the file
                with open(file_path, 'r') as file:
                    # Read the first line (header) using ';' as the delimiter
                    header_line = file.readline().strip()
                    headers = header_line.replace('\"', '').split(';')

                    # Step 2: Read the rest of the file with ',' as the delimiter
                    data = pd.read_csv(file, delimiter=',', names=headers, skiprows=1)

                uploaded_data = []
                for index, row in data.iterrows():
                    print("row ", row['Semester'])
                    # Append row data to uploaded_data, matching exact CSV header names
                    uploaded_data.append({
                        'Register_No': row['Register No'],  # Match exact header
                        'Student_Name': row['Student Name'],
                        'Branch': row['Branch'],
                        'Semester': row['Semester'],
                        'Course': row['Course'],
                        'Exam_Type': row['Exam Type'],
                        'Attendance': row['Attendance'],
                        'Withheld': row['Withheld'],
                        'IMark': row['IMark'],
                        'Grade': row['Grade'],
                        'Result': row['Result'],
                    })

                # Convert uploaded data to a DataFrame
                df_uploaded_data = pd.DataFrame(uploaded_data)

                # Define the Excel file path where the data will be saved
                excel_file_path = os.path.join(settings.MEDIA_ROOT, 'Result_Analysis.xlsx')

                # Save the DataFrame to Excel
                df_uploaded_data.to_excel(excel_file_path, index=False)

                print(f"Data saved to {excel_file_path} successfully!")

                # Pass uploaded_data to the template for display
                messages.success(request, 'File uploaded, analyzed, and saved as Excel successfully!')
                return render(request, 'csv_upload.html', {'form': form, 'uploaded_data': uploaded_data, 'excel_file_path': excel_file_path})

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'csv_upload.html', {'form': form})

    else:
        form = CSVUploadForm()

    return render(request, 'csv_upload.html', {'form': form})


def download_excel(request):
    excel_file_path = os.path.join(settings.MEDIA_ROOT, 'Result_Analysis.xlsx')
    if os.path.exists(excel_file_path):
        with open(excel_file_path, 'rb') as excel_file:
            response = HttpResponse(
                excel_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="Result_Analysis.xlsx"'
            return response
    else:
        messages.error(request, "Excel file does not exist.")
        return render(request, 'csv_upload.html', {'form': CSVUploadForm()})
    
