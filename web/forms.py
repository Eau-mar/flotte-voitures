from .models import Vehicule, DocumentVehicule, Entretien, Chauffeur, User
from django import forms

# ... Existing forms ...

class ChauffeurForm(forms.ModelForm):
    class Meta:
        model = Chauffeur
        fields = ["nom", "telephone", "numero_permis", "date_expiration_permis", "statut"]
        widgets = {
            "date_expiration_permis": forms.DateInput(attrs={"type": "date"})
        }

# ----------------------------
# Formulaire d'inscription
# ----------------------------
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer mot de passe")

    # champs chauffeur (optionnels)
    numero_permis = forms.CharField(required=False, label="Numéro permis")
    date_expiration_permis = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type':'date'}),
        label="Date d'expiration permis"
    )

    class Meta:
        model = User
        fields = ['first_name','last_name','telephone','role','password']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        permis = cleaned_data.get("numero_permis")
        date_perm = cleaned_data.get("date_expiration_permis")
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        if role == "driver":
            if not permis or not date_perm:
                raise forms.ValidationError(
                    "Les informations du permis sont obligatoires pour un chauffeur"
                )

        return cleaned_data

# ----------------------------
# Formulaire Login
# ----------------------------
class LoginForm(forms.Form):
    telephone = forms.CharField(label="Téléphone")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

# ----------------------------
# Formulaire reset par téléphone
# ----------------------------
class PhoneResetForm(forms.Form):
    telephone = forms.CharField(max_length=20, label="Téléphone")

class OTPVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label="Code OTP")

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer mot de passe")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        return cleaned


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = "__all__"


class DocumentVehiculeForm(forms.ModelForm):
    class Meta:
        model = DocumentVehicule
        fields = "__all__"
        widgets = {
            "date_emission": forms.DateInput(attrs={"type": "date"}),
            "date_expiration": forms.DateInput(attrs={"type": "date"}),
        }


class AssignVehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ["chauffeur"]
        labels = {
            "chauffeur": "Choisir un chauffeur"
        }


class EntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ["vehicule", "type_entretien", "date_prevue", "cout", "effectue"]
        widgets = {
            "date_prevue": forms.DateInput(attrs={"type": "date"})
        }