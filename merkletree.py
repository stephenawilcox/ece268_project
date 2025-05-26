from typing import List
import hashlib      # TEMPORARY, FOR TESTING MERKLE TREE
#from SHA3 import encode
#from poseidon import encode

def hash_data(data:str, hash_func:str):
    if(hash_func == "SHA256"):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    # elif(hash_func == "SHA3"):                                      #FIXME
    #     return hashlib.sha256(data.encode('utf-8')).hexdigest()     #CHANGE LATER
    # elif(hash_func == "POSEIDON"):
    #     return hashlib.sha256(data.encode('utf-8')).hexdigest()     #CHANGE LATER
    else:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
  

class Node:
    def __init__(self, left, right, hash:str, node_data, node_str:str):
        self.left:Node = left
        self.right:Node = right
        self.hash = hash
        self.node_data = node_data
        self.node_str = node_str

    def copy(self):
        return Node(left=self.left, right=self.right, hash=self.hash, node_data=self.node_data, node_str=self.node_str)


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
                               node_str="Node" + str(self.get_counter_val())))
        
        if((len(leaves) % 2) == 1):
            leaves.append(leaves[-1].copy())    #duplicate last element

        return self.recursive_build_tree(leaves)
    
    def recursive_build_tree(self, nodes:List[Node]):
        if((len(nodes) % 2) == 1):
            nodes.append(nodes[-1].copy())      #duplicate last element

        if(len(nodes) == 2):
            return Node(left=nodes[0], 
                        right=nodes[1], 
                        hash=hash_data(nodes[0].hash + nodes[1].hash, self.hash_func), 
                        node_data=(nodes[0].hash, nodes[1].hash), 
                        node_str="Node" + str(self.get_counter_val()))

        half_index = len(nodes) // 2    # early made it so len(nodes) is always even
        new_left:Node = self.recursive_build_tree(nodes[:half_index])
        new_right:Node = self.recursive_build_tree(nodes[half_index:])
        new_hash = hash_data(new_left.hash + new_right.hash, self.hash_func)
        new_node_data = (new_left.hash, new_right.hash)
        new_node_str = "Node" + str(self.get_counter_val())

        return Node(left=new_left, right=new_right, hash=new_hash, node_data=new_node_data, node_str=new_node_str)
    
    def print_tree(self):
        print(f"Root: {self.root.node_str}, left: {self.root.left.node_str}, right: {self.root.right.node_str}, hash: {self.root.hash}, data: {self.root.node_data}")
        self.recursive_print_tree(self.root.left)
        self.recursive_print_tree(self.root.right)
        return
    
    def recursive_print_tree(self, node:Node):
        if(node.left != None and node.right != None):
            print(f"Node: {node.node_str}, left: {node.left.node_str}, right: {node.right.node_str}, hash: {node.hash}, data: {node.node_data}")
            self.recursive_print_tree(node.left)
            self.recursive_print_tree(node.right)
        else:
            print(f"Node: {node.node_str}, left: {node.left}, right: {node.right}, hash: {node.hash}, data: {node.node_data}")
        return