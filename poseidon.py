# === Parameters ===
p = 2**61 - 1  # finite field prime
t = 3          # state width (t=2 inputs + 1 capacity)
R_F = 8        # full rounds
R_P = 57       # partial rounds
alpha = 5      # S-box exponent

# === Round constants and MDS matrix (small toy example) ===
round_constants = [i for i in range((R_F + R_P) * t)]
MDS = [
    [2, 3, 2],
    [3, 2, 3],
    [2, 3, 3]
]

def field_add(x, y): return (x + y) % p
def field_mul(x, y): return (x * y) % p
def field_pow(x, e): return pow(x, e, p)

# === Core steps ===

def add_constants(state, rc, round_idx):
    for i in range(t):
        state[i] = field_add(state[i], rc[round_idx * t + i])
    return state

def sbox(state, full=True):
    if full:
        return [field_pow(x, alpha) for x in state]
    else:
        return [field_pow(state[0], alpha)] + state[1:]

def mix(state, mds):
    return [sum(field_mul(state[j], mds[i][j]) for j in range(t)) % p for i in range(t)]

# === Poseidon Permutation ===
def poseidon_permute(state):
    round_idx = 0

    # Full rounds (first half)
    for _ in range(R_F // 2):
        state = add_constants(state, round_constants, round_idx)
        state = sbox(state, full=True)
        state = mix(state, MDS)
        round_idx += 1

    # Partial rounds
    for _ in range(R_P):
        state = add_constants(state, round_constants, round_idx)
        state = sbox(state, full=False)
        state = mix(state, MDS)
        round_idx += 1

    # Full rounds (second half)
    for _ in range(R_F // 2):
        state = add_constants(state, round_constants, round_idx)
        state = sbox(state, full=True)
        state = mix(state, MDS)
        round_idx += 1

    return state

# === Hashing 2 elements ===
def poseidon_hash(inputs):
    assert len(inputs) == t - 1
    state = inputs + [0]  # last element is capacity
    state = poseidon_permute(state)
    return state[0]  # usually first element is output

if __name__ == "__main__":
    msg = [12345, 67890]
    digest = poseidon_hash(msg)
    print("Poseidon(msg):", digest)
