import joblib
import torch
from src.alns_components.neural_operator_selector.neural_network import OperatorSelectionNet, SynergyOperatorSelectionNet
import torch.nn.functional as F

class NeuralOperatorSelector:
    def __init__(self, remove_operators, insert_operators):
        self.remove_operators = remove_operators
        self.insert_operators = insert_operators

        # Import feature scalers
        self.feature_prep = joblib.load("artifacts/feature_prep_s.joblib") #locally: ../../../artifacts/feature_prep.joblib -- global:artifacts/feature_prep_s_nops.joblib
        #self.y_scaler = joblib.load("artifacts/y_scaler.joblib")
        input_dim = len(self.feature_prep.get_feature_names_out())

        # Get model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = OperatorSelectionNet(input_dim).to(self.device)
        #self.model = SynergyOperatorSelectionNet(input_dim).to(self.device)
        # Load weights and biases from the best trained model
        file = "src/alns_components/neural_operator_selector/model_s.pt"
        state = torch.load(file, map_location=self.device) #locally: model_s.pt -- global: src/alns_components/neural_operator_selector/model.pt
        self.model.load_state_dict(state)
        self.model.eval()

    def select_operator(self, X_predict, t=0.1):
        X_transformed = self.feature_prep.transform(X_predict)
        X_tensor = torch.tensor(X_transformed, dtype=torch.float32, device=self.device)

        with torch.no_grad():
            destroy_scores, insert_scores = self.model(X_tensor)

        # # Get the operator index with the best predicted short_long_improvement
        # d_ix = torch.argmin(destroy_scores).item()
        # r_ix = torch.argmin(insert_scores).item()
        # remove_operator = self.remove_operators[d_ix]
        # insert_operator = self.insert_operators[r_ix]

        # Ensure destroy_scores is 1D
        destroy_scores = destroy_scores.view(-1)
        insert_scores = insert_scores.view(-1)

        #new approach with softmax:
        # Compute softmax probabilities over negative scores (lower = better)
        destroy_probs = F.softmax(-destroy_scores / t, dim=0)
        insert_probs = F.softmax(-insert_scores / t, dim=0)

        # Sample an index based on these probabilities
        d_ix = torch.multinomial(destroy_probs, 1).item()
        r_ix = torch.multinomial(insert_probs, 1).item()

        remove_operator = self.remove_operators[d_ix]
        insert_operator = self.insert_operators[r_ix]

        return remove_operator, insert_operator

    # function used to test the model with one-head:
    def _select_operator(self, X_predict):
        X_transformed = self.feature_prep.transform(X_predict)
        X_tensor = torch.tensor(X_transformed, dtype=torch.float32, device=self.device)

        with torch.no_grad():
            pair_scores = self.model(X_tensor)

        # Get the operator index with the best predicted short_long_improvement
        pair_scores = pair_scores.view(-1)
        t = 0.1
        pair_probs = F.softmax(-pair_scores / t, dim=0)
        pair_index = torch.multinomial(pair_probs, 1).item()

        d_ix = pair_index // num_insert
        r_ix = pair_index % num_insert

        remove_operator = self.remove_operators[d_ix]
        insert_operator = self.insert_operators[r_ix]
        return remove_operator, insert_operator
