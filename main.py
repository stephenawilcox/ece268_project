from typing import List
from merkletree import Merkle_Tree, hash_data
from time import time


def main():
    data_blocks:List[str] = []
    num_elements = 4
    for i in range(num_elements):
        data_blocks.append("element" + str(i))

    hash_func = "SHA256"

    start_time = time()
    cpu_tree = Merkle_Tree(data_blocks, hash_func)
    elapsed_time = time() - start_time

    print(f"Time: {elapsed_time}")
    cpu_tree.print_tree()

    target = hash_data("element0", hash_func)
    proof = cpu_tree.get_proof(target)
    print(f"Proof for {target}: {proof}")

    is_valid = Merkle_Tree.verify_proof(target, proof, cpu_tree.root.hash, hash_func)
    print(f"Is proof valid? {is_valid}")


if __name__ == "__main__":
    main()