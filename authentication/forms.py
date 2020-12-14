from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    error_css_class = "alert alert-danger"
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username",
                                      "class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password",
                                          "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("username", "password",)
