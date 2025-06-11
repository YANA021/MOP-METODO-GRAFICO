from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

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




class StyledAuthenticationForm(AuthenticationForm):
    """Authentication form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Usuario'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Contraseña', 'id': 'password'}
        )


class StyledUserCreationForm(UserCreationForm):
    """User creation form with email field and Bootstrap styling."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Usuario'}
        )
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email'}
        )
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Contraseña'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirmar contraseña'}
        )