import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import plotly.graph_objects as go
from scipy.optimize import linprog


BOUND = 10.0


def _clip_polygon(poly: Polygon, a: float, b: float, op: str, c: float, bound: float = BOUND) -> Polygon:
    """Clip a polygon with the half-plane defined by ``a*x + b*y (op) c``."""
    if b == 0:
        x = c / a if a != 0 else 0.0
        line = LineString([(x, -bound), (x, bound)])
    elif a == 0:
        y = c / b if b != 0 else 0.0
        line = LineString([(-bound, y), (bound, y)])
    else:
        line = LineString([(-bound, (c - a * (-bound)) / b), (bound, (c - a * bound) / b)])

    if op == '=':
        poly = _clip_polygon(poly, a, b, '<=', c, bound)
        return _clip_polygon(poly, a, b, '>=', c, bound)

    result = split(poly, line)
    if len(result.geoms) <= 1:
        return poly

    parts = []
    for part in result.geoms:
        rep = part.representative_point()
        val = a * rep.x + b * rep.y
        if op == '<=' and val <= c + 1e-9:
            parts.append(part)
        elif op == '>=' and val >= c - 1e-9:
            parts.append(part)

    if not parts:
        return Polygon()

    clipped = parts[0]
    for p in parts[1:]:
        clipped = clipped.union(p)
    return clipped


def _build_feasible_polygon(restricciones, bound=BOUND):
    """Return a polygon approximating the feasible region."""
    poly = Polygon([(-bound, -bound), (bound, -bound), (bound, bound), (-bound, bound)])
    for a, b, op, c in restricciones:
        poly = _clip_polygon(poly, a, b, op, c, bound)
        if poly.is_empty:
            break
    return poly


def _candidate_vertices(restricciones):
    """Return intersection points of all constraint lines."""
    lines = [(float(r[0]), float(r[1]), r[2], float(r[3])) for r in restricciones]
    verts = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a1, b1, _, c1 = lines[i]
            a2, b2, _, c2 = lines[j]
            A = np.array([[a1, b1], [a2, b2]], dtype=float)
            if abs(np.linalg.det(A)) < 1e-9:
                continue
            x, y = np.linalg.solve(A, np.array([c1, c2], dtype=float))
            verts.append((x, y))
    # axis intercepts
    for a, b, _, c in lines:
        if a != 0:
            verts.append((c / a, 0.0))
        if b != 0:
            verts.append((0.0, c / b))
    verts.append((0.0, 0.0))
    # remove duplicates
    uniq = []
    for v in verts:
        if not any(np.allclose(v, u) for u in uniq):
            uniq.append(v)
    return uniq


def _satisfies(point, restricciones):
    x, y = point
    for a, b, op, c in restricciones:
        val = a * x + b * y
        if op == '<=' and val > c + 1e-7:
            return False
        if op == '>=' and val < c - 1e-7:
            return False
        if op == '=' and abs(val - c) > 1e-7:
            return False
    return True


