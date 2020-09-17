from django.contrib import admin
from .models import EmailContact


@admin.register(EmailContact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email',]