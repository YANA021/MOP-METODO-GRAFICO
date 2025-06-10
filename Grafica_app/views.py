from django.shortcuts import render
from .forms import ProblemaPLForm
from .models import ProblemaPL


def metodo_grafico(request):
    mensaje = ''
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
            form = ProblemaPLForm()
    else:
        form = ProblemaPLForm()
    return render(request, 'nuevo_problema.html', {'form': form, 'mensaje': mensaje})
