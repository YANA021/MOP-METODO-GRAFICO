from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProblemaPLForm
from .utils import export_resultado
from .models import ProblemaPL
from .solver import resolver_metodo_grafico
import io
from openpyxl import Workbook
from docx import Document
from docx.shared import Inches
from django.contrib.auth import login as auth_login, logout
from .forms import (
    ProblemaPLForm,
    LoginForm,
    RegisterForm,
    ProfileForm,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def metodo_grafico(request):
    mensaje = ""
    resultado = None
    grafica_normal = ""
    grafica_cruz = ""
    post_data = None
    if request.method == "POST":
        form = ProblemaPLForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data["objetivo"],
                    coef_x1=form.cleaned_data["coef_x1"],
                    coef_x2=form.cleaned_data["coef_x2"],
                    restricciones=form.cleaned_data["restricciones"],
                )
                mensaje = "Problema guardado correctamente."
            bounds = {
                "x1_min": form.cleaned_data.get("x1_min"),
                "x1_max": form.cleaned_data.get("x1_max"),
                "x2_min": form.cleaned_data.get("x2_min"),
                "x2_max": form.cleaned_data.get("x2_max"),
            }
            resultado_normal = resolver_metodo_grafico(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                form.cleaned_data["restricciones"],
                bounds=bounds,
                estilo="normal",
            )
            resultado_cruz = resolver_metodo_grafico(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                form.cleaned_data["restricciones"],
                bounds=bounds,
                estilo="cruz",
            )
            resultado = resultado_normal
            grafica_normal = resultado_normal.get("grafica", "")
            grafica_cruz = resultado_cruz.get("grafica", "")
            post_data = request.POST
            form = ProblemaPLForm()
    else:
        form = ProblemaPLForm()
    context = {
        "form": form,
        "mensaje": mensaje,
        "grafica_normal": grafica_normal,
        "grafica_cruz": grafica_cruz,
        "resultado": resultado,
        "post_data": post_data,
    }
    return render(request, "nuevo_problema.html", context)


def exportar_resultado(request, formato):
    if request.method != "POST":
        return HttpResponse(status=405)

    form = ProblemaPLForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Datos invalidos", status=400)

    bounds = {
        "x1_min": form.cleaned_data.get("x1_min"),
        "x1_max": form.cleaned_data.get("x1_max"),
        "x2_min": form.cleaned_data.get("x2_min"),
        "x2_max": form.cleaned_data.get("x2_max"),
    }
    resultado = resolver_metodo_grafico(
        form.cleaned_data["objetivo"],
        form.cleaned_data["coef_x1"],
        form.cleaned_data["coef_x2"],
        form.cleaned_data["restricciones"],
        bounds=bounds,
    )

    fig = resultado.get("fig")
    try:
        data, content_type, filename = export_resultado(resultado, fig, formato)
    except ValueError:
        return HttpResponse("Formato no soportado", status=400)
    except Exception as e:
        return HttpResponse(f"Error generando archivo: {e}", status=500)

    response = HttpResponse(data, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def login_view(request):
    """Handle user authentication."""
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("home")
    else:
        form = LoginForm(request)
    return render(request, "login.html", {"form": form})


def register(request):
    """Create a new user account."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    context = {
        "form": form,
        "title": "Registro",
        "button_text": "Registrarse",
        "question_text": "¿Ya tienes una cuenta?",
        "login_text": "Iniciar sesión",
    }
    return render(request, "register.html", context)


@login_required
def perfil_show(request):
    """Display current user's profile."""
    return render(request, "show.html", {"user": request.user})


@login_required
def perfil_edit(request):
    """Allow the user to edit their profile."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil_show")
    else:
        form = ProfileForm(instance=request.user)
    # ``edit.html`` also resides at the project templates root.
    return render(request, "edit.html", {"form": form})


def logout_view(request):
    """Log out the current user and redirect to login."""
    logout(request)
    return redirect("login")


@login_required
def historial(request):
    """Display all ProblemaPL entries created by the logged in user."""
    problemas = ProblemaPL.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "historial.html", {"problemas": problemas})
