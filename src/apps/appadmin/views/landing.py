from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from datetime import date, datetime, timedelta
from typing import Any, Dict


class LandingView(TemplateView):
	template_name = "appadmin/landing.html"
