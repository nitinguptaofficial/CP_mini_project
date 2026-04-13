"""
Server-side chart generation with matplotlib.
Every public function returns a base64-encoded PNG string suitable for embedding
in HTML via  <img src="data:image/png;base64,{{ chart_b64 }}">.
"""

import base64
import io

import matplotlib

matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt


# ── colour palette ──────────────────────────────────────────────────────────
INDIGO = "#4f46e5"
VIOLET = "#8b5cf6"
RED = "#ef4444"
INDIGO_LIGHT = "rgba(79,70,229,0.25)"
BG_COLOR = "#f8f9fa"
TEXT_COLOR = "#1e1e2f"

# ── shared styling ──────────────────────────────────────────────────────────

def _apply_style(ax, fig):
    """Apply a consistent clean look to every chart."""
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)


def _fig_to_base64(fig) -> str:
    """Render the figure to a tight PNG and return as base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ── public chart builders ──────────────────────────────────────────────────

def bar_chart(labels, values, *, title="", ylabel="", color=INDIGO) -> str:
    """Vertical bar chart – used for top performers, subject comparison, etc."""
    if not labels:
        return _empty_chart(title)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    _apply_style(ax, fig)

    bars = ax.bar(labels, values, color=color, width=0.5, edgecolor="none", zorder=3)
    for bar in bars:
        bar.set_clip_on(False)

    # value labels on top of each bar
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{val}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=TEXT_COLOR,
            fontweight="bold",
        )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(0, max(values) * 1.15 if values else 1)
    ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    fig.tight_layout()
    return _fig_to_base64(fig)


def line_chart(labels, values, *, title="", ylabel="", color=INDIGO) -> str:
    """Line / area chart – used for performance trends."""
    if not labels:
        return _empty_chart(title)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    _apply_style(ax, fig)

    ax.plot(labels, values, color=color, linewidth=2, marker="o", markersize=5, zorder=3)
    ax.fill_between(labels, values, alpha=0.15, color=color, zorder=2)

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    fig.tight_layout()
    return _fig_to_base64(fig)


def _empty_chart(title: str) -> str:
    """Return a placeholder image when there is no data."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    _apply_style(ax, fig)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.text(0.5, 0.5, "No data available", ha="center", va="center",
            fontsize=14, color="#9ca3af", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return _fig_to_base64(fig)
