from django.http import Http404

from rest_framework.generics import UpdateAPIView
from rest_framework.serializers import ModelSerializer

from typing import Dict


class ActionView(UpdateAPIView):
	"""
	Generic Action View
	"""
	action_map:  Dict[str, ModelSerializer] = {}
	http_method_names = ("put", "patch", "head", "options",)

	def dispatch(self, request, *args, **kwargs):
		self.action = self.kwargs.get("action")
		return super().dispatch(request, *args, **kwargs)

	def get_serializer_class(self):

		if self.action in self.action_map:
			return self.action_map[self.action]

		raise Http404

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context["action"] = self.action
		return context
