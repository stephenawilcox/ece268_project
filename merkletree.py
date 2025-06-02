from typing import List
import hashlib      # TEMPORARY, FOR TESTING MERKLE TREE
from SHA3 import SHA3_hash
from poseidon_cpu import p_encode

def hash_data(data:str, hash_func:str):
    if(hash_func == "SHA256"):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif(hash_func == "SHA3"): 
        return SHA3_hash(data).hex()
    # elif(hash_func == "POSEIDON"):
    #     return p_encode(data)
    else:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
  

class Node:
    def __init__(self, left, right, hash:str, node_data, node_str:str, parent):
        self.left:Node = left
        self.right:Node = right
        self.hash = hash
        self.node_data = node_data
        self.node_str = node_str
        self.parent:Node = parent

    def set_parent(self, node):
        self.parent:Node = node

    def copy(self):
        return Node(left=self.left, 
                    right=self.right, 
                    hash=self.hash, 
                    node_data=self.node_data, 
                    node_str=self.node_str,
                    parent=self.parent)


class Merkle_Tree:
    def __init__(self, tree_data:List[str], hash_func:str):
        self.node_counter = 0
        self.hash_func = hash_func
        self.root = self.build_tree(tree_data)

    def get_counter_val(self):
        val = self.node_counter
        self.node_counter = self.node_counter + 1
        return val

    def build_tree(self, tree_data:List[str]):
        leaves:List[Node] = []
        for data in tree_data:
            leaves.append(Node(left=None, 
                               right=None, 
                               hash=hash_data(data, self.hash_func), 
                               node_data=data, 
                               node_str="Node" + str(self.get_counter_val()),
                               parent=None))
        
        if((len(leaves) % 2) == 1):
            leaves.append(leaves[-1].copy())    #duplicate last element

        return self.recursive_build_tree(leaves)
    
    def recursive_build_tree(self, nodes:List[Node]):
        if((len(nodes) % 2) == 1):
            nodes.append(nodes[-1].copy())      #duplicate last element

        if(len(nodes) == 2):
            new_node = Node(left=nodes[0], 
                        right=nodes[1], 
                        hash=hash_data(nodes[0].hash + nodes[1].hash, self.hash_func), 
                        node_data=(nodes[0].hash, nodes[1].hash), 
                        node_str="Node" + str(self.get_counter_val()),
                        parent=None)
            nodes[0].set_parent(new_node)
            nodes[1].set_parent(new_node)
            return new_node

        half_index = len(nodes) // 2    # early made it so len(nodes) is always even
        new_left:Node = self.recursive_build_tree(nodes[:half_index])
        new_right:Node = self.recursive_build_tree(nodes[half_index:])
        new_hash = hash_data(new_left.hash + new_right.hash, self.hash_func)
        new_node_data = (new_left.hash, new_right.hash)
        new_node_str = "Node" + str(self.get_counter_val())

        new_node = Node(left=new_left, right=new_right, hash=new_hash, node_data=new_node_data, node_str=new_node_str, parent=None)
        new_left.set_parent(new_node)
        new_right.set_parent(new_node)
        return new_node
    
    def print_tree(self):
        print(f"Root: {self.root.node_str}, left: {self.root.left.node_str}, right: {self.root.right.node_str}, hash: {self.root.hash}, data: {self.root.node_data}, parent: {None}")
        self.recursive_print_tree(self.root.left)
        self.recursive_print_tree(self.root.right)
        return
    
    def recursive_print_tree(self, node:Node):
        if(node.left != None and node.right != None):
            print(f"Node: {node.node_str}, left: {node.left.node_str}, right: {node.right.node_str}, hash: {node.hash}, data: {node.node_data}, parent: {node.parent.node_str}")
            self.recursive_print_tree(node.left)
            self.recursive_print_tree(node.right)
        else:
            print(f"Node: {node.node_str}, left: {node.left}, right: {node.right}, hash: {node.hash}, data: {node.node_data}, parent: {node.parent.node_str}")
        return
    
    def find_node(self, hash:str, node:Node):
        if(node.hash == hash):
            return node
        else:
            if(node.left != None and node.right != None):
                ln = self.find_node(hash, node.left)
                rn = self.find_node(hash, node.right)
                if(ln != None):
                    return ln
                elif(rn != None):
                    return rn
                else:
                    return None


    def get_proof(self, input_hash:str):
        proof = []
        base_node = self.find_node(input_hash, self.root)
        if(base_node == None):
            return proof
        # print(base_node.node_str)

        cur_node = base_node
        while(cur_node != self.root):
            parent_node = cur_node.parent
            if(cur_node.hash == parent_node.left.hash): # cur node is the left node of parent
                proof.append(("left", parent_node.right.hash))
            elif(cur_node.hash == parent_node.right.hash): # cur node is the right node of parent
                proof.append(("right", parent_node.left.hash))
            cur_node = parent_node

        return proof
    
    @staticmethod
    def verify_proof(input_hash:str, proof:List[tuple], root_hash:str, hash_func:str):
        current_hash = input_hash
        for side, other_hash in proof:
            if side == "left":  # the current hash was on the left side when concat
                current_hash = hash_data(current_hash + other_hash, hash_func)
            elif side == "right": # the current hash was on the right side when concat
                current_hash = hash_data(other_hash + current_hash, hash_func)
        return current_hash == root_hash
    