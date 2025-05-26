from typing import List
from merkletree import Merkle_Tree
from time import time


def main():
    data_blocks:List[str] = []
    num_elements = 5
    for i in range(num_elements):
        data_blocks.append("element" + str(i))

    hash_func = "SHA256"

    start_time = time()
    cpu_tree = Merkle_Tree(data_blocks, hash_func)
    elapsed_time = time() - start_time

    print(f"Time: {elapsed_time}")
    cpu_tree.print_tree()


if __name__ == "__main__":
    main()