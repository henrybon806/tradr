"""Training utilities for PyTorch models"""

import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from typing import Tuple, Dict, List
import numpy as np


class ModelTrainer:
    """Utility class for training PyTorch models"""
    
    def __init__(
        self,
        model: nn.Module,
        device: torch.device = None,
        loss_fn: nn.Module = None,
        optimizer: Optimizer = None
    ):
        self.model = model
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loss_fn = loss_fn or nn.CrossEntropyLoss()
        self.model.to(self.device)
        
        if optimizer is None:
            self.optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        else:
            self.optimizer = optimizer
        
        self.train_losses = []
        self.val_losses = []
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            outputs = self.model(inputs)
            loss = self.loss_fn(outputs, targets)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        self.train_losses.append(avg_loss)
        return avg_loss
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Validate model and return loss and accuracy"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.loss_fn(outputs, targets)
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        self.val_losses.append(avg_loss)
        
        return avg_loss, accuracy
    
    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader = None,
        epochs: int = 10,
        early_stopping_patience: int = 5
    ) -> Dict:
        """Train model for multiple epochs"""
        best_val_loss = float('inf')
        patience_counter = 0
        history = {"train_loss": [], "val_loss": [], "val_acc": []}
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            history["train_loss"].append(train_loss)
            
            if val_loader:
                val_loss, val_acc = self.validate(val_loader)
                history["val_loss"].append(val_loss)
                history["val_acc"].append(val_acc)
                
                print(f"Epoch {epoch+1}/{epochs} - Train: {train_loss:.4f}, Val: {val_loss:.4f}, Acc: {val_acc:.2f}%")
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping_patience:
                        print(f"Early stopping at epoch {epoch+1}")
                        break
            else:
                print(f"Epoch {epoch+1}/{epochs} - Train: {train_loss:.4f}")
        
        return history
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions on new data"""
        self.model.eval()
        x = x.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(x)
            probabilities = torch.softmax(outputs, dim=1)
        
        return probabilities
