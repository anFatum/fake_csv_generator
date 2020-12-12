from django.contrib.auth import authenticate, login
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from authentication.forms import LoginForm


class LoginView(TemplateView):
    template_name = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        context = {
            'form': LoginForm()
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        if form.is_valid():
            cleaned_form = form.cleaned_data
            user = authenticate(username=cleaned_form['username'],
                                password=cleaned_form['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
                form.add_error(None, "User is not active")
            else:
                form.add_error(None, "Wrong credentials")
        return render(request, self.template_name, context)
