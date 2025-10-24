
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def k_fold_sum_distribution(values, probs, k):
    """
    Вычисляет распределение суммы k независимых одинаково распределённых случайных величин.
    values — массив значений X
    probs  — массив вероятностей P (сумма должна быть равна 1)
    k      — сколько раз суммируем
    """
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)

    pmf = {v: p for v, p in zip(values, probs)}
    for _ in range(k):
        new_pmf = defaultdict(float)
        for a, pa in pmf.items():
            for b, pb in zip(values, probs):
                new_pmf[a + b] += pa * pb
        pmf = new_pmf

    sums = np.array(sorted(pmf.keys()))
    probabilities = np.array([pmf[s] for s in sums])
    return sums, probabilities

def pew(P, kstart, kend, id):
    X = [n + 1 for n in range(len(P))]
    rend = 0.8

    fig, ax_main = plt.subplots(figsize=(12, 5))

    for i, k in enumerate(range(kend, kstart - 1, -1)):
        if i == 0:
            ax = ax_main
        else:
            ax = ax_main.twiny()
            ax.set_xticks([])
            ax.set_xlabel("")
            for spine_name, spine in ax.spines.items():
                if spine_name in ("top", "bottom"):
                    spine.set_visible(False)

        sums, probs = k_fold_sum_distribution(X, P, k)
        col = rend - (rend / kend) * k
        ax.plot(sums, probs, marker="o", linestyle="-", color=(1, col, col))

    ax_main.set_title(f"Распределение суммы {len(P)} случайных величин с разными вероятностями")
    ax_main.set_xlabel("Сумма")
    ax_main.set_ylabel("Вероятность")
    ax_main.grid(True)

    os.makedirs("graphs", exist_ok=True)

    p_str = f"{P[0]}_{P[-1]}"
    filename = f"graphs/k{kstart}_k{kend}_p{p_str}_id{id}.png"

    fig.savefig(filename, format="PNG", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    return filename