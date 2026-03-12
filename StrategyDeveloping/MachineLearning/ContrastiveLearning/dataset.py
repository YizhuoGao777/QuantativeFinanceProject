import numpy as np
import torch
from torch.utils.data import Dataset
import torch
from torch.nn.utils.rnn import pad_sequence

def collate_fn(batch):
    anchors, positives, negatives = zip(*batch)

    def pad_and_stack(sequences):
        return pad_sequence(sequences, batch_first=True)

    anchors = pad_and_stack(anchors)
    positives = pad_and_stack(positives)
    negatives = pad_and_stack(negatives)

    return anchors, positives, negatives



class ContrastiveDataset(Dataset):
    def __init__(self, path):
        data = np.load(path, allow_pickle=True)
        self.anchors = data['anchor']  # shape: [N, T, F]
        self.positives = data['positive']
        self.negatives = data['negative']

    def __len__(self):
        return len(self.anchors)

    def __getitem__(self, idx):
        anchor = np.array(self.anchors[idx], dtype=np.float32)
        positive = np.array(self.positives[idx], dtype=np.float32)
        negative = np.array(self.negatives[idx], dtype=np.float32)

        return (
            torch.tensor(anchor),
            torch.tensor(positive),
            torch.tensor(negative),
        )

