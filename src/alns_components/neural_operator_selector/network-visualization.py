import torch
from torch.utils.tensorboard import SummaryWriter
from src.alns_components.neural_operator_selector.neural_network import OperatorSelectionNet

# Create dummy input
input_dim = 32  # match your real input dimension
dummy_input = torch.randn(1, input_dim)

# Initialize model
model = OperatorSelectionNet(input_dim=input_dim)

# Create TensorBoard writer
writer = SummaryWriter(log_dir="runs/operator_selection")

# Add model graph
writer.add_graph(model, dummy_input)

# Close writer
writer.close()