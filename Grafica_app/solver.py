
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import plotly.graph_objects as go
from scipy.optimize import linprog

BOUND = 10.0

def _fmt(num: float) -> str:
    if abs(num - round(num)) < 1e-6:
        return f"{int(round(num))}"
    return f"{num:.1f}"

def _clip_polygon(poly: Polygon, a: float, b: float, op: str, c: float, bound: float = BOUND) -> Polygon:
    if b == 0:
        x = c / a if a != 0 else 0.0
        line = LineString([(x, -bound), (x, bound)])
    elif a == 0:
        y = c / b if b != 0 else 0.0
        line = LineString([(-bound, y), (bound, y)])
    else:
        line = LineString(
            [(-bound, (c - a * (-bound)) / b), (bound, (c - a * bound) / b)]
        )
    if op == "=":
        poly = _clip_polygon(poly, a, b, "<=", c, bound)
        return _clip_polygon(poly, a, b, ">=", c, bound)

    result = split(poly, line)
    if len(result.geoms) <= 1:
        return poly

    parts = []
    for part in result.geoms:
        rep = part.representative_point()
        val = a * rep.x + b * rep.y
        if op == "<=" and val <= c + 1e-9:
            parts.append(part)
        elif op == ">=" and val >= c - 1e-9:
            parts.append(part)

    if not parts:
        return Polygon()

    clipped = parts[0]
    for p in parts[1:]:
        clipped = clipped.union(p)
    return clipped

def _build_feasible_polygon(restricciones, bound=BOUND):
    poly = Polygon([(-bound, -bound), (bound, -bound), (bound, bound), (-bound, bound)])
    for a, b, op, c in restricciones:
        poly = _clip_polygon(poly, a, b, op, c, bound)
        if poly.is_empty:
            break
    return poly

def _candidate_vertices(restricciones):
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
    for a, b, _, c in lines:
        if a != 0:
            verts.append((c / a, 0.0))
        if b != 0:
            verts.append((0.0, c / b))
    verts.append((0.0, 0.0))
    uniq = []
    for v in verts:
        if not any(np.allclose(v, u) for u in uniq):
            uniq.append(v)
    return uniq

def _satisfies(point, restricciones):
    x, y = point
    for a, b, op, c in restricciones:
        val = a * x + b * y
        if op == "<=" and val > c + 1e-7:
            return False
        if op == ">=" and val < c - 1e-7:
            return False
        if op == "=" and abs(val - c) > 1e-7:
            return False
    return True

def build_cartesian_axes(fig, x_min, x_max, y_min, y_max):
    fig.add_shape(type="line", x0=x_min, x1=x_max, y0=0, y1=0,
                  line=dict(color="black", width=2), layer="above")
    fig.add_shape(type="line", x0=0, x1=0, y0=y_min, y1=y_max,
                  line=dict(color="black", width=2), layer="above")

    for x in range(int(x_min), int(x_max) + 1):
        if x == 0:
            continue
        fig.add_shape(type="line", x0=x, x1=x, y0=-0.15, y1=0.15,
                      line=dict(color="black", width=1))
        fig.add_trace(go.Scatter(
            x=[x], y=[-0.4],
            mode="text",
            text=[str(x)],
            textposition="middle center",
            showlegend=False,
            hoverinfo='skip'
        ))
    for y in range(int(y_min), int(y_max) + 1):
        if y == 0:
            continue
        fig.add_shape(type="line", x0=-0.15, x1=0.15, y0=y, y1=y,
                      line=dict(color="black", width=1))
        fig.add_trace(go.Scatter(
            x=[-0.4], y=[y],
            mode="text",
            text=[str(y)],
            textposition="middle center",
            showlegend=False,
            hoverinfo='skip'
        ))
    return fig

