
from typing import Any, Optional
from django import forms


class DateInputWidget(forms.DateInput):
    input_type = "date"

    def __init__(self, attrs=None, format="%Y-%m-%d"):
        super().__init__(attrs)
        self.format = format


class DateTimeInputWidget(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, attrs={"step": 1}, format="%Y-%m-%dT%H:%M"):
        super().__init__(attrs)
        self.format = format


class MultipleChoiceModelField(forms.MultipleChoiceField):
    """Field for Mananging Array fields as Foreign Keys"""
    def clean(self, value):
        return super().clean([int(val) for val in value])

    def to_python(self, value: Optional[Any]) -> Optional[Any]:
        return [int(val) for val in super().to_python(value)]


class SelectPickerMultipleWidget(forms.SelectMultiple):
    # https://developer.snapappointments.com/bootstrap-select/examples/
    base_attrs = {
        'class': 'selectpicker', 'multiple': '', 'data-menu-style': 'dropdown-blue',
        'readonly': True
    }

    def __init__(self,
                 data_actions: bool = True,
                 class_name: str = None,
                 compressed: bool = False,
                 max_display: int = None,
                 *args,
                 **kwargs):
        attrs = self.base_attrs.copy()
        if "attrs" in kwargs:
            attrs.update(**kwargs.pop("attrs"))

        # Update Max Display Attributes
        if isinstance(max_display, int):
            attrs.update({
                'data-selected-text-format': f"count > {max_display}"
            })

        if class_name is not None:
            attrs.update({
                'class': ' '.join([attrs.get('class') or "", class_name])
            })

        if compressed:
            attrs.update({
                'class': ' '.join([attrs.get('class') or "", "compressed"])
            })

        if data_actions:
            attrs.update({'data-actions-box': 'true'})

        super(SelectPickerMultipleWidget, self).__init__(attrs=attrs, *args, **kwargs)
