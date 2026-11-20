import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ENCOURAGEMENT = "welcome_offer"
TREATMENT = "enrolled"
OUTCOME = "spend90"
CONFOUNDERS = {"income", "deal_seeking", "store_region"}
COLLIDERS = {"survey_responded"}
MEDIATORS = {"store_visits"}
AFTER_TREATMENT = {"store_visits", "survey_response"}
LATENT = "deal_seeking"

def build_dag() -> nx.DiGraph:
    """Return the project DAG. Add every arrow you can justify."""
    # initialize directed graph
    g = nx.DiGraph()
    # Add nodes
    g.add_node(TREATMENT)
    g.add_node(OUTCOME)
    g.add_node(LATENT)

    for node in CONFOUNDERS:
        g.add_node(node)

    for node in COLLIDERS:
        g.add_node(node)

    for node in MEDIATORS:
        g.add_node(node)

    # Add edges
    # edge for welcome offer to treatment
    g.add_edge(ENCOURAGEMENT, TREATMENT)

    # causal relationship from treatment to outcome
    g.add_edge(TREATMENT, OUTCOME)

    # causal relationships from confounders to treatment and outcome
    for node in CONFOUNDERS:
        g.add_edge(node, TREATMENT)
        g.add_edge(node, OUTCOME)

    # causal relationships from mediators to outcome
    for node in MEDIATORS:
        g.add_edge(TREATMENT, node)
        g.add_edge(node, OUTCOME)

    # causal relationships from colliders to treatment and outcome
    for node in COLLIDERS:
        g.add_edge(TREATMENT, node)
        g.add_edge(OUTCOME, node)

    return g

def plot_dag(g: nx.DiGraph, ax=None):
    """Draw the DAG. Style latent nodes differently from observed ones."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 8))

    # Keep node placement consistent between runs.
    pos = nx.spring_layout(g, seed=42)

    # Separate key nodes from the remaining variables for styling.
    encouragement_nodes = [node for node in g.nodes if node == ENCOURAGEMENT]
    treatment_outcome_nodes = [
        node for node in g.nodes if node in {TREATMENT, OUTCOME}
    ]
    latent_nodes = [node for node in g.nodes if node == LATENT]
    other_nodes = [
        node
        for node in g.nodes
        if node not in {ENCOURAGEMENT, TREATMENT, OUTCOME, LATENT}
    ]

    # Highlight encouragement and treatment/outcome; show other nodes in grey.
    for nodelist, color in (
        (encouragement_nodes, "lightgreen"),
        (treatment_outcome_nodes, "thistle"),
        (other_nodes, "lightgrey"),
    ):
        if nodelist:
            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=nodelist,
                node_color=color,
                node_size=1800,
                ax=ax,
            )

    # Keep latent nodes grey, but use a dotted outline to distinguish them.
    if latent_nodes:
        latent_collection = nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=latent_nodes,
            node_color="lightgrey",
            node_size=1800,
            ax=ax,
        )
        latent_collection.set_linestyle(":")

    # Show causal direction with arrows and identify nodes with labels.
    nx.draw_networkx_edges(
        g,
        pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
        ax=ax,
    )
    nx.draw_networkx_labels(g, pos, ax=ax)

    ax.set_title("Causal DAG")
    ax.set_axis_off()
    return ax

def backdoor_paths(g: nx.DiGraph, treatment: str, outcome: str) -> list[list[str]]:
    """Return all backdoor paths: paths from treatment to outcome whose
    first edge points INTO the treatment."""
    undirected = g.to_undirected()
    paths = []

    for parent in g.predecessors(treatment):
        if parent == outcome:
            continue
        for path in nx.all_simple_paths(undirected, treatment, outcome):
            if len(path) >= 3 and path[1] == parent:
                paths.append(path)

    # Preserve a stable, readable order in plots and notebook output.
    return sorted(paths, key=lambda path: tuple(path))



# Visual version of the DAG for reference.
# --- Styles: (fill, edge, title text, subtitle text) ---------------------------------
STYLES = {
    "neutral": ("#F1EFE8", "#888780", "#2C2C2A", "#5F5E5A"),
    "treat_outcome": ("#EEEDFE", "#534AB7", "#3C3489", "#534AB7"),
    "randomized": ("#E1F5EE", "#0F6E56", "#085041", "#0F6E56"),
}
ARROW_COLOR = "#5F5E5A"

# --- Boxes: name -> (subtitle, x, y, width, height, style, dashed) -------------------
BOXES = {
    "income":           ("observed, before", 130, 30, 120, 48, "neutral", False),
    "deal_seeking":     ("latent, before",   280, 30, 120, 48, "neutral", True),
    "store_region":     ("observed, before", 430, 30, 120, 48, "neutral", False),
    "welcome_offer":    ("randomized",        30, 190, 110, 48, "randomized", False),
    "enrolled":         ("treatment",        190, 190, 120, 48, "treat_outcome", False),
    "spend90":          ("outcome",          500, 190, 120, 48, "treat_outcome", False),
    "store_visits":     ("observed, after",  340, 290, 130, 48, "neutral", False),
    "survey_responded": ("observed, after",  340, 380, 130, 48, "neutral", False),
}

# --- Edges: (source, target, start_xy, end_xy) ---------------------------------------
EDGES = [
    ("income", "enrolled", (190, 82), (210, 186)),
    ("income", "spend90", (210, 82), (520, 186)),
    ("deal_seeking", "enrolled", (330, 82), (250, 186)),
    ("deal_seeking", "spend90", (350, 82), (560, 186)),
    ("store_region", "enrolled", (480, 82), (290, 186)),
    ("store_region", "spend90", (500, 82), (600, 186)),
    ("welcome_offer", "enrolled", (142, 214), (188, 214)),
    ("enrolled", "spend90", (312, 214), (498, 214)),
    ("enrolled", "store_visits", (285, 242), (338, 308)),
    ("store_visits", "spend90", (472, 308), (528, 242)),
    ("enrolled", "survey_responded", (262, 242), (338, 400)),
    ("spend90", "survey_responded", (585, 242), (472, 400)),
]

LEGEND = "Purple: treatment and outcome. Teal: randomized. Dashed: unobserved."


def draw_reference_dag(ax=None):
    """Draw the reference DAG. Returns (fig, ax)."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 7))
    else:
        fig = ax.figure

    ax.set_xlim(0, 680)
    ax.set_ylim(470, 0)  # flip y so (0, 0) is top-left, like SVG
    ax.set_aspect("equal")
    ax.axis("off")

    # Arrows first so boxes sit on top of any line ends
    for _src, _dst, start, end in EDGES:
        ax.add_patch(
            FancyArrowPatch(
                start, end,
                arrowstyle="-|>", mutation_scale=11,
                color=ARROW_COLOR, linewidth=1.1,
                shrinkA=0, shrinkB=0, zorder=1,
            )
        )

    for name, (subtitle, x, y, w, h, style, dashed) in BOXES.items():
        fill, edge, title_c, sub_c = STYLES[style]
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0,rounding_size=6",
                facecolor=fill, edgecolor=edge, linewidth=1.2,
                linestyle=(0, (4, 3)) if dashed else "-",
                zorder=2,
            )
        )
        cx = x + w / 2
        ax.text(cx, y + 18, name, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=title_c, zorder=3)
        ax.text(cx, y + 35, subtitle, ha="center", va="center",
                fontsize=8.5, color=sub_c, zorder=3)

    ax.text(30, 456, LEGEND, ha="left", va="center", fontsize=8.5, color="#5F5E5A")

    plt.show()
    return fig, ax