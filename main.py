from typing import List
from merkletree import Merkle_Tree, hash_data
from time import time


def main():
    data_blocks:List[str] = []
    num_elements = 16
    for i in range(num_elements):
        data_blocks.append("element" + str(i))

    hash_func1 = "SHA3"
    hash_func2 = "POSEIDON"

    start_time = time()
    cpu_tree = Merkle_Tree(data_blocks, hash_func1)
    elapsed_time1 = time() - start_time

    # cpu_tree.print_tree()

    target = hash_data("element0", hash_func1)
    proof = cpu_tree.get_proof(target)
    # print(f"Proof for {target}: {proof}")

    is_valid = Merkle_Tree.verify_proof(target, proof, cpu_tree.root.hash, hash_func1)
    print(f"TIME: {elapsed_time1}, HASH FUNC: {hash_func1}, VALID: {is_valid}")







    start_time = time()
    cpu_tree = Merkle_Tree(data_blocks, hash_func2)
    elapsed_time2 = time() - start_time

    # cpu_tree.print_tree()

    target = hash_data("element0", hash_func2)
    proof = cpu_tree.get_proof(target)
    # print(f"Proof for {target}: {proof}")

    is_valid = Merkle_Tree.verify_proof(target, proof, cpu_tree.root.hash, hash_func2)
    print(f" TIME: {elapsed_time2}, HASH FUNC: {hash_func2}, VALID: {is_valid}")



if __name__ == "__main__":
    main()