import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import ast

def Making_graph(initial_resource = 1000000,initial_capacity = 1000):
    m = 2
    initial_graph = nx.barabasi_albert_graph(1000, m,seed=110)
    # Set Initial Node Balances
    
    
    # Set initial balances as node attributes
    for node in initial_graph.nodes():
        initial_graph.nodes[node]['balance'] = initial_resource
   
    bidirectional_graph = nx.DiGraph()
    # Copy nodes from the initial graph
    bidirectional_graph.add_nodes_from(initial_graph.nodes())
    for node in bidirectional_graph.nodes():
        bidirectional_graph.nodes[node]['balance'] = initial_resource
    for u, v in initial_graph.edges():
        bidirectional_graph.add_edge(u, v, weight=initial_capacity)
        bidirectional_graph.add_edge(v, u, weight=initial_capacity)
    for u, v in initial_graph.edges():
        bidirectional_graph[u][v]['fee'] = 0
        bidirectional_graph[v][u]['fee'] = 0
        
    for node in bidirectional_graph.nodes():
        bidirectional_graph.nodes[node]['balance'] = 0
        
    degree_sequence = sorted((d for n, d in bidirectional_graph.degree()), reverse=True)
    dmax = max(degree_sequence)    
    for node in bidirectional_graph.nodes():
        bidirectional_graph.nodes[node]['budget'] = dmax-bidirectional_graph.degree(node)+1
    return bidirectional_graph




def centeralizer_func(graph,s,r):
    g=nx.Graph(graph)
    for node in graph.nodes():
        if g.nodes[node]['budget'] <= 0 and node!=s and node !=r:
            g.remove_node(node)
            graph.nodes[node]['budget']+=1
    return g

def adapt_balance(graph):
    for u, v in graph.edges():
      c1=graph[u][v]["weight"]
      c2=graph[v][u]["weight"]
      C=c1+c2
      #if c1>=c2:
      graph[u][v]['fee'] =((c2*2*0.005)/C)
      graph[v][u]['fee'] =((c1*2*0.005)/C)
      #if c2>c1:
        #graph[v][u]['fee'] =((c2*2*0.005)/C)
        #graph[u][v]['fee'] =((c1*2*0.005)/C)
      #if c1>=(C/2):
        #graph[u][v]['fee'] =((c1*2*0.095)/C)-0.09 # 0.05*transaction
        #graph[v][u]['fee'] =((c2*2*0.05)/C)
      #else:
        #graph[u][v]['fee'] =((c1*2*0.005)/C)
        #graph[v][u]['fee'] =((c2*2*0.095)/C)-0.09 # 0.05*transaction
        
def find_cheapest_spanning_tree(graph, recipient, transaction):
    Q = set(graph.nodes())
    cost = {v: float('inf') for v in graph.nodes()}
    cost[recipient] = 0
    path = {v: None for v in graph.nodes()}
    while Q:
        vi = min(Q, key=lambda v: cost[v])
        Q.remove(vi)

        for vj in graph.neighbors(vi):
            edge = graph[vj][vi]
            if cost[vi] + edge['fee']*transaction+transaction <= graph[vj][vi]["weight"]:
              if cost[vi]+edge['fee']*transaction < cost[vj] :
                cost[vj] = cost[vi] + edge['fee']*transaction
                path[vj] = (vj, vi)

    T = []
    for v in graph.nodes():
        if path[v] is not None:
            T.append(path[v])

    return T


def simulate_payment(graph, sender, recipient, amount,centeralizer = False):   
        adapt_balance(graph)
        if centeralizer ==True:
            g = centeralizer_func(graph,sender,recipient)
            tree = find_cheapest_spanning_tree(g, recipient, amount)
        else:
            tree = find_cheapest_spanning_tree(graph, recipient, amount)
        total_fee = 0
        intermediate_channels = []
        sender_find =False
        for a in tree:
            if sender in a:
                sender_find=True
        if sender_find==False:
            return False , float("NaN") ,[],0 
        else:
            intermediate_nodes= nx.shortest_path(nx.Graph(tree),sender,recipient)
        # Calculate total fee and find intermediate channels in the path
        dmax = max(d for n, d in graph.degree())
        if centeralizer == True:
            for node in graph.nodes():
                if node in intermediate_nodes[1:-1]:
                    graph.nodes[node]['budget']-=1
                elif graph.nodes[node]['budget']< dmax-graph.degree(node)+1:
                    graph.nodes[node]['budget']+=1
                

        mm =graph[intermediate_nodes[0]][intermediate_nodes[1]]['fee']
        graph[intermediate_nodes[0]][intermediate_nodes[1]]['fee']= 0
        for v in range(len(intermediate_nodes)-1):
            total_fee += graph[intermediate_nodes[v]][intermediate_nodes[v+1]]['fee']*amount
            intermediate_channels.append((intermediate_nodes[v], intermediate_nodes[v+1]))
        
        total_amount = amount + total_fee
        y=total_amount
        # Check if all intermediate channels have enough capacity for the transaction
        if all(graph[u][v]['weight'] >= total_amount for u, v in intermediate_channels):
            # Increase capacity for edges inside the ring and decrease for opposite edges
            for u, v in intermediate_channels:
                graph[u][v]['weight'] -= total_amount
                graph[v][u]['weight'] += total_amount
                fee_chan=graph[u][v]['fee']
                graph.nodes[u]['balance']+= fee_chan/2
                graph.nodes[v]['balance']+= fee_chan/2
                total_amount=total_amount- (fee_chan*amount)
            graph[intermediate_nodes[0]][intermediate_nodes[1]]['fee']= mm
            # Update sender and recipient balances
            #graph.nodes[recipient]['balance'] += amount
            #graph.nodes[sender]['balance'] -= total_amount

            return True , y ,intermediate_nodes ,len(intermediate_channels)
        else:
            graph[intermediate_nodes[0]][intermediate_nodes[1]]['fee']= mm
            return False , y,intermediate_nodes,len(intermediate_channels)
    
