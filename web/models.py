from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import random

# ----------------------------
# UTILISATEUR
# ----------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Gestionnaire'),
        ('driver', 'Chauffeur'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, unique=True)

    # login via telephone
    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.username} ({self.telephone})"


# ----------------------------
# VEHICULES
# ----------------------------
class Vehicule(models.Model):
    class Statut(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        MISSION = "MISSION", "En mission"
        MAINTENANCE = "MAINTENANCE", "En maintenance"

    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    annee = models.PositiveIntegerField()
    kilometrage = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.DISPONIBLE)
    date_creation = models.DateTimeField(auto_now_add=True)

    chauffeur = models.ForeignKey(
        "Chauffeur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicules"
    )

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"


# ----------------------------
# DOCUMENTS VEHICULE
# ----------------------------
from datetime import date

class DocumentVehicule(models.Model):

    class TypeDocument(models.TextChoices):
        ASSURANCE = "ASSURANCE", "Assurance"
        VISITE = "VISITE", "Visite technique"
        CARTE_GRISE = "CARTE_GRISE", "Carte grise"

    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="documents")
    type_document = models.CharField(max_length=20, choices=TypeDocument.choices)
    date_expiration = models.DateField()

    def est_expire(self):
        return self.date_expiration < date.today()

    def expire_bientot(self):
        return 0 <= (self.date_expiration - date.today()).days <= 30



# ----------------------------
# CHAUFFEUR
# ----------------------------
class Chauffeur(models.Model):

    class Statut(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        MISSION = "MISSION", "En mission"

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_chauffeur",
        null=True,
        blank=True
    )
    nom = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.DISPONIBLE)

    numero_permis = models.CharField(max_length=50, unique=True)
    date_expiration_permis = models.DateField()

    def __str__(self):
        return self.utilisateur.get_full_name() if self.utilisateur else self.nom



# ----------------------------
# ENTRETIEN VEHICULE
# ----------------------------
class Entretien(models.Model):
    TYPE_CHOICES = (
        ('vidange', 'Vidange'),
        ('reparation', 'Réparation'),
        ('revision', 'Révision'),
    )

    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="entretiens")
    type_entretien = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date_prevue = models.DateField()
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    effectue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type_entretien} - {self.vehicule.immatriculation}"


# ----------------------------
# OTP RECUPERATION MOT DE PASSE
# ----------------------------
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return f"OTP {self.code} pour {self.user.telephone}"
