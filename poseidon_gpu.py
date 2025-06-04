import cupy as cp
print(cp.__version__)

# Define field parameters (example: prime near 2^255)
p = 2**64 - 257

def string_to_field_elements(s: str, p: int, max_bytes_per_elem=31):
    # Convert string to bytes
    b = s.encode('utf-8')

    # Split into chunks
    chunks = [b[i:i+max_bytes_per_elem] for i in range(0, len(b), max_bytes_per_elem)]

    # Convert each chunk to an integer mod p
    field_elements = [int.from_bytes(chunk, 'little') % p for chunk in chunks]
    return field_elements

# Field operations
def fadd(x, y): return (x + y) % p
def fmul(x, y): return (x * y) % p
def fpow(x, e): return cp.power(x, e, dtype=cp.int64) % p
def sbox(x): return fpow(x, 5)  # x^5 mod p

# Toy MDS matrix and round constants (not secure!)
MDS = cp.array([
    [2, 3, 1],
    [1, 2, 3],
    [3, 1, 2]
], dtype=cp.int64)

RC = cp.arange(24, dtype=cp.int64)  # 8 rounds * 3 elements

# Poseidon permutation
def poseidon_permute(state):
    for r in range(8):
        state = fadd(state, RC[r * 3:r * 3 + 3])   # Add round constants
        state = sbox(state)                        # Apply nonlinearity
        state = MDS @ state                        # Mix with MDS matrix
        state = state % p
    return state

# Main Poseidon hash function
def poseidon_hash(inputs):
    assert len(inputs) <= 2
    state = cp.array(inputs + [0], dtype=cp.int64)  # Padding + capacity
    output = poseidon_permute(state)[0]
    return hex(int(output.get()))[2:]


#output = poseidon_hash([123, 456])
#print("Poseidon GPU digest:", hex(int(output.get()))[2:])
