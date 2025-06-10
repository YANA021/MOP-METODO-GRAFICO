from django.shortcuts import render
from django.http import HttpResponse
from .forms import ProblemaPLForm
from .models import ProblemaPL
from .solver import resolver_metodo_grafico
import io
from openpyxl import Workbook
from docx import Document
from docx.shared import Inches


def metodo_grafico(request):
    mensaje = ''
    resultado = None
    grafica = ''
    post_data = None
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
        buffer.write(fig.to_image(format='pdf'))
        content_type = 'application/pdf'
        filename = 'resultado.pdf'
    elif formato == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.append(['x1', 'x2', 'Z'])
        ws.append([resultado['x'], resultado['y'], resultado['z']])
        wb.save(buffer)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = 'resultado.xlsx'
    elif formato == 'word':
        doc = Document()
        doc.add_heading('Resultado del problema PL', level=1)
        doc.add_paragraph(f"x₁ = {resultado['x']:.2f}")
        doc.add_paragraph(f"x₂ = {resultado['y']:.2f}")
        doc.add_paragraph(f"Z = {resultado['z']:.2f}")
        img_stream = io.BytesIO(fig.to_image(format='png'))
        doc.add_picture(img_stream, width=Inches(5))
        doc.save(buffer)
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        filename = 'resultado.docx'
    else:
        return HttpResponse('Formato no soportado', status=400)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
