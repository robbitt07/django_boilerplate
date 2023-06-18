from rest_framework import serializers
from rest_framework.fields import ListField


class StringArrayField(ListField):
    """
    String representation of an array field.
    """

    def to_representation(self, obj):
        obj = super().to_representation(self, obj)
        # convert list to string
        return ",".join([str(element) for element in obj])

    def to_internal_value(self, data):
        data = data.split(",")  # convert string to list
        return super().to_internal_value(self, data)


class DisplayArrayField(ListField):
    """
    Display based Array field, takes a `display_options` kwarg to map
    codes to display names
    """

    def __init__(self, *args, **kwargs):
        display_options = kwargs.pop('display_options')
        super().__init__(self, *args, **kwargs)
        self.display_options = display_options

    def to_representation(self, obj, *args, **kwargs):
        obj = super().to_representation(obj)
        return {key: self.display_options.get(key) for key in obj}
