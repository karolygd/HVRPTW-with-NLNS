from resources.data import parse_problem_instance, parse_reduced_instance
import resources.global_context as global_context
from resources.datatypes.solution import Solution
from src.initial_solution import savings_vrptw
from src.alns import alns
import optuna
import pandas as pd
import optuna.visualization as vis


def objective(trial, initial_solution, instance_type, tw_spread):
    iterations = trial.suggest_int('iterations', 1000, 8000, step=1000)
    global_best_score = trial.suggest_int('global_best_score', 5, 20)
    local_best_score = trial.suggest_int('local_best_score', 3, global_best_score-1)
    accepted_score = trial.suggest_int('accepted_score', 1, local_best_score-1)
    cooling_function = trial.suggest_categorical('cooling_function', ['linear', 'exponential'])
    if cooling_function == 'exponential':
        t_start = trial.suggest_int('init_temp', 1000, 3000, step=1000)
        t_end = trial.suggest_float('final_temp', 0, 100)
    else:
        t_start = trial.suggest_int('init_temp', 100, 1100, step=500)
        t_end = trial.suggest_float('final_temp', 0.001, 1)
    # segment_size = trial.suggest_int('segment_size', 20, 50, step=10)

    alns_solution = alns(instance_type=instance_type, tw_spread=tw_spread, initial_solution=initial_solution,
                         number_of_iterations=iterations, operator_selection=1, h_start=t_start, h_end=t_end,
                         temp_update_func=cooling_function, segment_size=20,
                         o1=global_best_score, o2=local_best_score, o3=accepted_score)

    # The objective should be minimized or maximized depending on your metric (cost, fitness, etc.)
    return alns_solution.get_cost()  # minimize cost


instances = ["C101.txt", "R101.txt", "RC101.txt", "C201.txt", "R201.txt", "RC201.txt"] # "C101.txt",
studies = {}

for instance in instances:
    global_context.global_instance = parse_problem_instance(instance, vehicle_cost_structure='a')
    initial_solution = savings_vrptw()

    if instance[0] == "C":  # C: clustered instance
        instance_type = 0
    elif instance[1] == "C":  # RC: random-clustered instance
        instance_type = 2
    else:  # R: random instance
        instance_type = 1

    tw_spread = instance[1]
    try:
        tw_spread = int(instance[1])
    except:
        tw_spread = int(instance[2])

    study = optuna.create_study(direction='minimize', study_name=f'study_{instance}')
    study.optimize(lambda trial: objective(trial, initial_solution, instance_type, tw_spread), n_trials=19)
    studies[instance] = study

all_trials = []

for instance_name, study in studies.items():
    df = study.trials_dataframe()
    df['problem_instance'] = instance_name  # Add instance identifier
    all_trials.append(df)

# Combine all dataframes into one
combined_df = pd.concat(all_trials, ignore_index=True)
# Save combined results to JSON
combined_df.to_json('hyperparameter_study_results.json', orient='records', indent=2)