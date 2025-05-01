import joblib
import torch
from src.alns_components.neural_operator_selector.neural_network import OperatorSelectionNet

# todo: erase later:
# import pandas as pd
# from src.operators.remove_operators import RemoveOperators
# from src.operators.insertion_operators import InsertionOperators
# import resources.global_context as global_context
# from resources.data import parse_reduced_instance

# Optionally, incorporate ϵ-greedy or a softmax-based sampling if you want to maintain exploration.

class NeuralOperatorSelector:
    def __init__(self, remove_operators, insert_operators):
        self.remove_operators = remove_operators
        self.insert_operators = insert_operators
        # Features
        # Import feature scalers
        self.feature_prep = joblib.load("src/alns_components/neural_operator_selector/feature_prep.joblib")
        self.y_scaler = joblib.load("src/alns_components/neural_operator_selector/y_scaler.joblib")
        input_dim = len(self.feature_prep.get_feature_names_out())

        # Get model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = OperatorSelectionNet(input_dim).to(self.device)

        # Load weights and biases from the best trained model
        state = torch.load("src/alns_components/neural_operator_selector/model.pt",map_location=self.device)
        self.model.load_state_dict(state)
        self.model.eval()

    def select_operator(self, X_predict):
        X_transformed = self.feature_prep.transform(X_predict)
        X_tensor = torch.tensor(X_transformed, dtype=torch.float32, device=self.device)

        with torch.no_grad():
            destroy_scores, insert_scores = self.model(X_tensor)

        # Get the operator index with the best predicted short_long_improvement
        d_ix = torch.argmin(destroy_scores).item()
        r_ix = torch.argmin(insert_scores).item()
        remove_operator = self.remove_operators[d_ix]
        insert_operator = self.insert_operators[r_ix]

        return remove_operator, insert_operator

# # Prepare input data:
# num_pos    = ['iterations', 'acceptance_ratio', 'number_of_vertices_to_remove', 'i_last_improv', 'route_imbalance', 'capacity_utilization', 'success_r_op_1', 'success_r_op_2', 'success_r_op_3', 'success_r_op_4', 'success_r_op_5', 'success_i_op_1', 'success_i_op_2','success_i_op_3']
# num_signed = ['rel_delta_last_improv']
# cat_cols   = ['instance_type', 'tw_spread', 'operator_selection_mechanism',
#               'prev_remove_operator', 'prev_insert_operator']

# row_num = 899
# X_predict = pd.read_csv("../../../training_data_nn/test_set.csv").iloc[row_num][num_pos+num_signed+cat_cols]
# X_predict['prev_remove_operator'] = X_predict['prev_remove_operator']-1
# X_predict['prev_insert_operator'] = X_predict['prev_insert_operator']-1
# X_predict = pd.DataFrame([X_predict])
#
# global_context.global_instance = parse_reduced_instance("RC2_2_1_100.txt", vehicle_cost_structure='a')
#
# remove_operators = RemoveOperators()
# insert_operators = InsertionOperators()
# remove_operators_list = [remove_operators.random_customers(),
#                     remove_operators.randomly_selected_sequence_within_concatenated_routes(),
#                     remove_operators.a_posteriori_score_related_customers(),
#                     remove_operators.worst_cost_customers(),
#                     remove_operators.random_route()]
# insert_operators_list = [insert_operators.random_order_best_position(),
#                     insert_operators.customer_with_highest_position_regret_best_position(k=2),
#                     insert_operators.customer_with_highest_position_regret_best_position(k=3)]
#
#
# nos = NeuralOperatorSelector(remove_operators_list, insert_operators_list)
# remove, insert = nos.select_operator(X_predict)
# print(remove.name)
# print(insert.name)