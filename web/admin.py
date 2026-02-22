from django.contrib import admin
from .models import Vehicule, Chauffeur, Entretien
from django.contrib.auth import get_user_model
User = get_user_model()

# Register your models here.

tables = [User, Vehicule, Chauffeur, Entretien]

admin.site.register(tables)
