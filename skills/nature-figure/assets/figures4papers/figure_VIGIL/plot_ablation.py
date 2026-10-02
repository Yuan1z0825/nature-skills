import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec as gridspec


data_ablation = {
    'methods': [
        'DPO',
        'DA-DPO',
        'VIGIL (Ours)',
    ],
    'colors': [
        "#D88F8A",
        "#8BCF8B",
        "#0F4D92"
    ],
    '$\beta$': [0.05, 0.1, 0.2, 0.5],
    '$\lambda$': [0.1, 0.5, 1.0, 2.0],
    'data_fraction': [0.1, 0.25, 0.5, 1.0],
    'results': {
        'SFT': np.array([82.1]),  # POPE_Adv
        # This is 3 methods on 4 beta values.
        '$\beta$': np.array([
            [79.5, 82.8, 81.0, 76.2],
            [83.2, 84.2, 83.5, 81.0],
            [86.8, 86.9, 86.5, 85.8],
        ]),
        # This is our method.
        '$\lambda$': np.array([
            [84.5, 86.1, 86.9, 87.2], # POPE_Adv
            [49.8, 49.6, 49.5, 48.8], # MathVista
        ]),
        'data_fraction': np.array([
            [82.78, 83.19, 85.05, 85.67],
            [84.04, 85.46, 87.07, 87.81],
            [86.69, 88.18, 89.17, 89.82],
        ])
    }
}


def plot_curves(data_ablation):
    """
    Left panel: ablation on hyperparameter beta (x = beta values, y = score, 3 curves for 3 methods).
    Right panel: blank.
    """
    methods = data_ablation['methods']
    colors = data_ablation['colors']

    fig, axes = plt.subplots(1, 3, figsize=(27, 6), gridspec_kw={'width_ratios': [1.1, 1, 1]})

    ax = axes[0]
    y_ticks = [78, 82, 86, 90]
    data_fraction_key = 'data_fraction'
    data_fraction_vals = np.asarray(data_ablation[data_fraction_key])
    results_data_fraction = data_ablation['results'][data_fraction_key]  # shape (n_methods, n_data_fraction)
    x_pos = np.arange(len(data_fraction_vals))
    y_sft = data_ablation['results']['SFT']
    # SFT only horizontal line.
    ax.plot([x_pos[0] - 1, x_pos[-1] + 0.2], [y_sft, y_sft], color='black', alpha=0.3, linewidth=4, linestyle='--', label='SFT only')
    # Ours with 25% data horizontal line.
    ax.plot([x_pos[0] - 0.1, x_pos[-1] + 0.1], [results_data_fraction[-1][1], results_data_fraction[-1][1]], color=colors[-1], linewidth=3, linestyle=':')
    for m, (method, color) in enumerate(zip(methods, colors)):
        y = results_data_fraction[m]
        ax.plot(x_pos, y, color=color, linewidth=3, marker='o', markersize=10, label=method)

    ax.set_xlabel(r'Fraction of data used for post-training', fontsize=28, labelpad=18)
    ax.set_xlim(x_pos[0] - 0.5, x_pos[-1] + 0.4)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{item:.0%}' for item in data_fraction_vals])
    ax.set_ylabel('$POPE_{Adv}$' + r'$\uparrow$', fontsize=28, fontfamily='monospace', labelpad=12)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks)
    ax.tick_params(labelsize=24, length=8, width=1.5)
    ax.legend(fontsize=24, loc='lower center', ncols=2, frameon=False)

    ax = axes[1]
    y_ticks = [75, 79, 84, 88]
    beta_key = '$\beta$'
    beta_vals = np.asarray(data_ablation[beta_key])
    results_beta = data_ablation['results'][beta_key]  # shape (n_methods, n_beta)
    x_pos = np.arange(len(beta_vals))
    for m, (method, color) in enumerate(zip(methods, colors)):
        y = results_beta[m]
        ax.plot(x_pos, y, color=color, linewidth=3, marker='o', markersize=10, label=method)

    ax.set_xlabel(r'Hyperparameter $\beta$', fontsize=28, labelpad=18)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(b) for b in beta_vals])
    ax.set_ylabel('$POPE_{Adv}$' + r'$\uparrow$', fontsize=28, fontfamily='monospace', labelpad=12)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks)
    ax.tick_params(labelsize=24, length=8, width=1.5)
    ax.legend(fontsize=24, loc='lower center', frameon=False)

    ax = axes[2]
    y_ticks = [84, 85, 86, 87, 88]
    lambda_key = '$\lambda$'
    lambda_vals = np.asarray(data_ablation[lambda_key])
    results_lambda = data_ablation['results'][lambda_key]  # shape (2, n_beta)
    assert len(results_lambda) == 2
    x_pos = np.arange(len(lambda_vals))
    y = results_lambda[0]
    ax.plot(x_pos, y, color=colors[-1], linewidth=3, marker='o', markersize=10, label=methods[-1], alpha=0.4)
    ax.set_xlabel(r'Hyperparameter $\lambda$', fontsize=28, labelpad=18)
    ax.set_xticks(x_pos)
    ax.set_xlim(x_pos[0] - 0.5, x_pos[-1] + 0.5)
    ax.set_xticklabels([str(b) for b in lambda_vals])
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks)
    ax.set_ylabel('$POPE_{Adv}$' + r'$\uparrow$', fontsize=28, fontfamily='monospace', labelpad=12, color=colors[-1], alpha=0.4)
    ax.tick_params(labelsize=24, length=8, width=1.5)
    ax.legend(fontsize=24, loc='lower center', frameon=False)

    ax2 = ax.twinx()
    ax2.spines['right'].set_visible(True)
    y = results_lambda[1]
    ax2.set_ylabel('$MathVista$' + r'$\uparrow$', fontsize=28, fontfamily='monospace', labelpad=36, rotation=270, color=colors[-1], alpha=1.0)
    ax2.plot(x_pos, y, color=colors[-1], linewidth=3, marker='o', markersize=10, label=methods[-1], alpha=1.0)
    ax2.plot(x_pos, y, color=colors[-1], linewidth=3, marker='o', markersize=10, label=methods[-1], alpha=1.0)
    ax2.set_yticks([48, 48.5, 49, 49.5, 50])
    ax2.set_yticklabels([48, 48.5, 49, 49.5, 50])
    ax2.tick_params(labelsize=24, length=8, width=1.5)
    ax2.legend(fontsize=24, loc='lower center', frameon=False)

    # Right panel: at each x, print average of the two metrics at the top
    y_top = ax.get_ylim()[1] - 0.2
    for i in range(len(x_pos)):
        avg = (results_lambda[0][i] + results_lambda[1][i]) / 2
        ax.text(x_pos[i], y_top, f'Mean = {avg:.1f}', ha='center', va='bottom', fontsize=18)

    fig.tight_layout(pad=0.5)
    fig.subplots_adjust(wspace=0.3)
    os.makedirs('./figures/', exist_ok=True)
    fig.savefig('./figures/ablation_curves.png', dpi=300)
    plt.close(fig)
    return


if __name__ == '__main__':
    plt.rcParams['font.family'] = 'helvetica'
    plt.rcParams['font.size'] = 24
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.linewidth'] = 3

    plot_curves(data_ablation)
