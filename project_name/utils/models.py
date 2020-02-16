from django.conf import settings
from django.db import models

import uuid

class Common(models.Model):
	# Override default id
	id = models.BigAutoField(db_column='id', primary_key=True)
	uuid = models.UUIDField(default=uuid.uuid4, index=True, editable=False)
	
	# Meta Columns
	created_on  = models.DateTimeField(db_column='created_on', auto_now_add=True, editable=False)
	updated_on = models.DateTimeField(db_column='updated_on', auto_now=True, editable=False)
	created_by  = models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column='created_by',
									null=True, db_index=True, editable=False,
									on_delete=models.SET_NULL, related_name='%(class)s_created_by')
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by',
									null=True, db_index=True, editable=False,
									on_delete=models.SET_NULL, related_name='%(class)s_updated_by')

	def dj_model_meta(self):
		return self._meta

	class Meta:
		abstract = True