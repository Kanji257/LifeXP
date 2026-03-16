"""
skill_tree.py — LifeXP interactive skill tree using Plotly.
Nodes glow gold when mastered. Hover shows skill name and quest progress.
"""

import networkx as nx
import plotly.graph_objects as go

CATEGORY_COLORS = {
    "Physical":   "#FF6B6B",
    "Mental":     "#4ECDC4",
    "Financial":  "#FFE66D",
    "Social":     "#A8E6CF",
    "Spiritual":  "#C3A6FF",
    "Creative":   "#FFB347",
    "Default":    "#B0BEC5",
}
ROOT_COLOR = "#7C6A9A"
MASTERED_COLOR = "#F59E0B"


def build_skill_tree(skill_data: dict) -> nx.DiGraph:
    G = nx.DiGraph()
    root = "LIFE"
    G.add_node(root, label="LIFE", node_type="root")
    for category, skills in skill_data.items():
        cat_node = f"CAT_{category}"
        G.add_node(cat_node, label=category.upper(), node_type="category", category=category)
        G.add_edge(root, cat_node)
        for skill in skills:
            skill_node = f"SKILL_{category}_{skill}"
            short = skill if len(skill) <= 14 else skill[:12] + ".."
            G.add_node(skill_node, label=short, node_type="skill", category=category, full_name=skill)
            G.add_edge(cat_node, skill_node)
    return G


def _hierarchy_pos(G, root, width=4.0, vert_gap=0.5):
    pos = {}
    def _recurse(node, left, right, y):
        children = list(G.successors(node))
        pos[node] = ((left + right) / 2, y)
        if children:
            dx = (right - left) / len(children)
            nx_ = left
            for child in children:
                _recurse(child, nx_, nx_ + dx, y - vert_gap)
                nx_ += dx
    _recurse(root, 0, width, 0)
    return pos


def render_skill_tree(G: nx.DiGraph, skill_data: dict,
                       mastered_skills: set = None,
                       quest_progress: dict = None) -> go.Figure:
    """
    Render an interactive Plotly skill tree.
    mastered_skills: set of skill names that are mastered (glow gold)
    quest_progress: {skill_name: (done, total)} for hover tooltip
    """
    if mastered_skills is None:
        mastered_skills = set()
    if quest_progress is None:
        quest_progress = {}

    root = "LIFE"
    total_skills = sum(len(s) for s in skill_data.values())
    tree_width = max(3.5, total_skills * 0.9)
    pos = _hierarchy_pos(G, root, width=tree_width, vert_gap=0.55)

    # Build edge traces
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1.5, color="#334466"),
        hoverinfo="none",
    )

    # Build node traces — separate by type for different styling
    node_groups = {"root": [], "category": [], "skill_normal": [], "skill_mastered": []}

    for node in G.nodes():
        data = G.nodes[node]
        ntype = data.get("node_type", "skill")
        x, y = pos[node]
        label = data.get("label", node)
        full_name = data.get("full_name", label)
        category = data.get("category", "Default")

        if ntype == "root":
            node_groups["root"].append((x, y, label, "LifeXP Root", ROOT_COLOR, 28))
        elif ntype == "category":
            color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["Default"])
            node_groups["category"].append((x, y, label, f"Category: {category}", color, 22))
        else:
            is_mastered = full_name in mastered_skills
            done, total = quest_progress.get(full_name, (0, 0))
            hover = f"{full_name}<br>{'✨ MASTERED' if is_mastered else f'{done}/{total} quests'}"
            color = MASTERED_COLOR if is_mastered else CATEGORY_COLORS.get(category, CATEGORY_COLORS["Default"])
            group = "skill_mastered" if is_mastered else "skill_normal"
            node_groups[group].append((x, y, label, hover, color, 16))

    traces = [edge_trace]

    group_configs = {
        "root":          dict(size=32, symbol="circle", line_width=2, line_color="#A78BFA", opacity=0.95),
        "category":      dict(size=24, symbol="circle", line_width=1.5, line_color="white", opacity=0.9),
        "skill_normal":  dict(size=18, symbol="circle", line_width=1, line_color="white", opacity=0.85),
        "skill_mastered":dict(size=20, symbol="star", line_width=2, line_color="#FCD34D", opacity=1.0),
    }

    for group_name, nodes in node_groups.items():
        if not nodes:
            continue
        cfg = group_configs[group_name]
        xs = [n[0] for n in nodes]
        ys = [n[1] for n in nodes]
        labels = [n[2] for n in nodes]
        hovers = [n[3] for n in nodes]
        colors = [n[4] for n in nodes]

        traces.append(go.Scatter(
            x=xs, y=ys,
            mode="markers+text",
            marker=dict(
                size=cfg["size"],
                color=colors,
                symbol=cfg["symbol"],
                line=dict(width=cfg["line_width"], color=cfg["line_color"]),
                opacity=cfg["opacity"],
            ),
            text=labels,
            textposition="bottom center" if group_name != "root" else "middle center",
            textfont=dict(
                size=9 if group_name == "skill_normal" or group_name == "skill_mastered" else 10,
                color="white",
                family="monospace",
            ),
            hovertext=hovers,
            hoverinfo="text",
            hoverlabel=dict(
                bgcolor="#1A1A2E",
                bordercolor="#A78BFA",
                font=dict(color="white", size=12),
            ),
            showlegend=False,
        ))

    # Legend as annotation boxes
    annotations = []
    legend_x = 0.01
    for cat, color in CATEGORY_COLORS.items():
        if cat in skill_data:
            annotations.append(dict(
                x=legend_x, y=-0.08,
                xref="paper", yref="paper",
                text=f"<span style='color:{color}'>■</span> {cat}",
                showarrow=False,
                font=dict(color="white", size=10),
                align="left",
            ))
            legend_x += 0.18

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="#0F0F1A",
        plot_bgcolor="#0F0F1A",
        margin=dict(l=20, r=20, t=40, b=60),
        height=420,
        title=dict(
            text="LifeXP Skill Tree",
            font=dict(color="white", size=14, family="monospace"),
            x=0.5,
        ),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=annotations,
        hovermode="closest",
    )
    return fig
