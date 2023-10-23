from django.db import models
SEMESTER_CHOICES = [
    ('summer_2023', 'Summer 2023'),
    ('fall_2023', 'Fall 2023'),
    ('summer_2024', 'Summer 2024'),
    ('fall_2024', 'Fall 2024'),
]
# Create your models here.
class ExperimentData(models.Model):
    name = models.CharField(max_length=255)
    matrikel_number = models.IntegerField()
    experiment_number = models.CharField(max_length=10)
    report = models.FileField(upload_to='reports/')
    raw_data = models.FileField(upload_to='raw_data/')
    date_of_submission = models.DateTimeField(auto_now_add=True)
    semester = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        default='summer_2023'
    )
    def is_excel_file(self):
        return self.raw_data and (self.raw_data.url.endswith('.xlsx') or self.raw_data.url.endswith('.xls'))

    def __str__(self):
        return self.name
    
class Deadline(models.Model):
    experiment_name = models.CharField(max_length=255)
    experiment_deadline = models.DateTimeField()
    matrikel_number = models.IntegerField(default=0)
    semester = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        default='summer_2023'
    )


    def __str__(self):
        return self.experiment_name
    
class Template(models.Model):
    experiment_name = models.CharField(max_length=255)
    template = models.FileField(upload_to='templates/')  # Store templates in a folder called 'templates'

    def __str__(self):
        return self.experiment_name
