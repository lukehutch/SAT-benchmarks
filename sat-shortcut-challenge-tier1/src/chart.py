"""Dot plot of bench.py's results (values copied from the run recorded in LOG.md, 2026-11-22). CPU time, log scale."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
TO = 20000  # ms
rows = [  # label, ours, cadical, kissat  (ms; None = did not finish within the limit)
 ("Tseitin (XOR), 200 nodes", 2.1, None, None), ("Pigeonhole, 13 into 12", 3.1, None, None),
 ("Chessboard tiling, 14x14", 2.69, None, None), ("Multiplier equivalence, 10x10", 184.4, None, None),
 ("Multiplier equivalence, 8x8", 14.1, 7426.4, 6007.1), ("Hamiltonian cycle, cut vertex", 0.26, None, 84.6),
 ("Hamiltonian cycle, bipartite", 0.82, 97.8, 351.0),
 ("Adder equivalence, 64-bit", 61.7, 156.7, 159.2), ("Hamiltonian cycle, planted, 40", 332.5, 88.3, 1280.4),
 ("XOR system plus clauses", 136.1, 20.9, 26.9),
 ("Random 3-SAT, 200 vars", 655.8, 646.2, 607.2), ("Random 3-SAT, 250 vars", 3854.5, 3852.5, 1455.7)]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
series = [("Known shortcut (ours)", "#2a78d6", "o"), ("CaDiCaL", "#eb6834", "s"), ("Kissat", "#1baf7a", "D")]
fig, ax = plt.subplots(figsize=(12, 6.75), dpi=160); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
n = len(rows); off = (0.22, 0.0, -0.22)
for i, (lab, *vals) in enumerate(rows):
    y = n - 1 - i
    if i in (7, 10): ax.axhline(y + 0.5, color=GRID, lw=1.2)
    for (name, col, mk), v, o in zip(series, vals, off):
        if v is None:
            ax.plot(TO * 1.9, y + o, marker=mk, ms=9, mfc=SURF, mec=col, mew=2, ls="none", zorder=3)
        else:
            ax.plot(v, y + o, marker=mk, ms=9, color=col, mec=SURF, mew=1.2, ls="none", zorder=3)
ax.set_xscale("log"); ax.set_xlim(0.2, TO * 3.2); ax.set_ylim(-0.7, n - 0.3)
ax.axvline(TO, color=INK2, lw=1, ls=(0, (4, 4)))
ax.text(TO * 1.9, n - 0.42, "did not\nfinish", ha="center", va="bottom", fontsize=10, color=INK2)
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=12, color=INK)
ax.set_xticks([1, 10, 100, 1000, 10000]); ax.set_xticklabels(["1 ms", "10 ms", "100 ms", "1 s", "10 s"], fontsize=11, color=INK2)
ax.grid(axis="x", color=GRID, lw=1); ax.set_axisbelow(True)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(length=0)
h = [plt.Line2D([], [], marker=mk, color=col, ls="none", ms=9, label=name) for name, col, mk in series]
h.append(plt.Line2D([], [], marker="o", mfc=SURF, mec=INK2, mew=2, ls="none", ms=9, label="hollow = did not finish"))
ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.42, 1.09), ncol=4, frameon=False, fontsize=11, labelcolor=INK)
fig.suptitle("Known shortcuts beat top SAT solvers by up to 10,000x, but only on problems that have one",
             x=0.02, y=0.985, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.02, 0.02, "CPU time to solve, log scale; limit 10 to 20 s per run. Top group: a known method fits the problem (Gaussian elimination, counting, matching, simulating all inputs,\n"
         "graph tests). Middle: a shortcut exists but gains little or loses. Bottom: no structure, so we fall back to CaDiCaL. 12 of 47 instances; all answers agree.", fontsize=9.5, color=INK2, va="bottom")
for yy, t in ((n - 0.55, "shortcut wins"), (n - 7.55, "little or no gain"), (n - 10.55, "no structure")):
    ax.text(0.23, yy + 0.02, t, fontsize=9.5, color=INK2, va="top", style="italic")
fig.subplots_adjust(left=0.27, right=0.98, top=0.86, bottom=0.17)
fig.savefig("../results/shortcut_chart.png", facecolor=SURF)
