"""
    Implementation of SHA3-256-Keccak. For full documentation,
    https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf
"""
import math
import numpy as np
from bitarray import bitarray

#  Constants
rotation_offsets = [
    [ 0, 36,  3, 41, 18],
    [ 1, 44, 10, 45,  2],
    [62,  6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39,  8, 14],
]

round_constants = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
]


# DATA PROCESSING


def bitsToStateArray(bits, w):
    """
    This function takes in an input string and outputs the form of it in bits.

    INPUTS:

    bits - the input bit array

    w - The number of layers. w is 64 for b=1600

    OUTPUTS: 

    state_array - input bits arranged in the form of a 5x5xw state array

    """
    state_array = np.zeros((5, 5, w), dtype=int)

    # Map the flat bits into the state array
    for x in range(5):
        for y in range(5):
            for z in range(w):
                index = w * (5*y + x) + z
                state_array[x, y, z] = bits[index]
    
    return state_array

def stateArrayToBits(state_array, w):
    """
    This function takes in a state array as input and forms it into  a bit array

    INPUTS:

    state - the state array

    OUTPUTS: 

    bits - a bit string concatenation of all elements of the state_array

    """
    bits = bitarray()

    # Flatten the state array into a 1D bitarray
    for y in range(5):
        for x in range(5):
            for z in range(w):
                bits.append(state_array[x, y, z])
    return bits


# ROUND FUNCTIONS 
"""
The round functions are a series of functions that must be done sequentially to get the correct output. For more information on what each function does specifically, see the pdf linked at the top. Each function will take in a state array that holds the current state, as well as the depth of each lane (w) (aka the number of layers). 
"""
def theta(state_array, w):
    C = np.zeros((5, w), dtype=int)
    D = np.zeros((5, w), dtype=int)
    for x in range(5):
        for z in range(w):
            C[x, z] = state_array[x, 0, z] ^ state_array[x, 1, z] ^ state_array[x, 2, z] ^ state_array[x, 3, z] ^ state_array[x, 4, z]

    for x in range(5):
        for z in range(w):
            D[x, z] = C[(x - 1) % 5, z] ^ C[(x + 1) % 5, (z - 1) % w]

    new_state_array = np.zeros_like(state_array)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                new_state_array[x, y, z] = state_array[x, y, z] ^ D[x, z]

    return new_state_array 

def rho(state_array, w):
    new_state_array = np.zeros_like(state_array)
    for z in range(w):
        new_state_array[0, 0, z] = state_array[0, 0, z]
    for x in range(5):
        for y in range(5):
            if (x == 0 and y == 0):  
                continue 
            rotation_offset = rotation_offsets[x][y]
            for z in range(w):
                new_state_array[x, y, z] = state_array[x, y, (z - rotation_offset) % w]
    return new_state_array


def pi(state_array, w):
    new_state_array = np.zeros_like(state_array)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                new_state_array[x, y, z] = state_array[(x + 3*y) % 5, x, z]
    return new_state_array

def chi(state_array, w):
    new_state_array = np.zeros_like(state_array)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                new_state_array[x, y, z] = state_array[x, y, z] ^ ((state_array[(x + 1) % 5, y, z] ^ 1) & state_array[(x + 2) % 5, y, z])
    return new_state_array


def iota(state_array, w, l, i_r):
    new_state_array = state_array.copy()
    RC = round_constants[i_r]
    RC_new = [ ((RC >> z) & 1) for z in range(w) ]
    
    for z in range(w):
        new_state_array[0, 0, z] = new_state_array[0, 0, z] ^ RC_new[z]
    return new_state_array


def round(state_array, w, l, i_r):
    after_theta = theta(state_array, w)
    after_rho = rho(after_theta, w)
    after_pi = pi(after_rho, w)
    after_chi = chi(after_pi, w)
    after_iota = iota(after_chi, w, l, i_r)
    return after_iota


def Keccak_p(input, b, n_r=24):
    """
    This function performs the Keccak_p algorithm, which is needed as input for the sponge function.

    INPUTS:

    input - bitarray of length b (the length of the original string)

    b - permutation width. For standard implementations of SHA3-256, this is 1600

    n_r - number of rounds to go through for the round function, default to 24 rounds for Keccak[c]

    OUTPUTS:

    s - output string of length b
    """

    w = b // 25
    l = int(math.log2(w))
    state_array = bitsToStateArray(input, w)
    for i_r in range(n_r):
        state_array = round(state_array, w, l, i_r)
    s = stateArrayToBits(state_array, w)
    return s


