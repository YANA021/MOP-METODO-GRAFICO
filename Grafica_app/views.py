from django.shortcuts import render
from django.http import HttpResponse
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
            request.session['ultimo_problema'] = {
                'objetivo': form.cleaned_data['objetivo'],
                'coef_x1': form.cleaned_data['coef_x1'],
                'coef_x2': form.cleaned_data['coef_x2'],
                'restricciones': form.cleaned_data['restricciones'],
            }
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


def exportar_resultado(request, formato):
    problema = request.session.get('ultimo_problema')
    if not problema:
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('metodo_grafico'))

    resultado = resolver_metodo_grafico(
        problema['objetivo'],
        problema['coef_x1'],
        problema['coef_x2'],
        problema['restricciones'],
    )

    objetivo_text = 'Maximizar' if problema['objetivo'] == 'max' else 'Minimizar'

    if formato == 'excel':
        import pandas as pd
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            resumen = pd.DataFrame({
                'Parametro': ['Objetivo', 'Funcion Z', 'x1', 'x2', 'Z'],
                'Valor': [
                    objetivo_text,
                    f"Z = {problema['coef_x1']}x1 + {problema['coef_x2']}x2",
                    round(resultado['x'], 4),
                    round(resultado['y'], 4),
                    round(resultado['z'], 4),
                ]
            })
            resumen.to_excel(writer, index=False, sheet_name='Resumen')
            pd.DataFrame(problema['restricciones']).to_excel(
                writer, index=False, sheet_name='Restricciones'
            )
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="resultado.xlsx"'
        return response

    if formato == 'word':
        from docx import Document
        from io import BytesIO
        import base64
        doc = Document()
        doc.add_heading('Resultado PL', 0)
        doc.add_paragraph(f'Objetivo: {objetivo_text}')
        doc.add_paragraph(
            f"Funcion objetivo: Z = {problema['coef_x1']}x1 + {problema['coef_x2']}x2"
        )
        table = doc.add_table(rows=1, cols=4)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Coef x1'
        hdr_cells[1].text = 'Coef x2'
        hdr_cells[2].text = 'Operador'
        hdr_cells[3].text = 'Valor'
        for r in problema['restricciones']:
            row_cells = table.add_row().cells
            row_cells[0].text = str(r['coef_x1'])
            row_cells[1].text = str(r['coef_x2'])
            row_cells[2].text = r['operador']
            row_cells[3].text = str(r['valor'])

        doc.add_paragraph(
            f"Solucion optima: x1={resultado['x']:.2f}, x2={resultado['y']:.2f}, Z={resultado['z']:.2f}"
        )

        try:
            img_bytes = resultado['figure'].to_image(format='png')
            from docx.shared import Inches
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            doc.add_picture(tmp_path, width=Inches(4))
        except Exception:
            pass

        buffer = BytesIO()
        doc.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="resultado.docx"'
        return response

    if formato == 'pdf':
        from io import BytesIO
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        import base64

        try:
            img_bytes = resultado['figure'].to_image(format='png')
            grafica_b64 = base64.b64encode(img_bytes).decode('utf-8')
        except Exception:
            grafica_b64 = None

        html = render_to_string(
            'export_resultado.html',
            {
                'objetivo': objetivo_text,
                'coef_x1': problema['coef_x1'],
                'coef_x2': problema['coef_x2'],
                'restricciones': problema['restricciones'],
                'resultado': resultado,
                'grafica_b64': grafica_b64,
            }
        )
        buffer = BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resultado.pdf"'
        return response

    from django.http import HttpResponseBadRequest
    return HttpResponseBadRequest('Formato no soportado')
