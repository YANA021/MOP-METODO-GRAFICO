from django import forms

class ProblemaPLForm(forms.Form):
    OBJETIVO_CHOICES = [
        ('max', 'Maximizar'),
        ('min', 'Minimizar'),
    ]

    objetivo = forms.ChoiceField(choices=OBJETIVO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    coef_x1 = forms.FloatField(label='Coeficiente x1', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Coef x₁'}))
    coef_x2 = forms.FloatField(label='Coeficiente x2', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Coef x₂'}))
    restricciones = forms.CharField(widget=forms.HiddenInput())

    def clean_restricciones(self):
        import json
        data = self.cleaned_data['restricciones']
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError('Formato de restricciones invalido')
        if not isinstance(parsed, list):
            raise forms.ValidationError('Las restricciones deben ser una lista')
        for res in parsed:
            try:
                float(res.get('coef_x1'))
                float(res.get('coef_x2'))
                float(res.get('valor'))
            except (TypeError, ValueError):
                raise forms.ValidationError('Coeficientes y valores deben ser numeros')
            if res.get('operador') not in ['<=', '>=', '=']:
                raise forms.ValidationError('Operador invalido')
        return parsed