def graph_balances(G):
    n=0
    for u, v in G.edges():
        if G[u][v]["weight"] <= 10 or G[v][u]["weight"] <= 10 :
            n+=1
    return n

def plotgraph(g,r,amo):
    G = g

    pos =nx.spring_layout(g,seed=110)
    nx.draw(G, pos, with_labels=True, connectionstyle='arc3, rad = 0.05')
    edge_labels = dict([((u, v,), f'{int(d["weight"])} , {"{:.6f}".format(d["fee"])}\n\n{int(G.edges[(v,u)]["weight"])} , {"{:.6f}".format(G.edges[(v,u)]["fee"])}')
                    for u, v, d in G.edges(data=True) if pos[u][0] > pos[v][0]])

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=6)
    plt.show()

    G=nx.DiGraph(find_cheapest_spanning_tree(G,r,amo))
    #pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, connectionstyle='arc3, rad = 0.05')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red',font_size=6)
    plt.show()

def start_simulate(graph,number,suc_pay,unsuc_pay,n=0,tot_amo =[],more_exp=[],routed=[],no_route=[],g=[],centeralizer=False):
    bidirectional_graph=graph
    num_simulations = number
    successful_payments = suc_pay
    unsuccessful_payments=unsuc_pay
    for _ in range(num_simulations):
        nodes = list(bidirectional_graph.nodes())
        sender = random.choice(nodes)
        nodes.remove(sender)
        recipient = random.choice(nodes)
        amount = float(np.random.lognormal(2.95 , 1.2, 1))
        n+=1
        try:
            success , total_amount, node_path , len_path = simulate_payment(bidirectional_graph, sender, recipient, amount,centeralizer)
            tot_amo.append([n,sender,recipient,amount,total_amount,node_path,len_path,success])
            if success:
                successful_payments += 1
                print(f"{n}:Payment from node {sender} to node {recipient} with amount {amount} succeeded.{successful_payments}")
                if total_amount>(0.41+amount):
                    more_exp.append(amount)
                else:
                    routed.append(amount)
            else:
                unsuccessful_payments += 1
                print(f"{n}:Payment from node {sender} to node {recipient} with amount {amount} failed.{unsuccessful_payments}")
                no_route.append(amount)
        except (nx.NetworkXError, nx.NodeNotFound,nx.NetworkXNoPath) as e:
            unsuccessful_payments += 1
            print(f"{n}:Payment error: {e}")
            no_route.append(amount)
        g.append(graph_balances(bidirectional_graph))
        #plotgraph(bidirectional_graph,recipient,amount)

    print(f"Number of successful payments: {successful_payments}")
    print(f"Number of unsuccessful payments: {unsuccessful_payments}")
    return graph,tot_amo,routed,no_route,more_exp,g
def dgree_balance_node(bidirectional_graph,name='dgree_balance'):
    plt.figure(1)
    x_dgree=[]
    y_balance=[]
    for i in bidirectional_graph.nodes():
        y_balance.append(bidirectional_graph.nodes()[int(i)]['balance'])
        x_dgree.append(bidirectional_graph.degree(int(i))/2)
    plt.scatter(x_dgree,y_balance)
    plt.savefig(name +'.png')
    return x_dgree,y_balance


def plot_unbalance(g,name='unbalance'):
    plt.figure(2)
    plt.plot(g)
    plt.savefig(name +'.png')

def plot_payment_hist(routed,no_route,more_exp,name='payment_hist'):
    plt.figure(3)
    x=[]
    y=[]
    z=[]
    for i in no_route:
        x.append(float(i))
    for i in routed:
        y.append(float(i))
    for i in more_exp:
        z.append(float(i))
    label =['no-route','routed','mor expensive']
    colors = ['green', 'red', 'blue']
    
    plt.hist([x,y,z], 40,
            histtype ='bar',
            color = colors,
            label = label,
            log = True)
    
    plt.legend(prop ={'size': 10})
    plt.title('matplotlib.pyplot.hist() function Example\n\n',
            fontweight = "bold")
    plt.savefig(name +'.png')
    
