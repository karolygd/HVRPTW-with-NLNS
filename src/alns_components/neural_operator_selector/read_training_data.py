import numpy as np
import pandas as pd

def get_alns_data(csv_name):
    df = pd.read_csv(csv_name)
    feature_columns = ['iterations',
                    'instance_type',
                    'tw_spread',
                    'operator_selection_mechanism',
                    'number_of_vertices_to_remove',
                    "delta_last_improv",
                    "acceptance_ratio",
                    "i_last_improv",
                    'prev_remove_operator',
                    'prev_insert_operator',
                    'route_imbalance',
                    'capacity_utilization',
                    'success_r_op_1',
                    'success_r_op_2',
                    'success_r_op_3',
                    'success_r_op_4',
                    'success_r_op_5',
                    'success_i_op_1',
                    'success_i_op_2',
                    'success_i_op_3'
                    ]
    X_train = df[feature_columns].to_numpy()
    destroy_idx = df['chosen_remove_operator'].to_numpy()
    insert_idx = df['chosen_insert_operator'].to_numpy()
    target = df['short_long_improvement'].to_numpy()

    return X_train, destroy_idx, insert_idx, target

csv_name = '../../../c1_training.csv'
X_train, destroy_idx, insert_idx, target = get_alns_data(csv_name)
print(f"Shape: {destroy_idx.shape} --> {destroy_idx}")
print(f"Shape: {insert_idx.shape} --> {insert_idx}")
print(f"Shape: {target.shape} --> {target}")

# compute y: Immediate + Long-Term improvement
# since all training logs are stored in the same file, I have to separate them
# alpha*(immediate cost) + (1-alpha)*(best cost found in the next k steps)

# def get_future_best_cost(current_index, df, cost_col=20, k=20):
#     """
#     Returns the minimum cost over the next k rows (rows current_index+1 to current_index+k).
#     If no future rows are available, return NaN.
#     """
#     # Slicing the next k rows
#     future_slice = df.loc[current_index+1: current_index+k, cost_col]
#     if future_slice.empty:
#         return np.nan
#     else:
#         return future_slice.min()
#
# alpha = 0.7    # Example alpha
#
# new_values = []
# for i in range(len(df)):
#     immediate_cost = df.loc[i, 20]
#     best_future_cost = get_future_best_cost(i, df, cost_col=20)
#     if pd.isna(best_future_cost):
#         # If there's no next-row data (last iteration), use immediate_cost
#         new_values.append(immediate_cost)
#     else:
#         # alpha * immediate_cost + (1-alpha) * best_future_cost
#         combined = alpha * immediate_cost + (1 - alpha) * best_future_cost
#         new_values.append(combined)
# df["y"] = new_values


