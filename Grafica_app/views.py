from django.shortcuts import render
from .forms import ProblemaPLForm
from .models import ProblemaPL
from .solver import resolver_metodo_grafico


def metodo_grafico(request):
    mensaje = ''
    resultado = None
    grafica = ''
    if request.method == 'POST':
        form = ProblemaPLForm(request.POST)
        if form.is_valid():
            ProblemaPL.objects.create(
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
            form = ProblemaPLForm()
    else:
        form = ProblemaPLForm()
    context = {
        'form': form,
        'mensaje': mensaje,
        'grafica': grafica,
        'resultado': resultado,
    }
    return render(request, 'nuevo_problema.html', context)
