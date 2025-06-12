import cupy as cp
import sys
sys.path.append("external/poseidon-hash")
from poseidon import Poseidon, parameters
print(cp.__version__)

# Define field parameters 
p = parameters.prime_64  # Use a prime from Poseidon parameters
security_level = 128
input_rate = 8
t = 9
full_round = 8
partial_round = 41
alpha = 3
half_full_round = int(full_round / 2)
def string_to_field_elements(s: str, p: int, max_bytes_per_elem=8):
    # Convert string to bytes
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    b = s.encode('utf-8')

    # Split into chunks
    chunks = [b[i:i+max_bytes_per_elem] for i in range(0, len(b), max_bytes_per_elem)]

    # Convert each chunk to an integer mod p
    field_elements = [int.from_bytes(chunk, 'little') % p for chunk in chunks]
    return field_elements

# Field operations
def fpow(x, e): return cp.power(x, e, dtype=cp.uint64) % p
def sbox(x): return fpow(x, alpha)  # x^alpha mod p

# Convert hex strings to integers (removes '0x' prefix automatically)
matrix_64_int = [[int(x, 16) % p for x in row] for row in parameters.matrix_64]
MDS = cp.array(matrix_64_int, dtype=cp.uint64)

rc_64_int = [int(x, 16) % p for x in parameters.round_constants_64]
RC = cp.array(rc_64_int, dtype=cp.uint64)

state = cp.zeros(t, dtype=cp.uint64)  # State vector with t elements

def full_rounds(rc_counter, state):
    for r in range(0, half_full_round):
        # add round constants, apply s-box
        for i in range(0, t):
            state[i] = state[i] + RC[rc_counter]
            rc_counter += 1

            state[i] = sbox(state[i])

        # apply MDS matrix
        state = MDS @ state
        state = state % p  # Ensure state remains in field
    return rc_counter, state

def partial_rounds(rc_counter, state):
    for r in range(0, partial_round):
        # add round constants, apply s-box
        for i in range(0, t):
            state[i] = state[i] + RC[rc_counter]
            rc_counter += 1

        state[i] = sbox(state[i])

        # apply MDS matrix
        state = MDS @ state
        state = state % p  # Ensure state remains in field
    return rc_counter, state

# Main Poseidon hash function
def run_hash(data: str):
    """

    :param input_vec:
    :return:
    """
    input_vec = string_to_field_elements(data, parameters.prime_64)
    if len(input_vec) < t:
        input_vec.extend([0] * (t - len(input_vec)))
    state = cp.array(input_vec, dtype=cp.uint64)
    state = state % p  # Ensure input is in field
    rc_counter = 0

    # First full rounds
    rc_counter, state = full_rounds(rc_counter, state)

    # Middle partial rounds
    rc_counter, state = partial_rounds(rc_counter, state)

    # Last full rounds
    rc_counter, state = full_rounds(rc_counter, state)
    value = state[1].item()
    return str(value)

data = "Hello, Poseidon on GPU!"
output = run_hash(data)
print("Poseidon GPU digest:", output)
