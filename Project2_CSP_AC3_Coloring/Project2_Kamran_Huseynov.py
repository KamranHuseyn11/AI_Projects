

# In[7]:


import heapq
import copy
from collections import deque
import time


# In[8]:


# INITIALIZING ALL STRUCTURES NEEDED 

def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


def read_input_file(path_to_file,max_lines):
    nodes = []
    adj = []
    num_colors = 0
    iterate = 0
    my_input = open(path_to_file,'r',encoding='utf-8')
    for line in nonblank_lines(my_input):
        iterate += 1
        if line[0] in ('#','@'): #ignore lines that start with # and empty lines
            continue
        elif line[0].lower() == 'c': # colors = int starts with c
            num_colors = int(line.split('=')[-1].rstrip())
        else: 
            node1, node2 = int(line.split(',')[0].rstrip()), int(line.split(',')[1].rstrip())
            nodes.append(node1)
            nodes.append(node2)
            adj.append([node1,node2]) #list of adjacent nodes
        if iterate == max_lines:
            break
    my_input.close()
    return nodes,adj,num_colors

def init_domains(X,D):
    # initializing our domains, using dictionary of lists, each node will have all colors in the domain when we initialize
    dic = {}
    for i in X:
        dic[i] = copy.copy(D)
    return dic

def init_neighbors(X,adj):
    dic = {}
    for i in X:
        dic[i] = [] #initializing empty list for each node
    
    for j in adj:
        # edges are undirected so we will add nodes to each other's list in neighbors dictionary
        dic[j[0]].append(j[1]) 
        dic[j[1]].append(j[0])
    return dic


def init_node_map(X):
    dic = {} 
    for i in X:
        dic[i] = 0
    return dic

# we initially appended all nodes in input file, most of them are appended more than once, this line gets set of unique nodes and then 
# turns it to a list of variables(nodes) 
def initialize(path_to_file,max_lines):
    color_pool = ['red','green','blue','yellow','black','white','orange','brown',"silver","darkblue","lightblue","pink","violet","purple"] 
    my_nodes,my_adj,my_num_colors = read_input_file(path_to_file,max_lines)
    X = list(set(my_nodes))   
    color_D = color_pool[:my_num_colors] #getting domain of colors we need according to number of colors
    D = init_domains(X,color_D) # domains will be a dictionary of explicit colors that each node can use, gets updated after each step 
    Mapping = init_node_map(X)
    neighbors = init_neighbors(X,my_adj) # another dicitonary will be used to store neighbors for all nodes, will be used for checking constraints,AC3 etc.
    return X,D,neighbors,Mapping


# END OF FUNCTIONS FOR INITIALIZING


# In[9]:


# SOME HELPER FUNCTIONS FOR BACKTRACKING


# WE CHECK IF WE CAN ASSIGN COLOR TO NEW VERTEX, return False if there is already a neighbor with same color
def no_Collision(node_to_color_map,check_color,vertex,neighbors): 
    
    for neighbor_node in neighbors[vertex]:
        if check_color == node_to_color_map[neighbor_node]:
            return False
    
    return True



# You can use this function to make sure the result is consistent with constraints. not used in program overall 
def double_check(variables,node_to_color_map):
    flag = True
    for v in variables:
        for ne in neighbors[v]:
            if node_to_color_map[v] in (node_to_color_map[ne],0):
                flag = False
                print("false")
    if flag:
        print("true")
    return flag


# In[10]:


# FUNCTIONS for HEURISTICS


# We select next vertex by minimum remaning values
def select_node_by_MRV(variables,domains,node_to_color_map):
    Min = 10000
    select_vertex = -1
    
    for temp in variables:
        if len(domains[temp]) < Min and node_to_color_map[temp] == 0:
            Min = len(domains[temp])
            select_vertex = temp
    return select_vertex


