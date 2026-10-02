import os
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde
from scipy.interpolate import CubicSpline


def _gauss(x, mu, sig):
    y = np.exp(-0.5 * ((x - mu) / sig) ** 2)
    return y / (y.max() + 1e-12)


def _sample_tube(center_curve, t_samples, rng, sigma_u=0.08, sigma_v=0.18):
    pts = center_curve(t_samples)
    eps = 1e-3
    pts_f = center_curve(np.clip(t_samples + eps, 0, 1))
    tan = pts_f - pts
    tan_norm = np.linalg.norm(tan, axis=1, keepdims=True) + 1e-9
    t_hat = tan / tan_norm
    n_hat = np.stack([-t_hat[:, 1], t_hat[:, 0]], axis=1)
    u = rng.normal(0, sigma_u, size=(len(t_samples), 1))
    v = rng.normal(0, sigma_v, size=(len(t_samples), 1))
    return pts + u * n_hat + v * t_hat


def _mixture_t(n, centers, scales, weights, rng):
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    comp = rng.choice(len(centers), size=n, p=weights)
    t = rng.normal(np.array(centers)[comp], np.array(scales)[comp])
    return np.clip(t, 0, 1)


def _kde_prepare(P, grid=280, pad_x=1.8, pad_y=1.3):
    Xv, Yv = P[:, 0], P[:, 1]
    kde = gaussian_kde(np.vstack([Xv, Yv]))
    xmin, xmax = Xv.min() - pad_x, Xv.max() + pad_x
    ymin, ymax = Yv.min() - pad_y, Yv.max() + pad_y
    xx, yy = np.mgrid[xmin:xmax:complex(grid), ymin:ymax:complex(grid)]
    zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
    return xx, yy, zz, xmin, xmax, ymin, ymax


def plot_distribution(ax):
    color_prior = "#6F6F6F"
    color_see = "#0F4D92"
    color_blind = "#D88F8A"

    x = np.linspace(0.0, 1, 1000)
    p_prior = _gauss(x, 0.30, 0.07)
    p_see = _gauss(x, 0.72, 0.07)
    p_blind = 0.30 * _gauss(x, 0.30, 0.12) + 0.22

    y_star = 0.72
    see_star = np.interp(y_star, x, p_see)
    blind_star = np.interp(y_star, x, p_blind)

    ax.plot(x, p_prior, color=color_prior, linewidth=2.2, label=r"$P(y\mid x_t)$")
    ax.fill_between(x, 0, p_prior, color=color_prior, alpha=0.12)
    ax.plot(x, p_blind, color=color_blind, linewidth=2.2, label=r"$P(y\mid x_v^{\emptyset},x_t)$")
    ax.fill_between(x, 0, p_blind, color=color_blind, alpha=0.12)
    ax.plot(x, p_see, color=color_see, linewidth=2.8, label=r"$P(y\mid x_v,x_t)$")
    ax.fill_between(x, 0, p_see, color=color_see, alpha=0.12)

    ax.vlines(y_star, 0, 1.0, linewidth=2, linestyle=":", alpha=0.5, color="black")
    ax.annotate(
        "",
        xy=(y_star, see_star),
        xytext=(y_star, blind_star),
        arrowprops=dict(arrowstyle="<->", linewidth=2),
    )
    ax.text(y_star + 0.02, 0.5 * (see_star + blind_star), "      VIG",
            ha="left", va="center", fontsize=24, fontfamily='helvetica')

    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels([-1, 0, 1])
    ax.set_xlim(0, 1.05)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylim(0, 1.25)
    ax.set_xlabel("Answer space (arbitrary units)", fontsize=28, labelpad=12)
    ax.set_ylabel("Probability", fontsize=28, labelpad=18)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    ax.tick_params(width=1.5, length=8, labelsize=24)
    ax.legend(loc="upper center", frameon=False, ncols=3, prop={"family": "monospace", "size": 24})


