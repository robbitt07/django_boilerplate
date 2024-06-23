from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from datetime import date, datetime, timedelta
from typing import Any, Dict


class GenericTemplateView(TemplateView):
	template_name = 'appadmin/generic/generic_template.html'

	def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
		context = super().get_context_data(**kwargs)
		context['table_data'] = [
			{
				"bol_num": "123412344132",
				"customer": "3M Chemical",
				"pickup_date": date.today() + timedelta(days=2),
				"created_on": datetime.utcnow() - timedelta(minutes=37)
			},
			{
				"bol_num": "8789723847324",
				"customer": "Ivan Catalytic Recycling",
				"pickup_date": date.today() + timedelta(days=4),
				"created_on": datetime.utcnow() - timedelta(days=2)
			}, {
				"bol_num": "54242452345",
				"customer": "3M Chemical",
				"pickup_date": date.today() - timedelta(days=365),
				"created_on": datetime.utcnow() - timedelta(days=365) - timedelta(days=3)
			}
		]
		return context