import optuna
import pandas as pd
import json
import optuna.visualization as vis
from optuna.distributions import IntDistribution, FloatDistribution, CategoricalDistribution

df_trials = pd.read_json('hyperparameter_study_results.json', orient='records')
# print(df_trials.head())

# instances = ["C101.txt", "R101.txt", "RC101.txt", "C201.txt", "R201.txt", "RC201.txt"]
# # Add trials to optuna from my json file
# param_importances_per_instance = {}
# for instance in instances:
#     study = optuna.create_study(direction='minimize', study_name=f"study_{instance}")
#     for _, row in df_trials[df_trials['problem_instance'] == instance].iterrows():
#         # Extract parameters from your row
#         params = {
#             'iterations': row['params_iterations'],
#             'init_temp': row['params_init_temp'],
#             'final_temp': row['params_final_temp'],
#             'global_best_score': row['params_global_best_score'],
#             'local_best_score': row['params_local_best_score'],
#             'accepted_score': row['params_accepted_score'],
#             'cooling_function': row['params_cooling_function']
#         }
#
#         distributions = {
#             "iterations": IntDistribution(1000, 8000, step=1000),
#             "global_best_score": IntDistribution(5, 20),
#             "cooling_function": CategoricalDistribution(["exponential", "linear"])
#         }
#
#         if params["cooling_function"] == 'linear':
#             distributions["init_temp"] = IntDistribution(100, 1100, step=500)
#             distributions["final_temp"] = FloatDistribution(0.001, 1)
#         else:
#             distributions["init_temp"] = IntDistribution(1000, 3000, step=1000)
#             distributions["final_temp"] = FloatDistribution(0, 100)
#
#         distributions["local_best_score"] = IntDistribution(3, params["global_best_score"]-1)
#         distributions["accepted_score"] = IntDistribution(1, params["local_best_score"] - 1)
#
#         trial = optuna.trial.create_trial(
#             params=params,
#             value=row['value'],
#             state=optuna.trial.TrialState.COMPLETE,
#             user_attrs={"problem_instance": row["problem_instance"]},
#             distributions = distributions
#         )
#
#         study.add_trial(trial)
#     importance = optuna.importance.get_param_importances(study)
#     param_importances_per_instance[instance] = importance
#
# print(param_importances_per_instance)

# fig = vis.plot_param_importances(study)
# fig.show()

best_indices = df_trials.groupby("problem_instance")["value"].idxmin()

# Use these indices to extract the best trial per instance
best_trials = df_trials.loc[best_indices]

print(best_trials)

# ['params_iterations', 'params_global_best_score', 'params_cooling_function',
#                     'params_init_temp','params_final_temp','params_local_best_score','params_accepted_score'])