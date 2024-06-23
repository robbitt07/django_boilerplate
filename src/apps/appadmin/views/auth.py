from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from datetime import date, datetime, timedelta
from typing import Any, Dict


class LogoutUser(View):

	def get(self, request, *args, **kwargs):
		logout(request)
		return HttpResponseRedirect(reverse('login_user'))


class LoginUser(View):
	template_name = 'appadmin/login.html'

	def get(self, request, *args, **kwargs):
		form = AuthenticationForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = AuthenticationForm()

		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)

				# Redirect URL to previously desired page
				redirect_url = request.GET.get('next')
				if redirect_url is not None and redirect_url != '':
					return HttpResponseRedirect(redirect_url)

				return HttpResponseRedirect(reverse("landing"))

			context = {'error_message': 'Your account has been disabled'}
			return render(request, self.template_name, context=context)

		form = AuthenticationForm()
		context = {'error_message': 'Invalid login', 'form': form}
		return render(request, self.template_name, context=context)