# We select color for the selected vertex by least constraining value
def select_color_by_LCV(vertex,neighbors,domains):
    min_to_max_lcv_colors = []
    
    
    for color in domains[vertex]:
        value = 0
        for neighbor_node in neighbors[vertex]:
            if color in domains[neighbor_node]:
                value = value + 1

        heapq.heappush(min_to_max_lcv_colors,(value,color))
    return min_to_max_lcv_colors

# END OF HEURISTICS FUNCTIONS


# In[14]:


# AC3 FUNCTIONS


# each time we select new vertex,and color, we initiate queue for arc
def initiate_new_constraints(vertex,neighbors,node_to_color_map):
    arcs = deque([])

    for neighbor in neighbors[vertex]:
        if node_to_color_map[neighbor] == 0:
            arcs.append([neighbor,vertex])
    return arcs


# AC3 function, 1st value to return says if our graph is arc consistent, 2nd one returns new domains for vertices
def AC3(constraints_queue,new_domains,neighbors,node_to_color_map):
    while len(constraints_queue) != 0:
        current_arc = constraints_queue.popleft()
        arc_updated, new_domains = Compare_remove_values(current_arc,new_domains)
        
        if arc_updated:
            if len(new_domains[current_arc[0]]) ==0:
                return False,new_domains
            
            for neighbor in neigbors[current_arc[0]]:
                if node_to_color_map[neighbor] == 0 and neighbor != current_arc[1]:
                    constraints_queue.append([neighbor,current_arc[0]])
                    
    return True,new_domains


# function, takes new two neighbor vertices and deletes inconsistent values. if something is removed 1st value is True
# 2nd value updates domain of the vertex given in argument.
def Compare_remove_values(current_arc,new_domains):
    arc_is_updated = False
    if len(new_domains[current_arc[1]]) ==1:
        color_to_remove = new_domains[current_arc[1]][0]
        
        if color_to_remove in new_domains[current_arc[0]]:
            new_domain[current_arc[0]].remove(color_to_remove)
            arc_is_updated = True
        
    return (arc_is_updated,new_domains)
            
    
    


# In[12]:


# MAIN functions

# Backtracking, recursive function to find solution
def backtracking(num_assignments,variables,domains,neighbors,node_to_color_map):
    
    if num_assignments == len(variables):
           return True
    
    vertex = select_node_by_MRV(variables,domains,node_to_color_map)
    vertex_color_order = select_color_by_LCV(vertex,neighbors,domains)
    
    for iteration in domains[vertex]:
        check_color = heapq.heappop(vertex_color_order)[1]
        new_domains = copy.copy(domains)
        
        if no_Collision(node_to_color_map,check_color,vertex,neighbors):
            new_domains[vertex] = check_color

            constraints_queue = initiate_new_constraints(vertex,neighbors,node_to_color_map)
            
            is_consistent,domain_update = AC3(constraints_queue,new_domains,neighbors,node_to_color_map)
            
            if is_consistent:
                node_to_color_map[vertex] = check_color
                new_domain = copy.copy(domain_update)
                num_assignments = num_assignments + 1
            
            
                if backtracking(num_assignments,variables,domains,neighbors,node_to_color_map):
                    return True
                
            num_assignments = num_assignments - 1
            node_to_color_map[vertex] = 0


# one function above backtracking, we will run this function to print solution       
def CSP(path_to_file,read_max_lines = 1000):
    
    variables,domains,neighbors,node_to_color_map = initialize(path_to_file,read_max_lines)

    num_assignments = 0
    domains[1].pop(0)
    
    if backtracking(num_assignments,variables,domains,neighbors,node_to_color_map) == None:
        print("No Solution!")
        return False
    
    print("Result:\n")
    for vertex_number in variables:
        print(f"Vertex: {vertex_number} Color: {node_to_color_map[vertex_number]}")
        
    print("\n\n number of vertices: ", len(variables))
    return True


# In[ ]:





# In[20]:




path_to_file = input("Insert path to input file: ")

start = time.time()

CSP(path_to_file)

end = time.time()

print("\n runtime: ", end-start )


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




