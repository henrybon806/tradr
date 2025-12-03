"""Example usage of custom PyTorch models"""

import torch
from torch.utils.data import TensorDataset, DataLoader
from .models import SentimentAnalyzerLSTM, PriceMovementPredictor
from .trainer import ModelTrainer


def example_sentiment_training():
    """Example: Train sentiment analyzer"""
    print("=== Sentiment Analyzer LSTM Training ===\n")
    
    # Create dummy data
    batch_size = 32
    seq_length = 100
    vocab_size = 10000
    num_classes = 3  # positive, negative, neutral
    
    # Dummy training data
    X_train = torch.randint(0, vocab_size, (1000, seq_length))
    y_train = torch.randint(0, num_classes, (1000,))
    
    X_val = torch.randint(0, vocab_size, (200, seq_length))
    y_val = torch.randint(0, num_classes, (200,))
    
    # Create dataloaders
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Create model
    model = SentimentAnalyzerLSTM(
        vocab_size=vocab_size,
        embedding_dim=100,
        hidden_dim=128,
        output_size=num_classes,
        num_layers=2,
        dropout=0.3
    )
    
    # Create trainer
    trainer = ModelTrainer(model)
    
    # Train
    history = trainer.fit(
        train_loader,
        val_loader,
        epochs=5,
        early_stopping_patience=3
    )
    
    print("\nTraining complete!")
    print(f"Final train loss: {history['train_loss'][-1]:.4f}")
    print(f"Final val loss: {history['val_loss'][-1]:.4f}")
    print(f"Final val accuracy: {history['val_acc'][-1]:.2f}%\n")
    
    # Save model
    model.save_checkpoint("sentiment_model.pth")
    print("Model saved to sentiment_model.pth\n")
    
    return model, trainer


def example_price_prediction():
    """Example: Train price movement predictor"""
    print("=== Price Movement Predictor Training ===\n")
    
    # Create dummy data
    batch_size = 32
    num_features = 20  # Technical indicators
    num_samples = 500
    num_classes = 3  # up, down, neutral
    
    X_train = torch.randn(num_samples, num_features)
    y_train = torch.randint(0, num_classes, (num_samples,))
    
    X_val = torch.randn(100, num_features)
    y_val = torch.randint(0, num_classes, (100,))
    
    # Create dataloaders
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Create model
    model = PriceMovementPredictor(
        input_features=num_features,
        hidden_dim=128,
        num_layers=3,
        output_size=num_classes,
        dropout=0.3
    )
    
    # Create trainer
    trainer = ModelTrainer(model)
    
    # Train
    history = trainer.fit(
        train_loader,
        val_loader,
        epochs=5,
        early_stopping_patience=3
    )
    
    print("\nTraining complete!")
    print(f"Final train loss: {history['train_loss'][-1]:.4f}")
    print(f"Final val loss: {history['val_loss'][-1]:.4f}")
    print(f"Final val accuracy: {history['val_acc'][-1]:.2f}%\n")
    
    # Save model
    model.save_checkpoint("price_predictor.pth")
    print("Model saved to price_predictor.pth\n")
    
    return model, trainer


def example_inference():
    """Example: Load and use trained model"""
    print("=== Model Inference Example ===\n")
    
    # Load sentiment model
    model = SentimentAnalyzerLSTM(vocab_size=10000, output_size=3)
    model.load_checkpoint("sentiment_model.pth")
    
    trainer = ModelTrainer(model)
    
    # Make prediction
    sample_text = torch.randint(0, 10000, (1, 100))  # 1 sample, 100 tokens
    probabilities = trainer.predict(sample_text)
    
    sentiment_map = {0: "Positive", 1: "Negative", 2: "Neutral"}
    predicted_class = probabilities.argmax(dim=1).item()
    confidence = probabilities[0, predicted_class].item()
    
    print(f"Predicted sentiment: {sentiment_map[predicted_class]}")
    print(f"Confidence: {confidence:.4f}")
    print(f"All probabilities: {probabilities[0].cpu().numpy()}\n")


if __name__ == "__main__":
    # Run examples
    model1, trainer1 = example_sentiment_training()
    model2, trainer2 = example_price_prediction()
    example_inference()
