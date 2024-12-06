from simulate_pcn import *
tot_amo=[]
bidirectional_graph = Making_graph()
bidirectional_graph, tot_amo , routed , no_route , more_exp,g = start_simulate(bidirectional_graph,200000,0,0,n=0,tot_amo =[],more_exp=[],routed=[],no_route=[],g=[],centeralizer=False)
x_dgree,y_balance=dgree_balance_node(bidirectional_graph)
plot_unbalance(g)
plot_payment_hist(routed,no_route,more_exp)
plot_path_size(tot_amo)
plot_fee(tot_amo)
save_graph(bidirectional_graph,name="GRAPH")
save_data(tot_amo,more_exp ,routed ,no_route  ,g  ,x_dgree ,y_balance ,name_tot='data_tot',name_list_data='data_list')