import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
import matplotlib.pyplot as plt
import pandas as pd
import joblib

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create a dataset object for the dataloader
class ALNSDataset(Dataset):
    def __init__(self, datasource, feature_transformer, y_scaler):
        self.df = datasource.copy()
        self.feature_columns = ['iterations', 'acceptance_ratio', 'number_of_vertices_to_remove', 'i_last_improv',
                                'route_imbalance', 'capacity_utilization', 'success_r_op_1', 'success_r_op_2',
                                'success_r_op_3', 'success_r_op_4', 'success_r_op_5', 'success_i_op_1',
                                'success_i_op_2', 'success_i_op_3', 'rel_delta_last_improv', 'instance_type',
                                'tw_spread', 'operator_selection_mechanism', 'prev_remove_operator',
                                'prev_insert_operator']

        # transform data
        X_np = feature_transformer.transform(self.df[self.feature_columns])
        self.X = torch.tensor(X_np, dtype=torch.float32)

        # operator indices (0-based for easy gather())
        self.d_idx = torch.tensor(self.df['chosen_remove_operator'].values,
                                  dtype=torch.long)
        self.i_idx = torch.tensor(self.df['chosen_insert_operator'].values,
                                  dtype=torch.long)

        # target, scaled like during training
        y_np = y_scaler.transform(
            self.df[['short_long_improvement']]).reshape(-1)
        self.y = torch.tensor(y_np, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.d_idx[idx], self.i_idx[idx], self.y[idx]

class OperatorSelectionNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, hidden_dim_2=128, num_destroy=5, num_insert=3, p_drop=0.3):
        super(OperatorSelectionNet, self).__init__()

        # shared backbone
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p_drop),
            nn.Linear(hidden_dim, hidden_dim_2),
            nn.ReLU(),
            nn.Dropout(p_drop)
        )

        # task-specific heads
        self.destroy_head = nn.Linear(hidden_dim_2, num_destroy)
        self.insert_head = nn.Linear(hidden_dim_2, num_insert)

    def forward(self, x):
        # Pass input through shared layers
        x = self.backbone(x)
        return self.destroy_head(x), self.insert_head(x)

class SynergyOperatorSelectionNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_destroy=5, num_insert=3, p_drop=0.5):
        super().__init__()
        self.num_pairs = num_destroy * num_insert

        # shared backbone
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(),
            nn.Dropout(p_drop),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(),
            nn.Dropout(p_drop)
        )

        # task-specific heads
        self.pairs_head = nn.Linear(hidden_dim, self.num_pairs)

    def forward(self, x):
        # Pass input through shared layers
        h = self.backbone(x)
        pairs = self.pairs_head(h)
        return pairs

    def synergies(self, x):
        logits = self.forward(x)
        return logits.view(-1, self.num_destroy, self.num_insert)

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
    pred_destroy = destroy_scores[range(batch_size), d_idx]

    # Gather the insert_score for each chosen operator
    pred_insert = insert_scores[range(batch_size), r_idx]

    # MSE for each chosen operator vs. the same label y
    # We assume y is the "blended improvement" credited to both ops
    loss_destroy = (pred_destroy - y) ** 2
    loss_insert = (pred_insert - y) ** 2

    # Combine the losses, for example average them
    # (some might choose to weigh them differently, but 1:1 is common)
    loss = (loss_destroy.mean() + loss_insert.mean()) / 2.0

    return loss

def pairs_mse_loss(pair_scores, d_idx, r_idx, y, num_insert):
    """
    pair_scores:    (batch_size, d*i)
    d_idx:          (batch_size,) chosen destroy operator indices
    r_idx:          (batch_size,) chosen insert operator indices
    y:              (batch_size,) improvement label

    Returns scalar loss (MSE).
    """
    batch_size = pair_scores.size(0)
    flat_idx = d_idx * num_insert + r_idx
    pred = pair_scores[torch.arange(batch_size), flat_idx]
    loss = F.mse_loss(pred, y)

    return loss

