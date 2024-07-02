from rest_framework import serializers
import re


class ContextSerializer(serializers.ModelSerializer):

    def __new__(cls, *args, **kwargs):
        if kwargs.get("many", False) is True:
            context = kwargs.get("context", {})
            context.update({"has_many": True})
            kwargs.update({"context": context})

        return super().__new__(cls, *args, **kwargs)


class ReadOnlyModelSerializer(serializers.ModelSerializer):

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def create(self, validated_data):
        raise NotImplementedError("Read-Only Serializer")

    def update(self, instance, validated_data):
        raise NotImplementedError("Read-Only Serializer")


class ForeignKeyField(serializers.IntegerField):
    """Foreign Key Field for Abstract Models"""

    def __init__(self, *args, **kwargs):
        self.to = kwargs.pop("to")
        super().__init__(*args, **kwargs)
        self.reference_key = self.to._meta.pk.name

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        try:
            return self.to.objects.get(**{self.reference_key: data})
        except self.to.DoesNotExist:
            self.fail(f"{self.to}.{self.reference_key}={data} does not exit")

    def to_representation(self, value):
        if value:
            return getattr(value, self.reference_key)


class PhoneNumberField(serializers.CharField):

    @staticmethod
    def _validate_phone_number(value):
        digits = re.sub(r"\D", "", value)
        # TODO: Add Additional Validation
        if len(digits) != 11:
            raise serializers.ValidationError("Phone number must contain 11 digits.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(PhoneNumberField._validate_phone_number)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return re.sub(r"\D", "", data)

    def to_representation(self, value):
        value = super().to_representation(value)
        return f"+{value[0]} ({value[1:4]}) {value[4:7]}-{value[7:11]}"
