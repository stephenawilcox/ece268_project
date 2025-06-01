import sys
sys.path.append("external/poseidon-hash")
from poseidon import Poseidon, parameters

def string_to_field_elements(s: str, p: int, max_bytes_per_elem=31):
    # Convert string to bytes
    b = s.encode('utf-8')

    # Split into chunks
    chunks = [b[i:i+max_bytes_per_elem] for i in range(0, len(b), max_bytes_per_elem)]

    # Convert each chunk to an integer mod p
    field_elements = [int.from_bytes(chunk, 'little') % p for chunk in chunks]
    return field_elements

def p_encode(data:str) -> str:
    security_level = 128
    input_rate = 3
    t = 4
    alpha = 5
    poseidon_new = Poseidon(parameters.prime_64, security_level, alpha, input_rate, t)

    #input_vec = [x for x in range(0, t)]
    p = 2**64 - 257
    input_vec = string_to_field_elements(data, p)

    print("Input: ", input_vec)
    poseidon_output = poseidon_new.run_hash(input_vec)
    print("Output: ", hex(int(poseidon_output)))
    return hex(int(poseidon_output))[2:]