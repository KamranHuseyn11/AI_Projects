#!/usr/bin/env python
# coding: utf-8

# In[1]:


import heapq
import time
from math import sqrt


# In[2]:


#defining and initiliaztingvisited array to check wheter the node is explored, if index correlating to the node is 0
#then it is not visited. if 1 it is visited. this way it is much faster to check explored nodes,
#instead of scanning through visited nodes each time

#we use heapq function to manipulate frontier(fringe) as priority queue, and neighbors_dict 
# that respresents graph. each time we explore new node we will add its neighbors to frontier.

# route represents path for UCS algorithm. 


# In[3]:


#I think in the exercise description you meant that each square is 1000*1000 size. Anyway you can change square_size to 100 or 10 if you wish to
# to make heuristic admissible we will assume that nodes in adjacent squares can be as close as 1 unit length to each-other
# for instance, node in 76 and node in 79 will have 2 squares (78 77) there fore we will approximate the eucludian distance considering
# the cases where nodes can be in the closest part of their square to each-other. 

def calculate_heuristics(file_name,Dest,n,size_square):
    
    heur = []
    cord = []
    
    
    for i in range(n):
        cord.append(0)
    
    #reading vertex file
    file = open(file_name,'r',encoding="utf-8")
   
    # getting cordinates from positions, if node is in 72nd square then it is 72//10 = 7th row amd 72%10 = 2nd column
    for line in file.readlines():
        if line[0] not in ("#",'\\',' '):
            v,coordinate = line.split(",")
            v,coordinate = int(v),int(coordinate)
            cord_x = coordinate%10
            cord_y = coordinate//10
            cord[v] = [cord_x,cord_y]
            

    
# calculating heuristic for each node. dif_x is horizontal distance between nodes, dif_y is vertical. 
    for i in range(n):
        dif_x = (abs(cord[i][0] - cord[Dest][0])) -1
        dif_y = (abs(cord[i][1] - cord[Dest][1])) -1
       
    # if destination node, heuristic = 0
        if i == Dest:
            estimate_eucludian = 0
    
    # if the nodes are adjacent    
        elif cord[i][0] == cord[Dest][0] and cord[i][1] == cord[Dest][1]:
            estimate_eucludian = 1
    
    # if nodes are in same column        
        elif cord[i][0] == cord[Dest][0] and cord[i][1] != cord[Dest][1]:
            estimate_eucludian = dif_y *size_square + 1
    
    # if nodes are in same row
        elif cord[i][0] != cord[Dest][0] and cord[i][1] == cord[Dest][1]:
            estimate_eucludian = dif_x *size_square + 1
    
    # all other cases different column and row    
        else:
            estimate_eucludian = sqrt(dif_x**2 + dif_y**2)*size_square + 1 

        heur.append(estimate_eucludian)
    return heur


# In[4]:



def read_source_and_destination_nodes(file_name):
    # we read source and destination nodes from source and destination file sd.txt
    file = open(file_name,'r',encoding="utf-8")
    for line in file.readlines():
        if line[0].lower() == "s":
            Source = int(line.split(',')[1]) 
        elif line[0].lower() == "d":
            Destination = int(line.split(',')[1]) 
    return Source,Destination


def init_graph(n):
    # initializing our graph with empty lists, using dictionary of lists
    graph = {}
    for i in range(n):
        graph[i] = []
    return graph



def find_path(path,parent,D,S):
    # recursive method to retrieve path, path variable is going to be non-local so no need to return anything
    path.append(parent[D])
    if parent[D] != S:
        find_path(path,parent,parent[D],S)
        


def generate_graph(file_name_e,heuristic,num_nodes):
    
    my_graph = init_graph(n=num_nodes)
    
    # reading edge_file e.txt
    file = open(file_name_e,'r',encoding="utf-8")
    
    for line in file.readlines():
        if line[0] not in ("#",'\\',' '):
            v1,v2,cost = line.split(",")
            v1,v2,cost = int(v1),int(v2),int(cost)
    
    # this is the structure of our graph, first entry will be used for priority queue, 2nd entry in list is index of all adjacent nodes to the key node.
    # 3rd is used for calculating overall cost
            my_graph[v1].append([cost+heuristic[v2],v2,cost])
            my_graph[v2].append([cost+heuristic[v1],v1,cost])
            
            
            
    return my_graph


