import torch.nn as nn
import torch

class ContrastiveModel(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=4, batch_first=True),
            num_layers=2
        )
        self.proj = nn.Linear(input_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x):
        x = self.proj(x)  # [B, T, H]
        x = self.transformer(x)
        x = x.mean(dim=1)  # mean pooling
        return self.out(x)
