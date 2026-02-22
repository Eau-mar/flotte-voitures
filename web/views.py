from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, timedelta

from .models import Vehicule, DocumentVehicule, Entretien, PasswordResetOTP, Chauffeur
from .forms import (
    RegisterForm, LoginForm, PhoneResetForm, OTPVerificationForm, 
    SetNewPasswordForm, VehiculeForm, DocumentVehiculeForm, 
    AssignVehiculeForm, EntretienForm, ChauffeurForm
)

User = get_user_model()


def welcome(request):
    return render(request, "web/welcome.html")

# ----------------------------
# Inscription
# ----------------------------
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['telephone']
            user.set_password(form.cleaned_data["password"])
            user.save()

            if user.role == "driver":
                Chauffeur.objects.create(
                    utilisateur=user,
                    nom=f"{user.first_name} {user.last_name}",
                    telephone=user.telephone,
                    numero_permis=form.cleaned_data["numero_permis"],
                    date_expiration_permis=form.cleaned_data["date_expiration_permis"]
                )

            # définir backend manuellement
            user.backend = "web.backends.TelephoneBackend"
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "web/comptes/inscription.html", {"form": form})



# ----------------------------
# Login par téléphone
# ----------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            tel = form.cleaned_data["telephone"]
            password = form.cleaned_data["password"]

            # username correspond maintenant au telephone
            user = authenticate(request, username=tel, password=password)

            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Téléphone ou mot de passe incorrect")
    else:
        form = LoginForm()

    return render(request, "web/comptes/connexion.html", {"form": form})


# ----------------------------
# Logout
# ----------------------------
def logout_view(request):
    logout(request)
    return redirect("login")


# ----------------------------
# Mot de passe oublié → demander téléphone
# ----------------------------
def password_reset_phone(request):
    form = PhoneResetForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        tel = form.cleaned_data["telephone"]

        try:
            user = User.objects.get(telephone=tel)

            # supprimer anciens OTP
            PasswordResetOTP.objects.filter(user=user).delete()

            otp = PasswordResetOTP.objects.create(user=user)
            otp.generate_code()

            print("SMS OTP (simulé) :", otp.code)

            request.session["reset_user"] = user.id
            return redirect("verify_otp")

        except User.DoesNotExist:
            messages.error(request, "Numéro inconnu")

    return render(request, "web/comptes/reset.html", {"form": form})


# ----------------------------
# Vérification OTP
# ----------------------------
def verify_otp(request):
    if "reset_user" not in request.session:
        return redirect("login")

    form = OTPVerificationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]
        user_id = request.session["reset_user"]

        try:
            otp = PasswordResetOTP.objects.get(user_id=user_id, code=code)
            otp.is_verified = True
            otp.save()

            request.session["otp_verified"] = True
            return redirect("set_new_password")

        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "Code invalide")

    return render(request, "web/comptes/otp_verify.html", {"form": form})


# ----------------------------
# Nouveau mot de passe
# ----------------------------
def set_new_password(request):
    if not request.session.get("otp_verified"):
        return redirect("login")

    form = SetNewPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user_id = request.session["reset_user"]
        user = User.objects.get(id=user_id)

        user.password = make_password(form.cleaned_data["password1"])
        user.save()

        # nettoyage OTP et session
        PasswordResetOTP.objects.filter(user=user).delete()
        request.session.flush()

        messages.success(request, "Mot de passe modifié avec succès !")
        return redirect("login")

    return render(request, "web/comptes/set_new.html", {"form": form})


@login_required
def vehicule_create(request):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    form = VehiculeForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Véhicule ajouté")
        return redirect("vehicule_list")

    return render(request, "web/vehicules/create.html", {"form": form})


