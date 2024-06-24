from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.query import QuerySet

from utils.models import Common
from utils.model_helpers import model_to_dict

import numpy as np


class BoilerPlateEncoder(DjangoJSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # NOTE: Add Additional Abstract Models Here
        if set({Model, Common}).intersection(set(obj.__class__.__bases__)):
            return model_to_dict(obj)

        if isinstance(obj, QuerySet):
            return list(obj)

        if callable(obj):
            return f"{obj.__module__}.{obj.__name__}"

        return DjangoJSONEncoder.default(self, obj)