def resolver_metodo_grafico(objetivo: str, coef_x1: float, coef_x2: float, restricciones):
    """Resolve a two variable linear program using a graphical approach."""
    # Build full list of constraints, including non-negativity
    restr = [(float(r['coef_x1']), float(r['coef_x2']), r['operador'], float(r['valor'])) for r in restricciones]
    restr.extend([(1, 0, '>=', 0), (0, 1, '>=', 0)])

    # Determine polygon region for plotting
    poly = _build_feasible_polygon(restr)

    # collect feasible vertices
    candidates = [v for v in _candidate_vertices(restr) if _satisfies(v, restr)]

    if not candidates:
        return {
            'status': 'inviable',
            'grafica': go.Figure().to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})
        }

    # Evaluate objective function
    values = [coef_x1 * x + coef_x2 * y for x, y in candidates]
    if objetivo == 'min':
        opt_val = min(values)
    else:
        opt_val = max(values)
    opt_points = [p for p, v in zip(candidates, values) if abs(v - opt_val) < 1e-6]

    vertices = [
        {
            'x': float(x),
            'y': float(y),
            'z': float(val),
        }
        for (x, y), val in zip(candidates, values)
    ]

    status = 'optimo'
    opt_segment = None
    if len(opt_points) > 1:
        status = 'multiple'
        # take extreme points of the optimal segment for reference
        xs = [p[0] for p in opt_points]
        ys = [p[1] for p in opt_points]
        p_min = (min(xs), min(ys))
        p_max = (max(xs), max(ys))
        opt_segment = [p_min, p_max]

    # Use linprog to detect unboundedness
    A = []
    b = []
    for a, b_, op, c in restr:
        if op == '<=':
            A.append([a, b_])
            b.append(c)
        elif op == '>=':
            A.append([-a, -b_])
            b.append(-c)
        elif op == '=':
            A.append([a, b_])
            b.append(c)
            A.append([-a, -b_])
            b.append(-c)
    A = np.array(A)
    b = np.array(b)
    c_obj = np.array([-coef_x1, -coef_x2]) if objetivo == 'max' else np.array([coef_x1, coef_x2])
    res = linprog(c_obj, A_ub=A, b_ub=b, method='highs')
    if res.status == 3:
        status = 'no acotada'

    # Determine axis limits based on feasible vertices
    max_x = max((v['x'] for v in vertices), default=BOUND)
    max_y = max((v['y'] for v in vertices), default=BOUND)
    x_max = max(max_x, 0) + 1
    y_max = max(max_y, 0) + 1

    x_min = -1
    y_min = -1

    plot_bound = max(x_max, y_max)

    # Prepare plot
    fig = go.Figure()
    x = np.linspace(x_min, plot_bound, 400)
    for a, b_, op, c in restr:
        if b_ == 0:
            x_line = np.full_like(x, c / a)
            y_line = x
        else:
            x_line = x
            y_line = (c - a * x) / b_
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=f'{a}x₁ + {b_}x₂ {op} {c}',
                legendgroup='restricciones',
            )
        )

    if not poly.is_empty and hasattr(poly, 'exterior'):
        xs, ys = poly.exterior.xy
        fig.add_trace(
            go.Scatter(
                x=list(xs),
                y=list(ys),
                fill='toself',
                name='Región factible',
                opacity=0.3,
                legendgroup='region',
            )
        )
        for vx, vy in zip(xs, ys):
            fig.add_trace(
                go.Scatter(
                    x=[vx],
                    y=[vy],
                    mode='markers+text',
                    text=[f"({vx:.2f}, {vy:.2f})"],
                    textposition='top center',
                    legendgroup='intersecciones',
                    showlegend=False,
                )
            )

    x_opt, y_opt = opt_points[0]
    fig.add_trace(
        go.Scatter(
            x=[x_opt],
            y=[y_opt],
            mode='markers+text',
            text=[f"({x_opt:.2f}, {y_opt:.2f})"],
            name='Óptimo',
            legendgroup='optimo',
        )
    )
    z_line_y = (opt_val - coef_x1 * x) / coef_x2 if coef_x2 != 0 else np.full_like(x, opt_val / coef_x2)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=z_line_y,
            mode='lines',
            line=dict(dash='dash'),
            name='Función objetivo',
            legendgroup='objetivo',
        )
    )

    fig.update_layout(
        template='plotly',
        xaxis_title='x₁',
        yaxis_title='x₂',
        xaxis=dict(
            range=[x_min, x_max],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            showline=True,
        ),
        yaxis=dict(
            range=[y_min, y_max],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            showline=True,
        ),
        autosize=True,
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        responsive=True,
    )

    return {
        'status': status,
        'x': x_opt,
        'y': y_opt,
        'z': opt_val,
        'vertices': vertices,
        'opt_points': opt_points,
        'opt_segment': opt_segment,
        'grafica': fig.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True}),
        'fig': fig,
    }