@login_required
def vehicule_update(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    vehicule = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(request.POST or None, instance=vehicule)

    if form.is_valid():
        form.save()
        messages.success(request, "Véhicule mis à jour")
        return redirect("vehicule_list")

    return render(request, "web/vehicules/update.html", {"form": form, "vehicule": vehicule})


@login_required
def vehicule_delete(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    vehicule = get_object_or_404(Vehicule, pk=pk)
    
    if request.method == "POST":
        vehicule.delete()
        messages.success(request, "Véhicule supprimé")
        return redirect("vehicule_list")
        
    return render(request, "web/vehicules/confirm_delete.html", {"vehicule": vehicule})


@login_required
def vehicule_list(request):
    vehicules = Vehicule.objects.all()
    return render(request, "web/vehicules/list_vehicules.html", {"vehicules": vehicules})


@login_required
def document_create(request):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    if request.method == "POST":
        form = DocumentVehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save()
            messages.success(request, "Document ajouté")
            return redirect("document_list", vehicule_id=doc.vehicule.id)
    else:
        form = DocumentVehiculeForm()

    return render(request, "web/documents/ajout_document.html", {"form": form})


@login_required
def document_update(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    document = get_object_or_404(DocumentVehicule, pk=pk)
    form = DocumentVehiculeForm(request.POST or None, request.FILES or None, instance=document)

    if form.is_valid():
        form.save()
        messages.success(request, "Document mis à jour")
        return redirect("document_list", vehicule_id=document.vehicule.id)

    return render(request, "web/documents/update_document.html", {"form": form, "document": document})


@login_required
def document_delete(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    document = get_object_or_404(DocumentVehicule, pk=pk)
    vehicule_id = document.vehicule.id
    
    if request.method == "POST":
        document.delete()
        messages.success(request, "Document supprimé")
        return redirect("document_list", vehicule_id=vehicule_id)
        
    return render(request, "web/documents/confirm_delete_document.html", {"document": document})


def document_list(request, vehicule_id):
    vehicule = Vehicule.objects.get(id=vehicule_id)
    documents = vehicule.documents.all()

    return render(
        request,
        "web/documents/list_document.html",
        {"vehicule": vehicule, "documents": documents}
    )



@login_required
def assign_vehicule(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    vehicule = get_object_or_404(Vehicule, pk=pk)

    form = AssignVehiculeForm(request.POST or None, instance=vehicule)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Chauffeur assigné avec succès.")
        return redirect("vehicule_list")

    return render(request, "web/vehicules/assign.html", {
        "form": form,
        "vehicule": vehicule
    })


def entretien_list(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)
    entretiens = vehicule.entretiens.all().order_by("-date_prevue")

    return render(
        request,
        "web/entretiens/entretien_list.html",
        {
            "vehicule": vehicule,
            "entretiens": entretiens,
            "today": timezone.now().date()
        }
    )


@login_required
def chauffeur_list(request):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")
    
    chauffeurs = Chauffeur.objects.all()
    return render(request, "web/comptes/list_chauffeurs.html", {"chauffeurs": chauffeurs})


@login_required
def chauffeur_update(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    form = ChauffeurForm(request.POST or None, instance=chauffeur)

    if form.is_valid():
        form.save()
        messages.success(request, "Profil chauffeur mis à jour")
        return redirect("chauffeur_list")

    return render(request, "web/comptes/update_chauffeur.html", {"form": form, "chauffeur": chauffeur})


@login_required
def chauffeur_delete(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    
    if request.method == "POST":
        # Note: Depending on business logic, we might want to delete the User too, 
        # or just the chauffeur profile. Here we delete the profile.
        chauffeur.delete()
        messages.success(request, "Chauffeur supprimé")
        return redirect("chauffeur_list")
        
    return render(request, "web/comptes/confirm_delete_chauffeur.html", {"chauffeur": chauffeur})

@login_required
def entretien_create(request):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    form = EntretienForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        entretien = form.save()
        messages.success(request, "Entretien enregistré")
        return redirect("entretien_list", vehicule_id=entretien.vehicule.id)

    return render(request, "web/entretiens/ajout_entretien.html", {"form": form})


@login_required
def entretien_update(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    entretien = get_object_or_404(Entretien, pk=pk)
    form = EntretienForm(request.POST or None, instance=entretien)

    if form.is_valid():
        form.save()
        messages.success(request, "Entretien mis à jour")
        return redirect("entretien_list", vehicule_id=entretien.vehicule.id)

    return render(request, "web/entretiens/update_entretien.html", {"form": form, "entretien": entretien})


@login_required
def entretien_delete(request, pk):
    if request.user.role != "manager":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    entretien = get_object_or_404(Entretien, pk=pk)
    vehicule_id = entretien.vehicule.id
    
    if request.method == "POST":
        entretien.delete()
        messages.success(request, "Entretien supprimé")
        return redirect("entretien_list", vehicule_id=vehicule_id)
        
    return render(request, "web/entretiens/confirm_delete_entretien.html", {"entretien": entretien})


@login_required
def dashboard(request):
    # ... (existing dashboard code) ...
    user = request.user
    today = timezone.now().date()
    
    if user.role == "driver":
        # Chauffeur Dashboard
        chauffeur = getattr(user, 'profil_chauffeur', None)
        mes_vehicules = chauffeur.vehicules.all() if chauffeur else []
        
        context = {
            "chauffeur": chauffeur,
            "mes_vehicules": mes_vehicules,
            "today": today,
        }
        return render(request, "web/comptes/dashboard_chauffeur.html", context)

    # Manager Dashboard (logic preserved)
    in_30_days = today + timedelta(days=30)
    in_7_days = today + timedelta(days=7)

    # KPI VEHICULES
    total_vehicules = Vehicule.objects.count()
    vehicules_disponibles = Vehicule.objects.filter(statut="DISPONIBLE").count()
    vehicules_mission = Vehicule.objects.filter(statut="MISSION").count()
    vehicules_maintenance = Vehicule.objects.filter(statut="MAINTENANCE").count()

    # KPI CHAUFFEURS
    total_chauffeurs = Chauffeur.objects.count()
    chauffeurs_disponibles = Chauffeur.objects.filter(statut="DISPONIBLE").count()
    chauffeurs_mission = Chauffeur.objects.filter(statut="MISSION").count()

    # DOCUMENTS
    documents_expires = DocumentVehicule.objects.filter(date_expiration__lt=today)
    documents_bientot = DocumentVehicule.objects.filter(date_expiration__range=[today, in_30_days])
    documents_expires_count = documents_expires.count()
    documents_bientot_count = documents_bientot.count()

    # ENTRETIENS
    entretiens_retard = Entretien.objects.filter(date_prevue__lt=today, effectue=False)
    entretiens_bientot = Entretien.objects.filter(date_prevue__range=[today, in_7_days], effectue=False)

    # PERMIS
    chauffeurs_permis_expire = Chauffeur.objects.filter(date_expiration_permis__lt=today)

    # ACTIVITÉ RÉCENTE
    derniers_vehicules = Vehicule.objects.order_by("-date_creation")[:5]
    derniers_entretiens = Entretien.objects.order_by("-id")[:5]

    context = {
        "total_vehicules": total_vehicules,
        "vehicules_disponibles": vehicules_disponibles,
        "vehicules_mission": vehicules_mission,
        "vehicules_maintenance": vehicules_maintenance,
        "total_chauffeurs": total_chauffeurs,
        "chauffeurs_disponibles": chauffeurs_disponibles,
        "chauffeurs_mission": chauffeurs_mission,
        "documents_expires_count": documents_expires_count,
        "documents_bientot_count": documents_bientot_count,
        "documents_expires": documents_expires,
        "documents_bientot": documents_bientot,
        "entretiens_retard": entretiens_retard,
        "entretiens_bientot": entretiens_bientot,
        "chauffeurs_permis_expire": chauffeurs_permis_expire,
        "derniers_vehicules": derniers_vehicules,
        "derniers_entretiens": derniers_entretiens,
    }
    return render(request, "web/comptes/dashboard.html", context)