def plot_manifold(ax):
    rng = np.random.default_rng(42)
    xp = np.array([0.0, 0.18, 0.45, 0.72, 1.0])
    yt = np.array([0.15, 0.28, 0.18, 0.05, 0.10])
    ym = np.array([0.78, 0.70, 0.60, 0.68, 0.80])

    cs_t = CubicSpline(xp, yt, bc_type="natural")
    cs_m = CubicSpline(xp, ym, bc_type="natural")

    def curve_text(t):
        x = t
        y = cs_t(x) + 0.03 * np.sin(6 * np.pi * t)
        return np.stack([x, y], axis=1)

    def curve_mm(t):
        x = t
        y = cs_m(x) + 0.02 * np.sin(4 * np.pi * t + 0.6)
        return np.stack([x, y], axis=1)

    N = 2600
    t_text = _mixture_t(N, [0.20, 0.55, 0.82], [0.07, 0.09, 0.06], [0.35, 0.40, 0.25], rng)
    t_mm = _mixture_t(N, [0.18, 0.52, 0.80], [0.06, 0.10, 0.07], [0.30, 0.45, 0.25], rng)

    pts_text = _sample_tube(curve_text, t_text, rng, sigma_u=0.09, sigma_v=0.14)
    pts_mm = _sample_tube(curve_mm, t_mm, rng, sigma_u=0.08, sigma_v=0.13)

    A = np.array([[10.0, 0.0], [0.0, 3.5]])
    b_text = np.array([0.6, 0.9])
    b_mm = np.array([0.6, 2.4])

    P_t = pts_text @ A.T + b_text
    P_m = pts_mm @ A.T + b_mm

    tt = np.linspace(0.08, 0.95, 450)
    ridge_t = curve_text(tt) @ A.T + b_text
    ridge_m = curve_mm(tt) @ A.T + b_mm

    t_mid = 0.42
    idx_mid = np.searchsorted(tt, t_mid)
    u = np.linspace(0, 1, idx_mid)
    smooth = 3 * u**2 - 2 * u**3
    x_mix = (1 - smooth) * ridge_t[:idx_mid, 0] + smooth * ridge_m[:idx_mid, 0]
    y_mix = (1 - smooth) * ridge_t[:idx_mid, 1] + smooth * ridge_m[:idx_mid, 1] + 0.10 * np.sin(np.pi * u)
    x_ours = np.concatenate([x_mix, ridge_m[idx_mid:, 0]])
    y_ours = np.concatenate([y_mix, ridge_m[idx_mid:, 1]])

    star_inds = np.linspace(0, len(tt) - 1, 10, dtype=int)
    S_t = ridge_t[star_inds]
    star_inds_ours = np.linspace(0, len(x_ours) - 1, 10, dtype=int)
    S_m = np.column_stack([x_ours[star_inds_ours], y_ours[star_inds_ours]])

    xx_m, yy_m, zz_m, xmin_m, xmax_m, ymin_m, ymax_m = _kde_prepare(P_m)
    xx_t, yy_t, zz_t, xmin_t, xmax_t, ymin_t, ymax_t = _kde_prepare(P_t)

    xmin = min(xmin_m, xmin_t) - 0.6
    xmax = max(xmax_m, xmax_t) + 0.6
    ymin = min(ymin_m, ymin_t) - 0.4
    ymax = max(ymax_m, ymax_t) + 0.8

    levels_m = np.quantile(zz_m, np.linspace(0.72, 0.99, 10))
    levels_t = np.quantile(zz_t, np.linspace(0.72, 0.99, 10))

    blue = "#2E74B5"
    blue_pts = "#1f77b4"
    gray = "#6F6F6F"
    gray_pts = "#6b7280"
    red = "#D62728"

    ax.axis("off")
    ax.scatter(P_m[:, 0], P_m[:, 1], s=10, alpha=0.10, color=blue_pts, zorder=1)
    ax.scatter(P_t[:, 0], P_t[:, 1], s=10, alpha=0.10, color=gray_pts, zorder=1)
    ax.contour(xx_m, yy_m, zz_m, levels=levels_m, colors=blue, linewidths=1.6, alpha=0.3, zorder=2)
    ax.contour(xx_t, yy_t, zz_t, levels=levels_t, colors=gray, linewidths=1.6, alpha=0.3, zorder=2)
    ax.scatter(S_m[:, 0], S_m[:, 1], marker="*", s=185, color=red, edgecolor="white", linewidth=0.6, zorder=5)
    ax.scatter(S_t[:, 0], S_t[:, 1], marker="*", s=185, color=red, edgecolor="white", linewidth=0.6, zorder=5)

    bbox = dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=1)
    ax.text(xmin + 0.9, ymax + 0.2, r"Multimodal manifold $\mathcal{M}_\text{mm}$", va="top", bbox=bbox, size=24)
    ax.text(xmin + 0.9, ymin, r"Textual manifold $\mathcal{M}_\text{t}$", va="bottom", bbox=bbox, size=24)

    x0, y0 = xmin + 2.1, (ymin + ymax) / 2 - 0.2
    t0 = 0.12
    z_t0 = (curve_text(np.array([t0])) @ A.T + b_text)[0]
    z_m0 = (curve_mm(np.array([t0])) @ A.T + b_mm)[0]

    ax.plot([x0], [y0], marker="o", markersize=7, color="black", zorder=6)
    ax.plot([x0, x0], [z_t0[1], z_m0[1]], linestyle="--", linewidth=1.6, color="#D62728", alpha=0.9, zorder=3)
    ax.plot([x0], [z_t0[1]], marker="o", markersize=6, color=gray, zorder=6)
    ax.plot([x0], [z_m0[1]], marker="o", markersize=6, color=blue, zorder=6)
    ax.plot(ridge_t[:, 0], ridge_t[:, 1], linestyle="--", linewidth=2.6, color=gray, alpha=0.95, zorder=4)
    ax.plot(x_ours, y_ours, linewidth=3.0, color=blue, alpha=0.98, zorder=4)

    ax.text(x0 - 2, z_t0[1] - 0.8, r"$z_\text{t}=f_\text{t}(x_t)$", va="top", bbox=bbox, size=18)
    ax.text(x0 - 2, z_m0[1] + 1.2, r"$z_\text{mm}=f_\text{mm}(x_v,x_t)$", va="bottom", bbox=bbox, size=18)
    ax.text(x0 - 2, y0 + 0.4, r"sample $x=(x_v,x_t)$", bbox=bbox, size=18)

    idx_dpo = np.argmin(np.abs(ridge_t[:, 0]))
    xy_dpo = ridge_t[idx_dpo] + np.array([2, -0.2])
    idx_ours = np.argmin(np.abs(x_ours - 4))
    xy_ours = np.array([x_ours[idx_ours], y_ours[idx_ours]]) + np.array([0.8, 0.5])

    ax.annotate(
        "Standard DPO shortcut",
        xy=xy_dpo,
        xytext=(4, ymin + 0.8),
        arrowprops=dict(arrowstyle="->", linewidth=1.6, color="black"),
        bbox=bbox,
        zorder=6,
    )
    ax.annotate(
        r"Ours: enter $\mathcal{M}_\text{mm}$",
        xy=xy_ours,
        xytext=(4, ymax - 1.3),
        arrowprops=dict(arrowstyle="->", linewidth=1.6, color="black"),
        bbox=bbox,
        va="top",
        zorder=6,
    )
    ax.text(ridge_m[-1, 0] + 4.2, ridge_m[-1, 1], "grounded", ha="left", va="center", bbox=bbox, size=20)
    ax.text(ridge_t[-1, 0] + 4.2, ridge_t[-1, 1], "prior-dominated", ha="left", va="center", bbox=bbox, size=20)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)


def plot_concept():
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(24, 6))

    plot_distribution(ax_left)
    plot_manifold(ax_right)

    fig.tight_layout(pad=0.5)
    fig.subplots_adjust(wspace=0.25)

    pos = ax_right.get_position()
    ax_right.set_position([pos.x0, pos.y0 - 0.04, pos.width, pos.height])

    os.makedirs("./figures/", exist_ok=True)
    fig.savefig("./figures/concept.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    plt.rcParams["font.family"] = "helvetica"
    plt.rcParams["font.size"] = 18
    plt.rcParams["axes.linewidth"] = 1.5
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False

    plot_concept()
