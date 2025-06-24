from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class ProblemaPLForm(forms.Form):
    OBJETIVO_CHOICES = [
        ("max", "Maximizar"),
        ("min", "Minimizar"),
    ]

    input_classes = (
        "form-control bg-white border-gray-300 text-gray-800 placeholder-gray-500 "
        "dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
    )

    objetivo = forms.ChoiceField(
        choices=OBJETIVO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select " + input_classes})
    )
    coef_x1 = forms.FloatField(
        label="Coeficiente x1",
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Coeficiente de x₁"}
        ),
    )
    coef_x2 = forms.FloatField(
        label="Coeficiente x2",
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Coeficiente de x₂"}
        ),
    )
    x1_min = forms.FloatField(
        label="Valor mínimo para x1",
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Mínimo permitido para x₁"}
        ),
    )
    x1_max = forms.FloatField(
        label="Valor máximo para x1",
        required=False,
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Valor máximo permitido para x₁"}
        ),
    )
    x2_min = forms.FloatField(
        label="Valor mínimo para x2",
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Mínimo permitido para x₂"}
        ),
    )
    x2_max = forms.FloatField(
        label="Valor máximo para x2",
        required=False,
        widget=forms.NumberInput(
            attrs={"class": input_classes, "placeholder": "Máximo permitido para x₂"}
        ),
    )
    restricciones = forms.CharField(widget=forms.HiddenInput())

    def clean_restricciones(self):
        import json

        data = self.cleaned_data["restricciones"]
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Formato de restricciones invalido")
        if not isinstance(parsed, list):
            raise forms.ValidationError("Las restricciones deben ser una lista")
        for res in parsed:
            try:
                float(res.get("coef_x1"))
                float(res.get("coef_x2"))
                float(res.get("valor"))
            except (TypeError, ValueError):
                raise forms.ValidationError("Coeficientes y valores deben ser numeros")
            if res.get("operador") not in ["<=", ">=", "="]:
                raise forms.ValidationError("Operador invalido")
        return parsed

    def clean(self):
        cleaned = super().clean()
        x1_min = cleaned.get("x1_min")
        x1_max = cleaned.get("x1_max")
        x2_min = cleaned.get("x2_min")
        x2_max = cleaned.get("x2_max")
        if x1_min is not None and x1_max is not None and x1_max < x1_min:
            self.add_error(
                "x1_max", "El límite superior debe ser mayor o igual al inferior"
            )
        if x2_min is not None and x2_max is not None and x2_max < x2_min:
            self.add_error(
                "x2_max", "El límite superior debe ser mayor o igual al inferior"
            )
        return cleaned


class LoginForm(AuthenticationForm):
    """Authentication form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Usuario"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Contraseña", "id": "password"}
        )


class RegisterForm(UserCreationForm):
    """User creation form with email field and Bootstrap styling."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Usuario"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Email"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Contraseña"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirmar contraseña"}
        )


class ProfileForm(forms.ModelForm):
    """Form to edit user profile information."""

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Usuario"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Email"}
        )
