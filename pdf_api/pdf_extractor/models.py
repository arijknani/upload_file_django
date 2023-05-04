from django.db import models

class PDFFile(models.Model):
    file = models.FileField(upload_to='login/')
    text = models.TextField()