# # Create datasets for training
# train_df = pd.read_csv('../../../training_data_nn/c1_training.csv')
# val_df = pd.read_csv('../../../training_data_nn/c1_validation.csv')
#
# feature_prep = joblib.load("/feature_prep.joblib")
# y_scaler = joblib.load("/y_scaler.joblib")
#
# train_ds = ALNSDataset(train_df, feature_prep, y_scaler)
# val_ds   = ALNSDataset(val_df, feature_prep, y_scaler)
#
# batch_size = 100    # Change batch size and see effect
# train_loader = DataLoader(train_ds, batch_size, shuffle=False,  num_workers=0)   #check the effect of shuffle=True -> By shuffling the data the model has lower loss in training, but higher loss in validation
# val_loader   = DataLoader(val_ds,   batch_size, shuffle=False, num_workers=0)
#
# input_dim = train_ds.X.shape[1]
#
# # Training loop
# epochs = 150 #can add more epochs in the final training
# learning_rate = 3e-4 #before: 1e-3, train_loss=Epoch 46: train_loss=0.725729, val_loss=0.804593
#
# model = OperatorSelectionNet(input_dim).to(device) # move model to GPU
# opt  = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-5)
# scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
#                opt, mode='min', factor=0.5, patience=3)
#
# best_val_loss = float('inf')
# patience = 40 # Epochs to wait without improvement, #10, 15
# patience_counter = 0  # counts epochs without improvement
#
# train_losses = []
# val_losses = []
# for epoch in range(epochs):
#     # --- Training ---
#     model.train()
#     train_loss = 0
#     correct, total = 0, 0
#     for X, d_idx, r_idx, y in train_loader:
#         X = X.to(device)
#         d_idx = d_idx.to(device)
#         r_idx = r_idx.to(device)
#         y = y.to(device)
#
#         # print("debug X.size(0): ", X.size())
#         # print("debug d_idx.size(): ", d_idx.size())
#         # print("debug r_idx.size(): ", r_idx.size())
#         # print("debug y.size(): ", y.size())
#
#         # Forward pass through your model (the returns destroy and insert scores)
#         d_scores, r_scores = model(X)
#         loss = partial_mse_loss(d_scores, r_scores, d_idx, r_idx, y)
#         # Backpropagation:
#         opt.zero_grad()
#         loss.backward()
#         opt.step()
#
#         #print("debug loss.item(): ", loss.item())
#         train_loss += loss.item()*X.size(0) # sum up weighted by batch size
#
#     train_loss /= len(train_loader.dataset)
#
#     # --- Validation ---
#     model.eval()
#     val_loss = 0
#     with torch.no_grad():
#         for X_val, d_idx_val, r_idx_val, y_val in val_loader:
#             X_val = X_val.to(device)
#             d_idx_val = d_idx_val.to(device)
#             r_idx_val = r_idx_val.to(device)
#             y_val = y_val.to(device)
#
#             d_scores, r_scores = model(X_val)
#             loss = partial_mse_loss(d_scores, r_scores, d_idx_val, r_idx_val, y_val)
#             val_loss += loss.item() * X_val.size(0)
#
#     val_loss /= len(val_loader.dataset)
#
#     train_losses.append(train_loss)
#     val_losses.append(val_loss)
#
#     print(f"Epoch {epoch}: train_loss={train_loss:.6f}, val_loss={val_loss:.6f}")
#     scheduler.step(val_loss)
#     # ----- Save best model -----
#     if val_loss < best_val_loss:
#         best_val_loss = val_loss
#         patience_counter = 0 # reset counter
#         torch.save(model.state_dict(), "/Workspace/Users/d505571@burda.com/project/model.pt")
#         print(f"Saved new best model at epoch {epoch}")
#     else:
#         patience_counter += 1
#
#     if patience_counter >= patience:
#         print(f"Early stopping at epoch {epoch} (no improvement for {patience} epochs)")
#         break
#
# # Plot Learning Curves
# plt.figure(figsize=(10,6))
# plt.plot(train_losses, label="Train Loss")
# plt.plot(val_losses, label="Validation Loss")
# plt.xlabel("Epoch")
# plt.ylabel("Loss")
# plt.title("Learning Curves")
# plt.legend()
# plt.grid(True)
# plt.show()