from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, View

from authentication.forms import LoginForm


class LoginView(TemplateView):
    template_name = "authentication/login.html"

    def get(self, request, *args, **kwargs):
        """
        GET method returns Login view
        :param request: GET request
        :type request:
        :return: HTTP response
        :rtype: HttpResponse
        """
        context = {
            'form': LoginForm()
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        POST method login user (if credentials are valid and user is
        active) and redirects to main page
        :param request: POST request
        :type request:
        :return: HTTP response
        :rtype: HttpResponse
        """
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        if form.is_valid():
            cleaned_form = form.cleaned_data
            user = authenticate(username=cleaned_form['username'],
                                password=cleaned_form['password'])
            if user is not None and user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                form.add_error(None, "Wrong credentials")
        return render(request, self.template_name, context)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        """
        GET request for logout, redirecting to home page, that redirects to
        login page
        :param request:
        :type request:
        :rtype:
        """
        logout(request)
        return HttpResponseRedirect('/')
