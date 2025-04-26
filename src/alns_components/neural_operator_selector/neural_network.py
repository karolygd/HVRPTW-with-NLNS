import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd

# Create a dataset object for the dataloader
class ALNSDataset(Dataset):
    def __init__(self, csv_file):
        # Load the CSV into a DataFrame
        self.df = pd.read_csv(csv_file)
        # Identify which columns are features.
        self.feature_columns = ['iterations',
                                    'instance_type',
                                    'tw_spread',
                                    'operator_selection_mechanism',
                                    'number_of_vertices_to_remove',
                                    "rel_delta_last_improv",
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
                                    'success_i_op_3']

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        # Get feature values from all feature columns and convert to a tensor.
        features = torch.tensor(row[self.feature_columns].values, dtype=torch.float32)
        # Get destroy and insert operator indices (assuming they are stored as integers)
        destroy_idx = torch.tensor(int(row['chosen_remove_operator']), dtype=torch.int)
        insert_idx = torch.tensor(int(row['chosen_insert_operator']), dtype=torch.int)
        # Get the target value (blended improvement) as a float
        target = torch.tensor(float(row['short_long_improvement']), dtype=torch.float32)

        return features, destroy_idx, insert_idx, target

# Create datasets from your CSV files
train_dataset = ALNSDataset('../../../training_data_nn/c1_training.csv')
val_dataset = ALNSDataset('../../../training_data_nn/c1_validation.csv')
test_dataset = ALNSDataset('../../../training_data_nn/c1_test.csv')

# Create DataLoaders. Adjust batch_size and num_workers as needed.
batch_size = 40   # Todo: check the effect of changing batch size - should it be multiples of 20 according to my segment_size = 20 in alns?
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False) # Todo: change to True and see if changes in loss function
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

class OperatorSelectionNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_destroy=5, num_insert=3):
        super(OperatorSelectionNet, self).__init__()

        # Shared layers (simple example: 2 hidden layers)
        self.shared_fc1 = nn.Linear(input_dim, hidden_dim)
        self.shared_fc2 = nn.Linear(hidden_dim, hidden_dim)

        # Destroy head: outputs a score for each of the 5 destroy ops
        self.destroy_head = nn.Linear(hidden_dim, num_destroy)

        # Insert head: outputs a score for each of the 3 insert ops
        self.insert_head = nn.Linear(hidden_dim, num_insert)

        # Activation
        self.relu = nn.ReLU()

    def forward(self, x):
        # Pass input through shared layers
        x = self.relu(self.shared_fc1(x))
        x = self.relu(self.shared_fc2(x))

        # Separate heads
        destroy_scores = self.destroy_head(x)  # [batch_size, 5]
        insert_scores = self.insert_head(x)  # [batch_size, 3]

        return destroy_scores, insert_scores

# We need a partial MSE: only the chosen operator’s score in each head is compared to the target y. The other scores are not updated for that sample.
def partial_mse_loss(destroy_scores, insert_scores, d_idx, r_idx, y):
    """
    destroy_scores: (batch_size, 5)
    insert_scores:  (batch_size, 3)
    d_idx:          (batch_size,) chosen destroy operator indices
    r_idx:          (batch_size,) chosen insert operator indices
    y:              (batch_size,) improvement label

    Returns scalar loss (MSE).
    """
    batch_size = destroy_scores.size(0)
    # Gather the destroy_score for each chosen operator
    pred_destroy = destroy_scores[range(batch_size), d_idx-1] # I should have labeled my operators starting from 0 not 1

    # Gather the insert_score for each chosen operator
    pred_insert = insert_scores[range(batch_size), r_idx-1] # I should have labeled my operators starting from 0 not 1

    # MSE for each chosen operator vs. the same label y
    # We assume y is the "blended improvement" credited to both ops
    loss_destroy = (pred_destroy - y) ** 2
    loss_insert = (pred_insert - y) ** 2

    # Combine the losses, for example average them
    # (some might choose to weigh them differently, but 1:1 is common)
    loss = (loss_destroy.mean() + loss_insert.mean()) / 2.0

    return loss
#
# # How data should look like:

# # N = 10000
# # X_data = np.random.rand(N, input_dim).astype(np.float32)
# # # Random chosen destroy operator in [0..4]
# # d_data = np.random.randint(0, num_destroy, size=(N,))
# # # Random chosen insert operator in [0..2]
# # r_data = np.random.randint(0, num_insert, size=(N,))
# # # Random "improvement" labels, e.g. in range [-2.0, +2.0]
# # y_data = 4.0 * (np.random.rand(N) - 0.5).astype(np.float32)
# # # Convert to PyTorch tensors
# # X_tensor = torch.from_numpy(X_data)
# # d_tensor = torch.from_numpy(d_data)
# # r_tensor = torch.from_numpy(r_data)
# # y_tensor = torch.from_numpy(y_data)
#
# Hyperparameters
num_epochs = 50
learning_rate = 1e-3
hidden_dim = 64 # determines the number of neurons in the hidden layers of the model

# Initialize model, optimizer
input_dim = 20
num_destroy = 5
num_insert = 3
model = OperatorSelectionNet(input_dim=input_dim, hidden_dim=hidden_dim,
                             num_destroy=num_destroy, num_insert=num_insert)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# # Convert everything to float tensors on CPU (or GPU if desired)
# X_tensor = X_tensor.float()
# y_tensor = y_tensor.float()

# Simple training loop
train_loss_list = []
validation_loss_list = []
for epoch in range(num_epochs):
    model.train() # Set model to training mode
    for features, d_idx, i_idx, target in train_loader:
        # Forward pass through your model (the model returns destroy and insert scores)
        destroy_scores, insert_scores = model(features)
        loss = partial_mse_loss(destroy_scores, insert_scores, d_idx, i_idx, target)
        # Backprop
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Accumulate metrics and print statistics
        train_loss_list.append(loss.item())

    # Optionally evaluate on the validation set here
    model.eval()
    with torch.no_grad():
        for features, d_idx, i_idx, target in val_loader:
            destroy_scores, insert_scores = model(features)
            val_loss = partial_mse_loss(destroy_scores, insert_scores, d_idx, i_idx, target)
            validation_loss_list.append(val_loss.item())

    # Accumulate metrics and print statistics
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch + 1}/{num_epochs}"
              f" - Train Loss = {train_loss_list[-1]:.4f} - Validation Loss = {validation_loss_list[-1]:.4f}\n")


# Inference Operator Selector:
# with torch.no_grad():
#     destroy_scores, insert_scores = model(x_tensor)
#     best_destroy = torch.argmax(destroy_scores, dim=1).item()
#     best_insert = torch.argmax(insert_scores, dim=1).item()
#
# print("Chosen destroy operator:", best_destroy)
# print("Chosen insert operator:", best_insert)

# Optionally, incorporate ϵ-greedy or a softmax-based sampling if you want to maintain exploration.