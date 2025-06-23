from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import ProblemaPLForm
from .utils import export_resultado
from .models import ProblemaPL
from .solver import resolver_metodo_grafico
import json
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
    grafico = ""
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
            resultado = resolver_metodo_grafico(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                form.cleaned_data["restricciones"],
                bounds=bounds,
            )

            fig = resultado.get("fig")
            if fig is not None:
                grafico = fig.to_html(full_html=False)

            # remove non-serializable objects before rendering
            resultado = {k: v for k, v in resultado.items() if k != "fig"}
            post_data = request.POST.dict()
            form = ProblemaPLForm()
            context = {
                "form": form,
                "mensaje": mensaje,
                "resultado": resultado,
                "grafico": grafico,
                "post_data": post_data,
            }
            return render(request, "resultado.html", context)
    else:
        form = ProblemaPLForm()
    context = {
        "form": form,
        "mensaje": mensaje,
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
    """Display all ProblemaPL entries created by the logged in user with optional filters."""

    orden = request.GET.get("orden", "asc")
    if orden not in {"asc", "desc"}:
        orden = "asc"
    ordering = "-created_at" if orden == "desc" else "created_at"

    objetivo = request.GET.get("objetivo", "all")
    fecha_desde = request.GET.get("desde")
    fecha_hasta = request.GET.get("hasta")

    qs = ProblemaPL.objects.filter(user=request.user)

    if objetivo in {"max", "min"}:
        qs = qs.filter(objetivo=objetivo)

    if fecha_desde:
        try:
            qs = qs.filter(created_at__date__gte=fecha_desde)
        except ValueError:
            fecha_desde = None

    if fecha_hasta:
        try:
            qs = qs.filter(created_at__date__lte=fecha_hasta)
        except ValueError:
            fecha_hasta = None

    base_qs = qs.order_by("created_at")
    numero_por_id = {p.id: idx for idx, p in enumerate(base_qs, 1)}

    problemas = list(qs.order_by(ordering))
    for p in problemas:
        p.numero = numero_por_id.get(p.id)

    context = {
        "problemas": problemas,
        "orden": orden,
        "objetivo": objetivo,
        "desde": fecha_desde,
        "hasta": fecha_hasta,
    }

    return render(request, "historial.html", context)


@login_required
def ver_problema(request, pk):
    """Reexecute a saved problem and display the result."""
    problema = get_object_or_404(ProblemaPL, pk=pk, user=request.user)
    post_data = {
        "objetivo": problema.objetivo,
        "coef_x1": problema.coef_x1,
        "coef_x2": problema.coef_x2,
        "restricciones": json.dumps(problema.restricciones),
    }
    form = ProblemaPLForm(post_data)
    if form.is_valid():
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
        grafico = fig.to_html(full_html=False) if fig is not None else ""
        resultado = {k: v for k, v in resultado.items() if k != "fig"}
        context = {
            "form": ProblemaPLForm(),
            "mensaje": "",
            "resultado": resultado,
            "grafico": grafico,
            "post_data": post_data,
        }
        return render(request, "resultado.html", context)
    messages.error(request, "No se pudo cargar el problema seleccionado.")
    return redirect("historial")


def resultado_metodo_grafico(request):
    """Display the latest result stored in session."""
    data = request.session.get("resultado_metodo_grafico")
    if not data:
        return redirect("metodo_grafico")
    return render(request, "resultado.html", data)
