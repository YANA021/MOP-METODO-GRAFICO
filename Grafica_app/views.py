from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProblemaPLForm
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
    mensaje = ''
    resultado = None
    grafica = ''
    post_data = None
    if request.method == 'POST':
        form = ProblemaPLForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data['objetivo'],
                    coef_x1=form.cleaned_data['coef_x1'],
                    coef_x2=form.cleaned_data['coef_x2'],
                    restricciones=form.cleaned_data['restricciones'],
                )
                mensaje = 'Problema guardado correctamente.'
            resultado = resolver_metodo_grafico(
                form.cleaned_data['objetivo'],
                form.cleaned_data['coef_x1'],
                form.cleaned_data['coef_x2'],
                form.cleaned_data['restricciones'],
            )
            grafica = resultado.get('grafica', '')
            post_data = request.POST
            form = ProblemaPLForm()
    else:
        form = ProblemaPLForm()
    context = {
        'form': form,
        'mensaje': mensaje,
        'grafica': grafica,
        'resultado': resultado,
        'post_data': post_data,
    }
    return render(request, 'nuevo_problema.html', context)


def exportar_resultado(request, formato):
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ProblemaPLForm(request.POST)
    if not form.is_valid():
        return HttpResponse('Datos invalidos', status=400)

    resultado = resolver_metodo_grafico(
        form.cleaned_data['objetivo'],
        form.cleaned_data['coef_x1'],
        form.cleaned_data['coef_x2'],
        form.cleaned_data['restricciones'],
    )

    fig = resultado.get('fig')
    buffer = io.BytesIO()

    if formato == 'pdf':
        try:
            buffer.write(fig.to_image(format='pdf'))
        except Exception as e:
            return HttpResponse(f'Error generando PDF: {e}', status=500)
        content_type = 'application/pdf'
        filename = 'resultado.pdf'
    elif formato == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.append(['x1', 'x2', 'Z'])
        ws.append([resultado['x'], resultado['y'], resultado['z']])
        try:
            from openpyxl.drawing.image import Image as XLImage
            img_stream = io.BytesIO(fig.to_image(format='png'))
            img = XLImage(img_stream)
            img.anchor = 'E2'
            ws.add_image(img)
        except Exception:
            pass
        wb.save(buffer)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = 'resultado.xlsx'
    elif formato == 'word':
        doc = Document()
        doc.add_heading('Resultado del problema PL', level=1)
        doc.add_paragraph(f"x₁ = {resultado['x']:.2f}")
        doc.add_paragraph(f"x₂ = {resultado['y']:.2f}")
        doc.add_paragraph(f"Z = {resultado['z']:.2f}")
        try:
            img_stream = io.BytesIO(fig.to_image(format='png'))
            doc.add_picture(img_stream, width=Inches(5))
        except Exception as e:
            return HttpResponse(f'Error generando Word: {e}', status=500)
        doc.save(buffer)
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        filename = 'resultado.docx'
    else:
        return HttpResponse('Formato no soportado', status=400)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response




def login_view(request):
    """Handle user authentication."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home')
    else:
        form = LoginForm(request)
    return render(request, 'login.html', {'form': form})


def register(request):
    """Create a new user account."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    context = {
        'form': form,
        'title': 'Registro',
        'button_text': 'Registrarse',
        'question_text': '¿Ya tienes una cuenta?',
        'login_text': 'Iniciar sesión',
    }
    return render(request, 'register.html', context)


@login_required
def perfil_show(request):
    """Display current user's profile."""
    return render(request, 'perfil/show.html', {"user": request.user})


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
    return redirect('login') 


@login_required
def historial(request):
    """Display all ProblemaPL entries created by the logged in user."""
    problemas = ProblemaPL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'historial.html', {'problemas': problemas})
