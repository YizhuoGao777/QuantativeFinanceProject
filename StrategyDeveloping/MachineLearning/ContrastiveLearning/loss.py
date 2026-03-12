import torch
import torch.nn.functional as F

def contrastive_loss(anchor, positive, negative, temperature=0.1):
    pos_sim = F.cosine_similarity(anchor, positive)
    neg_sim = F.cosine_similarity(anchor, negative)
    logits = torch.cat([pos_sim.unsqueeze(1), neg_sim.unsqueeze(1)], dim=1)
    labels = torch.zeros(anchor.size(0), dtype=torch.long).to(anchor.device)
    return F.cross_entropy(logits / temperature, labels)
