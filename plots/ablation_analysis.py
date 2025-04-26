import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Columns:
# 'iteration', 'instance', 'run time', 'cost', 'components'
df = pd.read_csv('stat_analysis_ls.csv')

instances_top = ["C101.txt", "R101.txt", "RC101.txt", "C106.txt", "R106.txt", "RC106.txt"]
instances_bottom = ["C201.txt", "R201.txt", "RC201.txt", "C206.txt", "R206.txt", "RC206.txt"]
instances_all = instances_top + instances_bottom  # Ordered list

# Define the order for instances and components (variants)
instances = sorted(df['instance'].unique())
component_order = ["all components", "no local search", "no adaptive customer removal"]

#normalize costs for visualization in y-axis
for instance in instances:
    instance_mask = df['instance'] == instance
    min_cost = df.loc[instance_mask, 'cost'].min()
    max_cost = df.loc[instance_mask, 'cost'].max()

    df.loc[instance_mask, 'normalized_cost'] = (
            (df.loc[instance_mask, 'cost'] - min_cost) / (max_cost - min_cost)
    )

# Define a color mapping for the three variants
color_map = {
    "all components": "#ccebc5",
    "no local search": "#b3cde3",
    "no adaptive customer removal": "#fbb4ae"
}

# Number of variants per instance
n_variants = len(component_order)

def plot_boxplot(ax, instance):
    data_to_plot = []
    positions = []

    offsets = np.linspace(-0.3, 0.3, n_variants)  # Horizontal spacing between variants

    for j, comp in enumerate(component_order):
        subset = df[(df['instance'] == instance) & (df['components'] == comp)]
        data_to_plot.append(subset['normalized_cost'].values)
        positions.append(0 + offsets[j])

    # Plot boxplot
    bp = ax.boxplot(data_to_plot, positions=positions, widths=0.15, patch_artist=True, manage_ticks=False, showfliers=False)

    # Assign colors to each box based on variant
    for i, box in enumerate(bp['boxes']):
        variant_index = i % n_variants
        comp_variant = component_order[variant_index]
        box.set_facecolor(color_map[comp_variant])

    # Set x-axis labels
    ax.set_xticks([])
    ax.set_title(instance)
    if instance in ["C101.txt", "C201.txt"]:
        ax.set_ylabel('Normalized Cost')
    else:
        ax.set_ylabel('')
        #ax.tick_params(left=False)

plt.rcParams["font.family"] = "serif"
fig, axes = plt.subplots(nrows=2, ncols=6, figsize=(18, 8), sharey=True)
# Iterate over instances and assign each to a subplot
for idx, instance in enumerate(instances_all):
    row = 0 if instance in instances_top else 1  # Assign top or bottom row
    col = instances_top.index(instance) if instance in instances_top else instances_bottom.index(
        instance)  # Column index

    plot_boxplot(axes[row, col], instance)

# Create a single legend for the entire figure
handles = [mpatches.Patch(color=color_map[comp], label=comp) for comp in component_order]
fig.legend(handles=handles, loc="lower center", edgecolor='black', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.03))

plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()
