# MOP-METODO-GRAFICO
Proyecto de la Asignatura de Metodos de Optimizacion.

## Etapa 7: Requisitos no funcionales clave
- **RNF-01 – Responsive móvil**: formularios y gráficas se adaptan a móviles gracias a Bootstrap 5.
- **RNF-02 – Rápida respuesta**: el cálculo y renderizado tardan menos de 2 segundos.
- **RNF-03 – Intuitivo y educativo**: la interfaz incluye ayuda contextual con modales y tooltips.
- **RNF-04 – Seguridad**: se validan formularios en el servidor y se protege con CSRF.
- **RNF-05 – Navegadores y sistemas**: probado en Chrome, Firefox, Edge y móviles Android/iOS.
- **RNF-06 – Modular y escalable**: separamos utilidades en `utils.py`, vistas en `views.py` y formularios en `forms.py`.
- **RNF-07 – Accesibilidad**: contraste alto y soporte para lectores de pantalla con atributos ARIA.

## Centrar ejes en Plotly
Para que los ejes y los marcadores se ubiquen en el origen, actualiza el layout de la figura de la siguiente manera:

```python
fig.update_layout(
    xaxis=dict(
        title='x₁',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black',
        showline=True,
        linecolor='black',
        mirror=True,
        ticks='inside',
        position=0,
        range=[xmin, xmax],
        anchor='y',
    ),
    yaxis=dict(
        title='x₂',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black',
        showline=True,
        linecolor='black',
        mirror=True,
        ticks='inside',
        position=0,
        range=[ymin, ymax],
        anchor='x',
    ),
    plot_bgcolor='white',
)
```

## Zoom por arrastre en la vista cartesiana
La vista cartesiana ahora permite acercar una región dibujando un rectángulo.
Esto se logra habilitando `dragmode="zoom"` y evitando fijar la proporción de
los ejes, por lo que el usuario puede seleccionar libremente el área de interés
y mantener el nivel de zoom hasta que decida restablecerlo.

## Interfaz mejorada

El proyecto incluye un modo claro/oscuro que detecta automáticamente la preferencia del sistema.
Las transiciones entre modos son suaves y el contenido principal se presenta dentro de tarjetas con efecto *glassmorphism*.
Al añadir restricciones se muestra una animación de aparición y la interfaz despliega un spinner mientras se procesan los formularios.
