from django.db import models

class EmailContact(models.Model):
    email=models.EmailField(max_length=250)
    is_active= models.BooleanField(default=True)