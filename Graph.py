import Node

class Graph(object):
    def __init__(self, words, nodes, d):
        self.words = words
        self.nodes = nodes
        self.d = d
   
                    
    def calculatePageRank(self, d):   
        for node in self.nodes:
            node.previous_pr = 1.0/len(self.nodes) #initialize equal start weights which sum up to 1
        min_change_val = 0.01
        min_change = True #chechs after each iteration if a minimum change happend in the algorithm
        div = 1.0/len(self.nodes)
        while min_change == True: #from here the iterations begin
            min_change = False
            for node in self.nodes: #begin to fill node weights with damping partition
                node.page_rank = (1-d)*div
            for node in self.nodes:
                cnt_neighbours = len(node.neighbours)
                for neighbour in node.neighbours: #let weight flow from each node to its neighbours
                    neighbour.page_rank += d*node.previous_pr/cnt_neighbours
            for node in self.nodes: #check min_difference to previous iteration
                if abs(node.previous_pr-node.page_rank)>min_change_val:
                    min_change = True
                    break
            for node in self.nodes: #declare weights as old weights
                node.previous_pr = node.page_rank
            
            
    def calculateKPP(self): #key player problem, not normalized. the information for betweenness can be extracted almost identically, so the basic informations for betweenness are gathered in here, too. the lines where this happens are marked
        for node in self.nodes: #create a bft for each node
            kpp_value = 0.0
            node_list = self.nodes[:] #this is used to check if we have seen a node before
            node_list.remove(node)
            for element in node.neighbours:
                node_list.remove(element)
                element.tree_dictionary[node] = [[node], 1] #part1 for betweenness. stores the shortest path information to each node in a dictionary
            queue = node.neighbours #the queue contains all nodes in a certain distance. in fact, it is not exactly used like a queue                
            depth = 0 #this is the distance to the start node
            while len(queue)>0:
                depth +=1
                neighbours_list = []
                for element in queue: #for each element in the queue look for neighbours and put them in the neighbours_list. then the neighbours_list becomes the new queue
                    kpp_value += 1.0/depth
                    for el in element.neighbours:
                        if el in node_list:
                            node_list.remove(el)
                            neighbours_list.append(el)
                            el.tree_dictionary[node] = [[element], depth+1] #part2 for betweenness
                        else: #part3 for betweenness
                            if el.tree_dictionary[node][1]==depth+1: #check if we have a new shortest path here
                                temp_list = el.tree_dictionary[node]
                                temp_list[0].append(element)
                                el.tree_dictionary[node] = temp_list #new node is added to nodes contained in shortest paths
                queue = neighbours_list
            node.kpp = kpp_value
            
                            
    def calculateBetweenness(self): #not normalized
        node_zero = self.nodes[1]
        for node in self.nodes: #find all shortest paths from node to node
            for key in node.tree_dictionary.keys():
                visited = []
                queue = [node]
                for i in range(node.tree_dictionary[key][1]-1):
                    queue_betweenness_sum = 0
                    for queue_node in queue:
                        for next_node in queue_node.tree_dictionary[key][0]:
                            queue_betweenness_sum += queue_node.betweenness_relevance
                            if next_node in visited:
                                next_node.betweenness_relevance += queue_node.betweenness_relevance
                            else:
                                visited.append(next_node)                                
                                next_node.betweenness_relevance = queue_node.betweenness_relevance
                    for visited_node in visited:
                        visited_node.betweenness += float(visited_node.betweenness_relevance)/queue_betweenness_sum                        
                    queue = visited
                    visited = []
                
    def calculateMaximumFlow(self):
        for node in self.nodes:
            node.initialize_residual_graph()
        self.temp_nodes = self.nodes[:]
        while len(self.temp_nodes)>0:
            node1 = self.temp_nodes.pop()
            nodes2 = self.temp_nodes[:]
            for node2 in nodes2:
                #print node1.name, node2.name
                found_path = True
                while found_path == True:
                    result_list = self.createResidualGraph(node1, node2)
                    #result_list = output of this function: make a breadt first search on the graph and return a shortest path from node to node2
                    if len(result_list) == 0:
                        found_path = False
                    else:
                        for node_iter in range(len(result_list)-1):
                            node3 = result_list[node_iter]
                            node4 = result_list[node_iter+1]
                            #print node3.name, node4.name
                            node3.residual_graph_neighbours[node4] +=1
                            node4.residual_graph_neighbours[node3] -=1
                        node1.residual_value +=1
                        node2.residual_value +=1
                for nodey in self.nodes: #reset all resdiual values for the next round
                    nodey.reset_residual_values()
        for node in self.nodes:
            print node.name, node.residual_value
            
    def createResidualGraph(self, start_node, end_node):
        queue = [start_node]
        visited = [start_node]
        result = []
        found = False
        while len(queue)>0 and found == False:
            node = queue.pop(0)
            for node2 in node.residual_graph_neighbours.keys():
                if node2 not in visited:
                    if node.residual_graph_neighbours[node2] >= 0:
                        node2.predecessor = node
                        if node2 == end_node:
                            found = True
                            backtrack_node = node2
                            while not backtrack_node == start_node:
                                result.append(backtrack_node)
                                backtrack_node = backtrack_node.predecessor
                            result.append(backtrack_node)
                        else:                           
                            visited.append(node2)
                            queue.append(node2)
        templist = []
        for node in result:
            templist.append(node.name)
        print start_node.name, end_node.name, templist
        return result
                
    
if __name__ == "__main__":
    Node1 = Node.Node("1")    
    Node2 = Node.Node("2")
    Node3 = Node.Node("3")
    Node4 = Node.Node("4")
    Node5 = Node.Node("5")
    Node6 = Node.Node("6")
    Node7 = Node.Node("7")
    Node8 = Node.Node("8")
    Node9 = Node.Node("9")
    Node1.neighbours = [Node2, Node3]
    Node2.neighbours = [Node1, Node4, Node5]
    Node3.neighbours = [Node1, Node6]
    Node4.neighbours = [Node2, Node7]
    Node5.neighbours = [Node2, Node8]
    Node6.neighbours = [Node3, Node7]
    Node7.neighbours = [Node4, Node6, Node9]
    Node8.neighbours = [Node5, Node9]
    Node9.neighbours = [Node7, Node8]
    
    g = Graph(["Fisch"], [Node1, Node2, Node3, Node4, Node5, Node6, Node7, Node8, Node9], 0.8)
    g.calculatePageRank(g.d)
    g.calculateKPP()
    g.calculateBetweenness()
    g.calculateMaximumFlow()
    
        