import numpy as np
from typing import List, Optional, Tuple, Any

class ImprovedCTRNN:
    def __init__(self, size: int = 256) -> None:
        self.size: int = size
        self.voltages: np.ndarray = np.zeros(size)
        self.adaptation: np.ndarray = np.zeros(size)
        self.time_constants: np.ndarray = np.random.uniform(2.0, 10.0, size)
        self.biases: np.ndarray = np.random.uniform(-1.0, 1.0, size)
        self.weights: np.ndarray = np.random.uniform(-1.0, 1.0, (size, size))
        self.compress_weights: np.ndarray = np.random.uniform(-0.5, 0.5, (64, 19))
        self.compressed_memory: np.ndarray = np.zeros(64)
        self.voltage_history: List[np.ndarray] = []
        self.attention_weights: np.ndarray = np.random.uniform(-0.5, 0.5, (size, 32))
        self.thinking_mode: int = 0
        self.mode_switch_threshold: float = 0.7
        self.ltm_trace: np.ndarray = np.zeros(size)
        self.ltm_decay: float = 0.999
        self._last_outputs: np.ndarray = np.full(size, 0.5)
        self._prev_motor: np.ndarray = np.array([0.5, 0.5])
        self._batched_net_in: Optional[np.ndarray] = None

    def compress_sensors(self, sensors: np.ndarray) -> np.ndarray:
        compressed: np.ndarray = np.tanh(np.dot(self.compress_weights, sensors))
        self.compressed_memory = 0.9 * self.compressed_memory + 0.1 * compressed
        return self.compressed_memory

    def get_outputs(self, uncertainty: Optional[float] = None) -> np.ndarray:
        active_voltages: np.ndarray = np.clip(self.voltages - (self.adaptation * 1.5), -50, 50)
        if uncertainty is not None:
            self.thinking_mode = 1 if uncertainty > self.mode_switch_threshold else 0
        return 1.0 / (1.0 + np.exp(-active_voltages))

    def tick(self, dt: float, sensors: np.ndarray, uncertainty: Optional[float] = None, 
             use_planning: bool = False, precomputed_net_input: Optional[np.ndarray] = None) -> np.ndarray:
        compressed: np.ndarray = self.compress_sensors(sensors)
        outputs: np.ndarray = self.get_outputs(uncertainty)
        network_input: np.ndarray = precomputed_net_input if precomputed_net_input is not None else np.dot(self.weights, outputs) + self.biases
        total_input: np.ndarray = network_input.copy()
        total_input[:min(self.size, len(compressed))] += compressed[:min(self.size, len(compressed))] * 50.0
        derivative: np.ndarray = (-self.voltages + total_input) / self.time_constants
        self.voltages = np.clip(self.voltages + derivative * dt, -100, 100)
        self.adaptation += (outputs * 0.1 - self.adaptation * 0.05) * dt
        self._last_outputs = outputs
        return outputs