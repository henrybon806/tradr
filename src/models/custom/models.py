"""Sentiment Analysis Model using PyTorch"""

import torch
import torch.nn as nn
from .base import BaseModel
from typing import Tuple


class SentimentAnalyzerLSTM(BaseModel):
    """LSTM-based sentiment analyzer for financial news
    
    Predicts: positive, negative, neutral sentiment
    """
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embedding_dim: int = 100,
        hidden_dim: int = 128,
        output_size: int = 3,  # positive, negative, neutral
        num_layers: int = 2,
        dropout: float = 0.3,
        bidirectional: bool = True
    ):
        super().__init__(vocab_size, output_size)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # LSTM layer
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )
        
        # Dense layers
        lstm_output_dim = hidden_dim * (2 if bidirectional else 1)
        self.fc1 = nn.Linear(lstm_output_dim, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, output_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
    
    def forward(self, x: torch.Tensor, lengths: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x: Token indices (batch_size, seq_length)
            lengths: Sequence lengths for padding (optional)
        
        Returns:
            Sentiment logits (batch_size, 3)
        """
        # Embedding
        embedded = self.dropout(self.embedding(x))  # (batch, seq_len, embedding_dim)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)  # hidden: (num_layers*directions, batch, hidden_dim)
        
        # Use last hidden state
        hidden = hidden[-1] if self.lstm.bidirectional else hidden[0]  # (batch, hidden_dim*directions)
        
        # Fully connected layers
        out = self.dropout(self.relu(self.fc1(hidden)))
        out = self.dropout(self.relu(self.fc2(out)))
        out = self.fc3(out)  # (batch, 3)
        
        return out


class SentimentAnalyzerTransformer(BaseModel):
    """Transformer-based sentiment analyzer"""
    
    def __init__(
        self,
        vocab_size: int = 10000,
        embedding_dim: int = 128,
        num_heads: int = 8,
        num_layers: int = 4,
        ffn_dim: int = 512,
        output_size: int = 3,
        dropout: float = 0.1,
        max_seq_length: int = 512
    ):
        super().__init__(vocab_size, output_size)
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.positional_encoding = nn.Embedding(max_seq_length, embedding_dim)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification head
        self.fc1 = nn.Linear(embedding_dim, 256)
        self.fc2 = nn.Linear(256, output_size)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x: Token indices (batch_size, seq_length)
            mask: Attention mask (optional)
        
        Returns:
            Sentiment logits (batch_size, 3)
        """
        seq_length = x.shape[1]
        positions = torch.arange(seq_length, device=x.device).unsqueeze(0)
        
        # Embedding + Positional encoding
        embedded = self.embedding(x) + self.positional_encoding(positions)
        embedded = self.dropout(embedded)
        
        # Transformer
        transformer_out = self.transformer(embedded, src_key_padding_mask=mask)
        
        # Mean pooling over sequence
        pooled = transformer_out.mean(dim=1)  # (batch, embedding_dim)
        
        # Classification
        out = self.dropout(self.relu(self.fc1(pooled)))
        out = self.fc2(out)
        
        return out


class PriceMovementPredictor(BaseModel):
    """Predict if stock price will go up/down/stay"""
    
    def __init__(
        self,
        input_features: int = 20,  # Number of technical indicators
        hidden_dim: int = 128,
        num_layers: int = 3,
        output_size: int = 3,  # up, down, neutral
        dropout: float = 0.3
    ):
        super().__init__(input_features, output_size)
        
        layers = []
        in_features = input_features
        
        for i in range(num_layers):
            layers.append(nn.Linear(in_features, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_features = hidden_dim
        
        layers.append(nn.Linear(hidden_dim, output_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Feature tensor (batch_size, num_features)
        
        Returns:
            Price movement logits (batch_size, 3)
        """
        return self.network(x)
