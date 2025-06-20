import matplotlib.pyplot as plt
import numpy as np


def gradient_color(score: float) -> str:
    s = max(0.0, min(1.0, score**2))

    if s == 1.0:
        return "#3bb143"  # hardcoded for score 1.0
    # define key colors
    r1, g1, b1 = 0xCC, 0x00, 0x00      # #CC0000 (red)
    r_mid, g_mid, b_mid = 0xFF, 0xD7, 0x00  # #FFD700 (golden yellow)
    r2, g2, b2 = 0x0B, 0xDA, 0x51      # #0bda51 (green)

    if s <= 0.5:
        # gradient from red to golden yellow
        t = s / 0.5
        r = int(r1 + (r_mid - r1) * t)
        g = int(g1 + (g_mid - g1) * t)
        b = int(b1 + (b_mid - b1) * t)
    else:
        # gradient from golden yellow to green
        t = (s - 0.5) / 0.5
        r = int(r_mid + (r2 - r_mid) * t)
        g = int(g_mid + (g2 - g_mid) * t)
        b = int(b_mid + (b2 - b_mid) * t)

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def demo(intervals=10):
    """Show a row of colored blocks for scores\
         from 0 to 1 with two-segment gradient."""
    scores = np.linspace(0, 1, intervals)
    colors = [gradient_color(s) for s in scores]

    fig, ax = plt.subplots(figsize=(intervals, 1))
    for i, c in enumerate(colors):
        rect = plt.Rectangle((i, 0), 1, 1, color=c)
        ax.add_patch(rect)
        ax.text(i + 0.5, 0.5, f"{scores[i]:.2f}",
                va='center', ha='center', fontsize=8,
                color='black' if scores[i] < 0.75 else 'white')

    ax.set_xlim(0, intervals)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Demo two-segment\
        gradient_color function")
    parser.add_argument("-n", "--intervals", type=int, default=10,
                        help="Number of intervals between 0 and 1")
    args = parser.parse_args()
    demo(args.intervals)
