# 🚗 Gestion de Flotte de Véhicules

Application web développée avec Django permettant la gestion complète d’une flotte de véhicules.

---

## 📌 Fonctionnalités

- Authentification par téléphone
- Gestion des rôles (Gestionnaire / Chauffeur)
- Gestion des véhicules
- Attribution de véhicule à un chauffeur
- Gestion des documents (assurance, visite technique, etc.)
- Suivi des entretiens
- Dashboard avec indicateurs KPI
- Alertes (documents expirés, permis expirés, maintenance en retard)

---

## 🛠 Technologies utilisées

- Python 3.14
- Django 6
- SQLite
- HTML / CSS
- JavaScript

---

# ⚙️ Installation du projet
Create a virtual environment
python -m venv venv
Activate it:
Windows
venv\Scripts\activate
Mac / Linux
source venv/bin/activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Apply migrations
python manage.py makemigrations
python manage.py migrate
5️⃣ Create superuser (optional)
python manage.py createsuperuser
6️⃣ Run the development server
python manage.py runserver

Open your browser:

http://127.0.0.1:8000/

## 1️⃣ Cloner le dépôt

```bash
git clone https://github.com/Eau-mar/gestion_flotte_voitures.git
cd gestion_flotte_voitures
