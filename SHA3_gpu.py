import numpy as np
import cupy as cp


def SHA3_hash_gpu(msg, b=1600, c=512, d=256):
    return 0

def main():
    hash = SHA3_hash_gpu("abc")
    print(hash.hex().upper())
    
    

if __name__ == "__main__":
    main()