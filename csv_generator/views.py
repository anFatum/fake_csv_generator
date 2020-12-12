from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required(login_url="/auth/login")
def index(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, "base/navbar.html", context)