def resolver_metodo_grafico(objetivo: str, coef_x1: float, coef_x2: float, restricciones, estilo: str = "normal"):
    restr = [(float(r["coef_x1"]), float(r["coef_x2"]), r["operador"], float(r["valor"])) for r in restricciones]
    restr.extend([(1, 0, ">=", 0), (0, 1, ">=", 0)])
    poly = _build_feasible_polygon(restr)
    candidates = [v for v in _candidate_vertices(restr) if _satisfies(v, restr)]
    if not candidates:
        return {
            "status": "inviable",
            "grafica": go.Figure().to_html(
                full_html=False,
                include_plotlyjs="cdn",
                config={"responsive": True, "doubleClick": "reset"},
            ),
        }
    values = [coef_x1 * x + coef_x2 * y for x, y in candidates]
    opt_val = min(values) if objetivo == "min" else max(values)
    opt_points = [p for p, v in zip(candidates, values) if abs(v - opt_val) < 1e-6]
    vertices = [{"x": float(x), "y": float(y), "z": float(val)} for (x, y), val in zip(candidates, values)]

    status = "optimo"
    opt_segment = None
    if len(opt_points) > 1:
        status = "multiple"
        xs = [p[0] for p in opt_points]
        ys = [p[1] for p in opt_points]
        opt_segment = [(min(xs), min(ys)), (max(xs), max(ys))]

    max_x = max((v["x"] for v in vertices), default=BOUND)
    max_y = max((v["y"] for v in vertices), default=BOUND)
    x_max = max(max_x, 0) + 1
    y_max = max(max_y, 0) + 1
    plot_bound = max(x_max, y_max)
    negative_margin = min(1.0, 0.1 * plot_bound) * 1.2
    x_min = -negative_margin
    y_min = -negative_margin

    fig = go.Figure()
    if estilo == "cruz":
        fig = build_cartesian_axes(fig, x_min, x_max, y_min, y_max)

    x = np.linspace(x_min, plot_bound, 400)
    for a, b_, op, c in restr:
        if b_ == 0:
            x_line = np.full_like(x, c / a)
            y_line = x
        else:
            x_line = x
            y_line = (c - a * x) / b_
        fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name=f"{a}x₁ + {b_}x₂ {op} {c}"))

    if not poly.is_empty and hasattr(poly, "exterior"):
        xs, ys = poly.exterior.xy
        fig.add_trace(go.Scatter(x=list(xs), y=list(ys), fill="toself", name="Región factible", opacity=0.3))
        for vx, vy in zip(xs, ys):
            fig.add_trace(go.Scatter(x=[vx], y=[vy], mode="markers+text", text=[f"({_fmt(vx)}, {_fmt(vy)})"], textposition="top center", showlegend=False))

    x_opt, y_opt = opt_points[0]
    fig.add_trace(go.Scatter(x=[x_opt], y=[y_opt], mode="markers+text", text=[f"({_fmt(x_opt)}, {_fmt(y_opt)})"], name="Óptimo"))

    z_line_y = (opt_val - coef_x1 * x) / coef_x2 if coef_x2 != 0 else np.full_like(x, opt_val / coef_x2)
    fig.add_trace(go.Scatter(x=x, y=z_line_y, mode="lines", line=dict(dash="dash"), name="Función objetivo"))

    if estilo == "cruz":
        fig.update_layout(
            xaxis=dict(visible=False, range=[x_min, x_max], fixedrange=True),
            yaxis=dict(visible=False, range=[y_min, y_max], fixedrange=True),
            plot_bgcolor="white",
            autosize=True,
            height=600,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
    else:
        fig.update_layout(
            template="plotly",
            xaxis=dict(
                title="x₁", range=[x_min, x_max],
                showgrid=True, gridcolor="lightgray",
                zeroline=True, zerolinewidth=2, zerolinecolor="black",
                showline=True, linecolor="black", mirror=True,
                ticks="inside", ticklen=6, tickcolor="black",
            ),
            yaxis=dict(
                title="x₂", range=[y_min, y_max],
                showgrid=True, gridcolor="lightgray",
                zeroline=True, zerolinewidth=2, zerolinecolor="black",
                showline=True, linecolor="black", mirror=True,
                ticks="inside", ticklen=6, tickcolor="black",
            ),
            plot_bgcolor="white",
            autosize=True,
            height=600,
            margin=dict(l=40, r=40, t=40, b=40),
            dragmode="zoom",
        )

    return {
        "status": status,
        "x": x_opt,
        "y": y_opt,
        "z": opt_val,
        "vertices": vertices,
        "opt_points": opt_points,
        "opt_segment": opt_segment,
        "grafica": fig.to_html(
            full_html=False,
            include_plotlyjs="cdn",
            config={"responsive": True, "doubleClick": "reset"},
        ),
        "fig": fig,
    }
