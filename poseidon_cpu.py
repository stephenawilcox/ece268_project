import sys
sys.path.append("external/poseidon-hash")
from poseidon import Poseidon, parameters

def main():
    security_level = 128
    input_rate = 3
    t = 4
    alpha = 5
    poseidon_new = Poseidon(parameters.prime_64, security_level, alpha, input_rate, t)

    input_vec = [x for x in range(0, t)]
    print("Input: ", input_vec)
    poseidon_output = poseidon_new.run_hash(input_vec)
    print("Output: ", hex(int(poseidon_output)))


if __name__ == "__main__":
    main()