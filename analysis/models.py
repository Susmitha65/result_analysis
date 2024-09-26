from django.db import models
from django.contrib.auth.models import User

# 1. User Profile (Optional, only needed if you want to extend the default user model)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

# 2. CSV Upload Model
class CSVFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # To track who uploaded the file
    file = models.FileField(upload_to='uploads/csv/')  # Stores the file in 'uploads/csv/' directory
    upload_date = models.DateTimeField(auto_now_add=True)  # Automatically set the upload date

    def __str__(self):
        return f"{self.file.name} uploaded by {self.user.username} on {self.upload_date}"

# 3. Student Result Model
class StudentResult(models.Model):
    csv_file = models.ForeignKey(CSVFile, on_delete=models.CASCADE, related_name='results')  # Link to uploaded CSV file
    register_no = models.CharField(max_length=50)  # Student registration number
    student_name = models.CharField(max_length=100)  # Student name
    branch = models.CharField(max_length=100)  # Branch/Department
    semester = models.IntegerField()  # Semester
    course = models.CharField(max_length=100)  # Course name
    exam_type = models.CharField(max_length=50)  # Exam type (e.g., final, internal)
    attendance = models.CharField(max_length=50)  # Attendance information
    withheld = models.BooleanField(default=False)  # Whether result is withheld
    internal_marks = models.IntegerField()  # Marks obtained in internal exams
    grade = models.CharField(max_length=5)  # Grade (e.g., A, B, C)
    result = models.CharField(max_length=50)  # Final result (e.g., pass, fail)

    def __str__(self):
        return f"{self.student_name} - {self.register_no}"

# Signals to auto-create UserProfile (optional)
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