def plot_path_size(tot_amo,name='path_size'):
    plt.figure(4)
    w=[]
    k=[]
    o=[]
    for i in range(len(tot_amo)):
        q=float(tot_amo[i][4]-tot_amo[i][3])
        if q >0.41:
            w.append(tot_amo[i][6])
        else:
            k.append(tot_amo[i][6])
        if tot_amo[i][6] >= 20:
            o.append(tot_amo[i])

    #plt.hist(w,alpha=0.5,log=True,bins=7)
    #plt.hist(k,alpha=0.5,log=True,bins=8)

    label =['routed','more-exp']
    colors = ['red', 'blue']
    
    plt.hist([k,w], 25,
            color = colors,
            label = label,
            log= True)
    plt.savefig(name +'.png')
    
def plot_fee(tot_amo,name='fee_plot'):
    plt.figure(5)
    q=[]
    for i in range(len(tot_amo)):
        q.append(float(tot_amo[i][4]-tot_amo[i][3]))

    #plt.hist(w,alpha=0.5,log=True,bins=7)
    #plt.hist(k,alpha=0.5,log=True,bins=8)

    label =['tot-amo']
    colors = ['red']
    
    plt.hist(q, 100,
            color = colors,
            label = label,
            log= True)
    m=0
    for i in q :
        if i >=0.41:
            m=m+1
    print("number of more expensive:",m)
    plt.savefig(name +'.png')

def save_graph(bidirectional_graph,name="GRAPH"):
    
    for i , v in bidirectional_graph.edges():
        bidirectional_graph[i][v]['weight']=float(bidirectional_graph[i][v]['weight'])
        bidirectional_graph[i][v]['fee']=float(bidirectional_graph[i][v]['fee'])
    nx.write_gml(bidirectional_graph, name+".gml")
    nx.write_gexf(bidirectional_graph, name+".gexf")

def save_data(tot_amo=[] ,more_exp=[] ,routed=[],no_route=[] ,g=[] ,x_dgree=[] ,y_balance=[],name_tot='data_tot',name_list_data='data_list'):
    if tot_amo!=[]:
        df = pd.DataFrame(tot_amo)
        df.transpose().to_csv(name_tot+'.csv')
    if more_exp!=[] or routed!=[] or no_route!=[] or g!=[] or x_dgree!=[] or y_balance!=[]:    
        x=[more_exp,routed,no_route,g,x_dgree,y_balance]
        df = pd.DataFrame(x)
        df.transpose().to_csv(name_list_data+'.csv')
        
def load_graph(file):
    #file="test_true_no_center11.gexf"
    graph=nx.read_gexf(file)
    bidirectional_graph = nx.DiGraph()
    bidirectional_graph.add_nodes_from(graph.nodes())
    #for node in bidirectional_graph.nodes():
    #   bidirectional_graph.nodes[node]['balance'] = initial_resource
    for u, v in graph.edges():
        bidirectional_graph.add_edge(int(u), int(v), weight=graph[str(u)][str(v)]['weight'] )
        bidirectional_graph.add_edge( int(v), int(u), weight=graph[str(v)][str(u)]['weight'] )
    for u, v in graph.edges():    
        bidirectional_graph[int(u)][ int(v)]['fee'] = graph[str(u)][str(v)]['fee']   
        bidirectional_graph[ int(v)][int(u)]['fee'] = graph[str(v)][str(u)]['fee']   

        
    degree_sequence = sorted((d for n, d in graph.degree()), reverse=True)
    dmax = max(degree_sequence)    
    for node in graph.nodes():
        bidirectional_graph.nodes[int(node)]['budget'] = graph.nodes[node]['budget']
        bidirectional_graph.nodes[int(node)]['balance'] = graph.nodes[node]['balance']
    return bidirectional_graph


def convert_str_to_type(value_str):
        try:
            # Try converting to int
            return int(value_str)
        except ValueError:
            try:
                # Try converting to float
                return float(value_str)
            except ValueError:
                try:
                    # Try converting to list using ast.literal_eval
                    return ast.literal_eval(value_str)
                except (SyntaxError, ValueError):
                    # If all attempts fail, return the original string
                    return value_str
                
def load_data(path_name_tot="data_tot.csv",path_name_list_data='data_list.csv'):
    df = pd.read_csv(path_name_tot)

    for column in df.columns:
        df[column] = df[column].apply(convert_str_to_type)
    tot_amo=[]
    for i in df.columns[1:]:
        tot_amo.append(df[i].tolist())
    df2 = pd.read_csv(path_name_list_data)
    import math
    for i in df2.columns[1:]:
        if i =="0":
            more_exp=[x for x in df2[i].tolist() if not math.isnan(x)]
        if i =="1":
            routed=[x for x in df2[i].tolist() if not math.isnan(x)]
        if i =="2":
            no_route=[x for x in df2[i].tolist() if not math.isnan(x)]
        if i =="3":
            g =[x for x in df2[i].tolist() if not math.isnan(x)]
        if i =="4":
            x_dgree=[x for x in df2[i].tolist() if not math.isnan(x)]
        if i =="5":
            y_balance=[x for x in df2[i].tolist() if not math.isnan(x)]
             

