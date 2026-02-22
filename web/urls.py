from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register, login_view, logout_view, password_reset_phone,
    verify_otp, set_new_password, vehicule_list, vehicule_create,
    dashboard, document_create, document_list, assign_vehicule,
    entretien_create, entretien_list, welcome, vehicule_update,
    vehicule_delete, document_update, document_delete, assign_vehicule,
    entretien_update, entretien_delete, chauffeur_list,
    chauffeur_update, chauffeur_delete)

urlpatterns = [
    path("", welcome, name='bienvenue'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('bord/', dashboard, name='dashboard'),
    path("reset/", password_reset_phone, name="password_reset"),
    path("verify/", verify_otp, name="verify_otp"),
    path("new-password/", set_new_password, name="set_new_password"),
    path("vehicules/", vehicule_list, name="vehicule_list"),
    path("vehicules/ajouter/", vehicule_create, name="vehicule_create"),
    path("vehicules/<int:pk>/modifier/", vehicule_update, name="vehicule_update"),
    path("vehicules/<int:pk>/supprimer/", vehicule_delete, name="vehicule_delete"),
    path("documents/ajouter/", document_create, name="document_create"),
    path("documents/<int:pk>/modifier/", document_update, name="document_update"),
    path("documents/<int:pk>/supprimer/", document_delete, name="document_delete"),
    path("vehicule/<int:vehicule_id>/documents/", document_list, name="document_list"),
    path("vehicules/<int:pk>/assign/", assign_vehicule, name="vehicule_assign"),
    path("entretiens/ajouter/", entretien_create, name="entretien_create"),
    path("entretiens/<int:pk>/modifier/", entretien_update, name="entretien_update"),
    path("entretiens/<int:pk>/supprimer/", entretien_delete, name="entretien_delete"),
    path("vehicule/<int:vehicule_id>/entretiens/", entretien_list, name="entretien_list"),
    path("chauffeurs/", chauffeur_list, name="chauffeur_list"),
    path("chauffeurs/<int:pk>/modifier/", chauffeur_update, name="chauffeur_update"),
    path("chauffeurs/<int:pk>/supprimer/", chauffeur_delete, name="chauffeur_delete"),
]

