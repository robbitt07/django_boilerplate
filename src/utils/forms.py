from django import forms


class DateInputWidget(forms.DateInput):
    input_type = 'date'

    def __init__(self, attrs=None, format='%Y-%m-%d'):
        super().__init__(attrs)
        self.format = format


class DateTimeInputWidget(forms.DateTimeInput):
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M:%S'):
        super().__init__(attrs)
        self.format = format


class ContextForm(forms.Form):

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context if isinstance(context, dict) else None
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Filter Querysets to Customer
            if hasattr(self.fields[field], 'queryset') and 'customer' in self.context:
                self.fields[field].queryset = self.fields[field].queryset.filter(
                    customer=self.context['customer']
                )


class ContextModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context if isinstance(context, dict) else None
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Filter Querysets to Customer
            if hasattr(self.fields[field], 'queryset') and 'customer' in self.context:
                self.fields[field].queryset = self.fields[field].queryset.filter(
                    customer=self.context['customer']
                )
