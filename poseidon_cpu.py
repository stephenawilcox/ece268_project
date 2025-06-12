import sys
sys.path.append("external/poseidon-hash")
from poseidon import Poseidon, parameters

def string_to_field_elements(s: str, p: int, max_bytes_per_elem=8):
    # Convert string to bytes
    b = s.encode('utf-8')

    # Split into chunks
    chunks = [b[i:i+max_bytes_per_elem] for i in range(0, len(b), max_bytes_per_elem)]

    # Convert each chunk to an integer mod p
    field_elements = [int.from_bytes(chunk, 'little') % p for chunk in chunks]
    return field_elements

def p_encode(data:str) -> str:
    security_level = 128
    input_rate = 8
    t = 9
    full_round = 8
    partial_round = 41
    alpha = 3
    poseidon_new = Poseidon(parameters.prime_64, security_level, alpha, input_rate, t, full_round=full_round,
                        partial_round=partial_round, rc_list=parameters.round_constants_64, mds_matrix=parameters.matrix_64)

    input_vec = string_to_field_elements(data, parameters.prime_64)

    #print("Input: ", input_vec)
    poseidon_output = poseidon_new.run_hash(input_vec)
    #print("Output: ", hex(int(poseidon_output)))
    return hex(int(poseidon_output))[2:]