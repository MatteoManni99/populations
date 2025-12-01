"""
Small flexible fully-connected neural network in PyTorch (Classification)
- N fully connected (Linear) layers
- Designed for classification tasks (logits output compatible with CrossEntropyLoss)
- Option to provide activations per layer (or a single activation for all hidden layers)
- Methods to set/get layer parameters (weights and biases)
- Helpers: predict_proba, predict, evaluate (accuracy on a DataLoader), save/load
- No training loop included (as requested)

Usage:
    python pytorch_fcnet.py

Requires: torch
"""

from typing import List, Optional, Sequence, Tuple, Union
import torch
import torch.nn as nn
from torch.utils.data import DataLoader


class FCClassifier(nn.Module):
    """Fully-connected classifier with N Linear layers.

    Args:
        layer_sizes: list of ints describing sizes including input and output.
            Example: [input_dim, hidden1, hidden2, num_classes]
        activations: either a single activation name applied to all hidden layers
            or a list of activation names with length len(layer_sizes)-1.
            Supported: 'relu', 'tanh', 'sigmoid', 'identity', 'leaky_relu'
        bias: whether to use bias in Linear layers
        init: weight initialization method for Linear layers. Supported: 'xavier', 'kaiming', 'normal', 'zero', or None
    """

    def __init__(
        self,
        layer_sizes: Sequence[int],
        activations: Union[str, Sequence[str]] = "relu",
        bias: bool = True,
        init: Optional[str] = "xavier",
    ) -> None:
        super().__init__()
        if len(layer_sizes) < 2:
            raise ValueError("layer_sizes must contain at least input and output sizes")

        self.layer_sizes = list(layer_sizes)
        n_layers = len(self.layer_sizes) - 1

        # Normalize activations to list of length n_layers
        if isinstance(activations, str):
            activations = [activations] * n_layers
        else:
            if len(activations) != n_layers:
                raise ValueError("activations length must match number of layers")
            activations = list(activations)

        self.activations = activations
        self.bias = bias

        # Create linear layers
        self.layers = nn.ModuleList()
        for i in range(n_layers):
            in_dim = self.layer_sizes[i]
            out_dim = self.layer_sizes[i + 1]
            self.layers.append(nn.Linear(in_dim, out_dim, bias=bias))

        # Map activation names to callables
        self._act_fns = [self._make_activation(a) for a in self.activations]

        # Apply initialization
        if init is not None:
            self._initialize_weights(init)

    def _make_activation(self, name: str):
        name = name.lower()
        if name == "relu":
            return nn.ReLU()
        if name == "tanh":
            return nn.Tanh()
        if name == "sigmoid":
            return nn.Sigmoid()
        if name == "identity":
            return nn.Identity()
        if name == "leaky_relu":
            return nn.LeakyReLU()
        raise ValueError(f"Unsupported activation: {name}")

    def _initialize_weights(self, method: str) -> None:
        method = method.lower()
        for layer in self.layers:
            if not isinstance(layer, nn.Linear):
                continue
            if method == "xavier":
                nn.init.xavier_uniform_(layer.weight)
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
            elif method == "kaiming":
                nn.init.kaiming_uniform_(layer.weight, nonlinearity='relu')
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
            elif method == "normal":
                nn.init.normal_(layer.weight, mean=0.0, std=0.01)
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
            elif method == "zero":
                nn.init.zeros_(layer.weight)
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
            else:
                raise ValueError(f"Unknown init method: {method}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. Applies each linear layer followed by its activation.
        The activation for the final layer is applied as well; for classification it's typical to use
        'identity' on the last layer and then feed logits to CrossEntropyLoss.
        """
        out = x
        for layer, act in zip(self.layers, self._act_fns):
            out = layer(out)
            out = act(out)
        return out

    # ----- Classification helpers -----
    def predict_proba(self, x: torch.Tensor, dim: int = 1) -> torch.Tensor:
        """Return class probabilities (softmax over logits)."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probs = torch.softmax(logits, dim=dim)
        return probs

    def predict(self, x: torch.Tensor, dim: int = 1) -> torch.Tensor:
        """Return predicted class indices (argmax over probabilities)."""
        probs = self.predict_proba(x, dim=dim)
        return torch.argmax(probs, dim=dim)

    def evaluate(self, dataloader: DataLoader, device: Optional[torch.device] = None) -> float:
        """Compute accuracy over a DataLoader. Expects dataset yields (inputs, labels) where labels are integer class indices.

        Returns accuracy in [0,1].
        """
        if device is None:
            device = next(self.parameters()).device
        self.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for xb, yb in dataloader:
                xb = xb.to(device)
                yb = yb.to(device)
                preds = self.predict(xb)
                if preds.ndim > 1:
                    preds = preds.view(-1)
                if yb.ndim > 1:
                    yb = yb.view(-1)
                correct += (preds.to(yb.device) == yb).sum().item()
                total += yb.numel()
        return correct / total if total > 0 else 0.0

    # ----- Parameter utilities -----
    def set_layer_parameters(
        self, layer_idx: int, weight: torch.Tensor, bias: Optional[torch.Tensor] = None
    ) -> None:
        """Set weight (and optionally bias) for a specific layer.

        weight should have shape (out_features, in_features).
        bias should have shape (out_features,).
        """
        if not (0 <= layer_idx < len(self.layers)):
            raise IndexError("layer_idx out of range")
        layer = self.layers[layer_idx]
        with torch.no_grad():
            if weight.shape != layer.weight.shape:
                raise ValueError(f"weight shape mismatch: expected {layer.weight.shape}, got {weight.shape}")
            layer.weight.copy_(weight)
            if bias is not None:
                if not self.bias:
                    raise ValueError("this network was constructed without bias")
                if bias.shape != layer.bias.shape:
                    raise ValueError(f"bias shape mismatch: expected {layer.bias.shape}, got {bias.shape}")
                layer.bias.copy_(bias)

    def get_layer_parameters(self, layer_idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Return (weight, bias) tensors for a specific layer. Bias may be None if not used."""
        if not (0 <= layer_idx < len(self.layers)):
            raise IndexError("layer_idx out of range")
        layer = self.layers[layer_idx]
        return layer.weight.detach().clone(), (layer.bias.detach().clone() if layer.bias is not None else None)

    def set_all_parameters(self, params: Sequence[Tuple[torch.Tensor, Optional[torch.Tensor]]]) -> None:
        """Set parameters for all layers from a sequence of (weight, bias) tuples.

        Length of params must equal number of layers.
        """
        if len(params) != len(self.layers):
            raise ValueError("params length must match number of layers")
        for i, (w, b) in enumerate(params):
            self.set_layer_parameters(i, w, b)

    def get_all_parameters(self) -> List[Tuple[torch.Tensor, Optional[torch.Tensor]]]:
        """Return list of (weight, bias) for all layers."""
        out = []
        for i in range(len(self.layers)):
            out.append(self.get_layer_parameters(i))
        return out

    # ----- Save / Load -----
    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    def load(self, path: str, map_location: Optional[Union[str, torch.device]] = None) -> None:
        state = torch.load(path, map_location=map_location)
        self.load_state_dict(state)


# Example usage
def example_usage():
    # esempio: classificatore 4 -> 8 -> 3 (3 classi)
    net = FCClassifier([4, 8, 3], activations=["relu", "identity"], bias=True, init="xavier")
    print(net)

    # Dummy input
    x = torch.randn(5, 4)
    logits = net(x)                # shape (5, 3)
    probs = net.predict_proba(x)   # shape (5, 3)
    preds = net.predict(x)         # shape (5,)
    print('logits shape:', logits.shape)
    print('probs shape:', probs.shape)
    print('preds:', preds)

    # Esempio: leggere e impostare pesi del primo layer
    w0, b0 = net.get_layer_parameters(0)
    print('layer 0 weight shape:', w0.shape)
    net.set_layer_parameters(0, torch.full_like(w0, 0.05), torch.zeros_like(b0) if b0 is not None else None)
    print('first weight element after set:', net.get_layer_parameters(0)[0].view(-1)[0].item())

    # Salva e carica modello
    net.save('fc_classifier.pth')
    net.load('fc_classifier.pth')
    print('Model saved and loaded successfully.')
