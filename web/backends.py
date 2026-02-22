from django.contrib.auth.backends import ModelBackend
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ le vrai modèle

class TelephoneBackend(ModelBackend):
    """
    Authentification via telephone au lieu de username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(telephone=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None