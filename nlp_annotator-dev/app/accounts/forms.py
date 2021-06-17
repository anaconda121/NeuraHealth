from django import forms
from django.forms import Form, ModelForm, Textarea
from django.core.validators import MaxValueValidator, MinValueValidator 
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.models import User

# user authentication
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

# form to sign up new user for login view
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


# form to request additional patients for dashboard view
class RequestPatientsForm(Form):
    num_to_add = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], label = '')
    