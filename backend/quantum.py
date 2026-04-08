import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class QuantumMetrics:
    qubit_states: List[str]
    entanglement_score: int
    superposition_stability: int
    decoherence_risk: str
    probabilities: List[float]

def _to_angle(value: float, min_val: float, max_val: float) -> float:
    """Map a financial value to a rotation angle in [0, π]"""
    clamped = max(min_val, min(max_val, value))
    return ((clamped - min_val) / (max_val - min_val)) * np.pi

def _ry_gate(theta: float) -> np.ndarray:
    """RY(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]"""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)

def _apply_single_qubit_gate(state: np.ndarray, n: int, target: int, gate: np.ndarray) -> np.ndarray:
    """Apply a single-qubit gate to qubit `target` in an n-qubit state vector"""
    # Build full gate via tensor product: I ⊗ ... ⊗ gate ⊗ ... ⊗ I
    full_gate = np.array([[1.0]], dtype=complex)
    for i in range(n):
        full_gate = np.kron(full_gate, gate if i == target else np.eye(2, dtype=complex))
    return full_gate @ state

def _apply_cnot(state: np.ndarray, n: int, control: int, target: int) -> np.ndarray:
    """Apply CNOT gate: flips target qubit when control qubit is |1⟩"""
    dim = 1 << n
    new_state = state.copy()
    for i in range(dim):
        control_bit = (i >> (n - 1 - control)) & 1
        if control_bit == 1:
            flipped = i ^ (1 << (n - 1 - target))
            if i < flipped:
                new_state[i], new_state[flipped] = state[flipped].copy(), state[i].copy()
    return new_state

def _measure_prob1(state: np.ndarray, n: int, qubit: int) -> float:
    """Born rule: probability of measuring qubit in state |1⟩"""
    prob = 0.0
    for i in range(1 << n):
        if (i >> (n - 1 - qubit)) & 1:
            prob += abs(state[i]) ** 2
    return prob

def _classify_state(prob1: float) -> str:
    """Classify qubit state from Bloch sphere Z-axis value"""
    z = 1 - 2 * prob1
    if z > 0.6:
        return "|0⟩"
    elif z < -0.6:
        return "|1⟩"
    elif abs(z) < 0.15:
        return "|+⟩"
    return "|-⟩"

def run_quantum_circuit(
    change_percent: float,
    volume_ratio: float,
    week52_position: float,
    sentiment_score: float,
) -> QuantumMetrics:
    """
    Real quantum circuit simulator:
    - 4 qubits initialized to |0000⟩
    - RY gates encode financial data as rotation angles
    - CNOT gates create entanglement between qubits
    - Born rule computes measurement probabilities
    - Metrics derived from quantum state math
    """
    N = 4

    # Map financial data to rotation angles [0, π]
    theta0 = _to_angle(change_percent, -0.1, 0.1)       # q0: price change
    theta1 = _to_angle(volume_ratio, 0.5, 3.0)           # q1: volume ratio
    theta2 = _to_angle(week52_position, 0.0, 1.0)        # q2: 52w position
    theta3 = _to_angle(sentiment_score, 0.0, 100.0)      # q3: FinBERT sentiment

    # Initialize |0000⟩ state vector (2^4 = 16 amplitudes)
    state = np.zeros(1 << N, dtype=complex)
    state[0] = 1.0

    # Layer 1: RY rotations — encode financial data into qubits
    state = _apply_single_qubit_gate(state, N, 0, _ry_gate(theta0))
    state = _apply_single_qubit_gate(state, N, 1, _ry_gate(theta1))
    state = _apply_single_qubit_gate(state, N, 2, _ry_gate(theta2))
    state = _apply_single_qubit_gate(state, N, 3, _ry_gate(theta3))

    # Layer 2: CNOT entanglement
    state = _apply_cnot(state, N, 0, 1)  # price ↔ volume
    state = _apply_cnot(state, N, 2, 3)  # 52w position ↔ sentiment
    state = _apply_cnot(state, N, 1, 2)  # cross-entangle middle qubits

    # Layer 3: Second RY layer (variational depth)
    state = _apply_single_qubit_gate(state, N, 0, _ry_gate(theta3 * 0.5))
    state = _apply_single_qubit_gate(state, N, 3, _ry_gate(theta0 * 0.5))

    # Measure: Born rule probabilities
    probs = [_measure_prob1(state, N, q) for q in range(N)]

    # Qubit state labels from Bloch sphere
    qubit_states = [_classify_state(p) for p in probs]

    # Entanglement Score: average mixedness of qubits
    entanglement_score = int(np.clip(
        round(sum(4 * p * (1 - p) for p in probs) / N * 100), 0, 100
    ))

    # Superposition Stability: variance of probs around 0.5
    variance = sum((p - 0.5) ** 2 for p in probs) / N
    superposition_stability = int(np.clip(
        round((1 - np.sqrt(variance) * 2) * 100), 0, 100
    ))

    # Decoherence Risk: purity of quantum state
    purity = sum(p ** 2 + (1 - p) ** 2 for p in probs) / N
    if purity > 0.85:
        decoherence_risk = "High"
    elif purity > 0.65:
        decoherence_risk = "Medium"
    else:
        decoherence_risk = "Low"

    return QuantumMetrics(
        qubit_states=qubit_states,
        entanglement_score=entanglement_score,
        superposition_stability=superposition_stability,
        decoherence_risk=decoherence_risk,
        probabilities=[round(p, 2) for p in probs],
    )