# In[17]:


def run_search(vertex_file='v.txt', edge_file='e.txt',source_des_file = 'sd.txt', square_size=1000, num_nodes=100, algo='A_star'):
    
    # for calculating run time of the algorithm
    start_time = time.time()    
    
    S,D = read_source_and_destination_nodes(source_des_file)
    
    if algo.lower() == 'a_star':
        heuristic = calculate_heuristics(vertex_file,Dest=D,n=num_nodes,size_square=square_size)
    elif algo.lower() == 'ucs':
        heuristic = []
        for i in range(num_nodes):
            heuristic.append(0)
    else:
        print('Algorithm Not Found! Please, use either UCS or A_star as an input!')
    
    # we will use neighbors dict to store graph
    neighbors_dict = generate_graph(edge_file,heuristic,num_nodes)
    
    #parents dictionary is used for mapping the node to its parent, we will then recursively find the shortest path when algorithm explores the destination node
    parents = {}
    cost = 0
    
    # fronties is fringe, and it simulates priority queue with the help of heapq module
    frontier = []
    
    # vistited[explored node] = 1 , else = 0
    visited = []
    
    # we initialize our path with a list which has destionation node as the first entry
    path = [D]
    
    # to store the order in which the nodes are explored
    full_route = []
    
    # at start no node is visited, all values in the list is 0 
    for i in range(num_nodes):
        visited.append(0)
    
    # we start by pushing Source node to out priority queue (frontier), cost is 0 and value of heuristic dont matter at this point
    heapq.heappush(frontier, (cost, [S,cost,S]))
    
            
    while len(frontier) != 0:
        # each time we take a node from frontier with lowest cost+heuritic
        current_score,[current_node,current_cost,parent_node] = heapq.heappop(frontier)
        
        # if visited = 0 we explore the node, update parent,route,and visited
        if visited[current_node] == 0:
            full_route.append(current_node)
            visited[current_node] = 1
            parents[current_node] = parent_node
            
            # if explored node is the destination node, we output and then end the program
            if current_node == D:
                print(f"\nreached destination!\n\n cost = {current_cost}\n\nnumber of nodes explored: {len(full_route)}\nexplortion order is as follows:")
                    
                print(full_route)
                    
                print('\n\n Path is as follows:')
                
                # find the shortest path with recursion
                find_path(path,parents,D,S)
                    
                for i in range(len(path)-1,0,-1):
                    print(path[i], end=' >> ')
                print(path[0])        
                
                end_time = time.time()
                print(f"\n\noverall execution time for {algo.upper() } algorithm is {end_time-start_time} seconds")
                
                return
            else:
                
                # if explored node is not the destination node, we proceed by adding the adjacent nodes to the frontier
                for node in neighbors_dict[current_node]:
                    heapq.heappush(frontier, (node[0] + current_cost, [node[1],node[2]+current_cost,current_node]))
    
    # if there is no node left in frontier and destination node is not reached. then there is no path from source to destionation
    print(f"There is no path to destination!! job failed!")
        
    end_time = time.time()
    print(f"\n\noverall execution time for {algo.upper() } algorithm is {end_time-start_time} seconds")
    


# In[20]:


my_size = 1000




#we will input algorithm option and if A* is chose the program aditionally will ask for the square_size.

manual = input('Do you wish to input files manually? y/n?  ')

if manual.lower()[0] == 'y':
    my_e = input('path to edge file:  ')
    my_v = input('path to vertex file:  ')
    my_sd = input('path to source/destination file:  ')
else:
    my_v = 'v.txt'
    my_e = 'e.txt'
    my_sd = 'sd.txt'

my_algo = input("\nPlease, input the algorithm: A_star/UCS?  ")

if my_algo.lower() == 'a_star':
     my_size = int(input("\nPlease, input the size of each square: 10/100/1000?  "))
print("\n\n")


run_search(algo=my_algo,square_size=my_size)
print("\nEnd of program.")


# In[12]:


a = 'sadsdad'
a.upper()


# In[ ]:




