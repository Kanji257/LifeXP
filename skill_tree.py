"""
skill_tree.py — LifeXP skill tree rendering.
Fixed: legend placed in separate axes below the tree (no overlap), clean labels.
"""

import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

CATEGORY_COLORS = {
    "Physical":   "#FF6B6B",
    "Mental":     "#4ECDC4",
    "Financial":  "#FFE66D",
    "Social":     "#A8E6CF",
    "Spiritual":  "#C3A6FF",
    "Creative":   "#FFB347",
    "Default":    "#B0BEC5",
}
ROOT_COLOR = "#555577"


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
            G.add_node(skill_node, label=short, node_type="skill", category=category)
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


def render_skill_tree(G: nx.DiGraph, skill_data: dict) -> plt.Figure:
    root = "LIFE"
    total_skills = sum(len(s) for s in skill_data.values())
    n_cats = len(skill_data)

    fig_w = max(12, total_skills * 1.9)
    # Extra height at bottom for the legend row
    fig_h = max(6, n_cats * 1.8) + 1.2

    tree_width = max(3.5, total_skills * 0.9)
    pos = _hierarchy_pos(G, root, width=tree_width, vert_gap=0.52)

    # Two rows: tree on top, legend strip at bottom
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor="#0F0F1A")
    gs = gridspec.GridSpec(
        2, 1,
        height_ratios=[fig_h - 1.2, 1.2],
        hspace=0.05,
        figure=fig,
    )

    ax = fig.add_subplot(gs[0])
    ax_legend = fig.add_subplot(gs[1])
    ax.set_facecolor("#0F0F1A")
    ax_legend.set_facecolor("#0F0F1A")
    ax_legend.axis("off")

    # Node styling
    node_colors, node_sizes, labels = [], [], {}
    for node in G.nodes():
        data = G.nodes[node]
        ntype = data.get("node_type", "skill")
        labels[node] = data.get("label", node)
        if ntype == "root":
            node_colors.append(ROOT_COLOR)
            node_sizes.append(2800)
        elif ntype == "category":
            cat = data.get("category", "Default")
            node_colors.append(CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Default"]))
            node_sizes.append(2000)
        else:
            cat = data.get("category", "Default")
            node_colors.append(CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Default"]))
            node_sizes.append(1500)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#334466", arrows=False, width=1.5, alpha=0.7)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.92)

    root_nodes  = {n: labels[n] for n in G.nodes() if G.nodes[n].get("node_type") == "root"}
    cat_nodes   = {n: labels[n] for n in G.nodes() if G.nodes[n].get("node_type") == "category"}
    skill_nodes = {n: labels[n] for n in G.nodes() if G.nodes[n].get("node_type") == "skill"}
    nx.draw_networkx_labels(G, pos, labels=root_nodes,  ax=ax, font_size=9,  font_color="white", font_weight="bold")
    nx.draw_networkx_labels(G, pos, labels=cat_nodes,   ax=ax, font_size=8,  font_color="white", font_weight="bold")
    nx.draw_networkx_labels(G, pos, labels=skill_nodes, ax=ax, font_size=7,  font_color="white")

    ax.set_title("LifeXP Skill Tree", color="white", fontsize=13, fontweight="bold",
                 pad=10, fontfamily="monospace")
    ax.axis("off")

    # Legend in the separate bottom strip — horizontal, centred
    patches = [
        mpatches.Patch(color=CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Default"]), label=cat)
        for cat in skill_data.keys()
    ]
    ax_legend.legend(
        handles=patches,
        loc="center",
        ncol=min(len(patches), 6),   # up to 6 per row
        facecolor="#1A1A2E",
        edgecolor="#2A2A4A",
        labelcolor="white",
        fontsize=9,
        framealpha=0.9,
        borderpad=0.7,
        columnspacing=1.2,
    )

    fig.tight_layout(pad=1.2)
    return fig