def pad10(x, m):
    """
    This function creates the padding needed for the sponge function.

    INPUTS:
    x - positive integer x,

    m - non-negative integer m

    OUTPUTS:
    pad - padding used for sponge function
    """

    j = (-m - 2) % x 
    zeros = bitarray(j)
    zeros.setall(0)
    one = bitarray('1')
    pad = one + zeros + one
    return pad



def truncate(r, S):
    """
    This function truncates a bitstring S up to the r-1th bit

    INPUTS:
    r - The bit to truncate up to
    S - the input bit string

    OUTPUT:
    S[0:r] - the truncated version of the input up to bit r-1
    """
    return S[0:r]

def sponge(N, b, c, d):
    """
    This function computes the sponge function. It is specified by a function f (Keccak-p), a padding (pad-10), and a constant c (inputted from calling Keccak_c)

    INPUTS:

    N - the original message given as a bit array

    b - permutation width. For standard implementations of SHA3-256, this is 1600

    c - capacity such that r + c = b (where r is some positive integer, and b is the bit length used in the algorithm). For SHA3-256, the value c is 512. c can also be calculated as c = b - r(where r is some positive integer, and b is the bit length used in the algorithm). For SHA3-256, the value c is 512.

    d - output length of the hash. For SHA3-256, the value of d is 256 (real input)

    OUTPUTS:

    z - output string z such that len(z) = d
    
    """
    r = b - c
    P = N.copy()
    P.extend(pad10(r, len(P)))
    n = int(len(P)/r) 
    
    # Step 5
    S = bitarray(b)
    S.setall(0)
    zeros_c = bitarray(c)
    zeros_c.setall(0)
    # Step 6
    for i in range(n):
        # Pi || 0^c
        intermediate = bitarray()
        intermediate.extend(P[i*r:i*r + r])
        intermediate.extend(zeros_c)
        # Input to keccak
        keccak_p_input = S ^ intermediate
        S = Keccak_p(keccak_p_input, b)
    # Step 7
    Z = truncate(r, S)         # Z now is exactly r bits
    return Z[:d]


def Keccak_c(msg, b, c, d):
    """
    This function computes Keccak[c] for some bit msg.

    INPUTS:
    msg - The given bit message for Keccak[c]. 
    
    b - permutation width. For standard implementations of SHA3-256, this is 1600

    c - capacity (i.e. double the digest length). c can also be calculated as c = b - r(where r is some positive integer, and b is the bit length used in the algorithm). For SHA3-256, the value c is 512.

    d - output length of the hash. For SHA3-256, the value of d is 256

    OUTPUTS:

    result - the result for the given input for Keccak[c] in bits

    """
    result = sponge(msg, b, c, d)
    return result




def SHA3_hash(msg, b=1600, c=512, d=256):
    """
    This function computes the SHA3-Keccak version of a message. 

    INPUTS:
    msg - the original message given as a string

    b - permutation width. For standard implementations of SHA3-256, this is 1600

    c - capacity such that r + c = b (where r is some positive integer, and b is the bit length used in the algorithm). For SHA3-256, the value c is 512. c can also be calculated as c = b - r(where r is some positive integer, and b is the bit length used in the algorithm). For SHA3-256, the value c is 512.

    d - output length of the hash. For SHA3-256, the value of d is 256

    OUTPUT:

    hash - the final hash of the message given in bits
    """
    # Convert to bits
    msg_bits = bitarray(endian='little')
    msg_bits.frombytes(msg.encode('ascii'))
    msg_bits = msg_bits + bitarray('01')
    # Begin Hash
    hash = Keccak_c(msg_bits, b, c, d)
    return hash



# DEBUG
def print_state(state):
    """
        This function is used to see the state of the 3D state array whenever called.

        INPUTS:

        state - The current state array
    """
    for i, layer in enumerate(state):  # Enumerate layers
        print(f"Layer {i}:\n{layer}")

"""
Function to ensure that little endian is used when reading out bitarray
"""
def bits_to_little_endian_bytes(bits: bitarray) -> bytes:
    n = len(bits)
    if n % 8 != 0:
        raise ValueError("Length of bits must be a multiple of 8")
    out = bytearray(n // 8)
    for i in range(0, n, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= (bits[i + j] << j)
        out[i // 8] = byte_val
    return bytes(out)

def main():
    raw_bits = SHA3_hash("abc")
    digest_bytes = bits_to_little_endian_bytes(raw_bits)
    print(digest_bytes.hex().upper())
    
    

if __name__ == "__main__":
    main()