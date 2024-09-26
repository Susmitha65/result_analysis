import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CSVUploadForm

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
                # Open the uploaded file and read its content
                csv_file.open(mode='r')  # Open the file in reading mode
                decoded_file = csv_file.read().splitlines()  # No need to decode
                reader = csv.DictReader(decoded_file, delimiter=';')  # Specify semicolon delimiter

                uploaded_data = []
                for row in reader:
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

                # Pass uploaded_data to the template for display
                messages.success(request, 'File uploaded and analyzed successfully!')
                return render(request, 'csv_upload.html', {'form': form, 'uploaded_data': uploaded_data})

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'csv_upload.html', {'form': form})

    else:
        form = CSVUploadForm()

    return render(request, 'csv_upload.html', {'form': form})
