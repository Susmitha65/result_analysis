import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CSVUploadForm
import pandas as pd
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
                with open(csv_file.name, 'r') as file:
                    # Read the first line (header) using ';' as the delimiter
                    header_line = file.readline().strip()
                    #header_line =h  
                    headers = header_line.split(';')
                    #print(headers)
                    # Step 2: Read the rest of the file with ',' as the delimiter
                    data = pd.read_csv(file, delimiter=',', names=headers, skiprows=1)
                    data.columns = data.columns.str.replace('"', '').str.strip()
                print(data)
                uploaded_data=[]
                for index,row in data.iterrows():
                    print("row ",row['Semester'])
                    #break
                    #Append row data to uploaded_data, matching exact CSV header names
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
                #     print(uploaded_data)
                   # break
                # Pass uploaded_data to the template for display
                messages.success(request, 'File uploaded and analyzed successfully!')
                return render(request, 'csv_upload.html', {'form': form, 'uploaded_data': uploaded_data})
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'csv_upload.html', {'form': form})

    else:
        form = CSVUploadForm()

    return render(request, 'csv_upload.html', {'form': form})
