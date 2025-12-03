"""Base PyTorch model classes"""

import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import Tuple


class BaseModel(nn.Module, ABC):
    """Abstract base class for all ML models"""
    
    def __init__(self, input_size: int, output_size: int):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size
    
    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass - must be implemented by subclasses"""
        pass
    
    def train_mode(self):
        """Set model to training mode"""
        self.train()
    
    def eval_mode(self):
        """Set model to evaluation mode"""
        self.eval()
    
    def save_checkpoint(self, path: str):
        """Save model checkpoint"""
        torch.save(self.state_dict(), path)
    
    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        self.load_state_dict(torch.load(path))
    
    def get_device(self) -> torch.device:
        """Get device model is on (CPU or GPU)"""
        return next(self.parameters()).device
    
    def move_to_device(self, device: torch.device):
        """Move model to specified device"""
        self.to(device)
