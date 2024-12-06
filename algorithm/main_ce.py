from simulate_pcn import *
tot_amo=[]
bidirectional_graph = Making_graph()
bidirectional_graph, tot_amo , routed , no_route , more_exp,g = start_simulate(bidirectional_graph,200000,0,0,n=0,tot_amo =[],more_exp=[],routed=[],no_route=[],g=[],centeralizer=True)
x_dgree,y_balance=dgree_balance_node(bidirectional_graph,'dgree_balance_ce')
plot_unbalance(g,'unbalance_ce')
plot_payment_hist(routed,no_route,more_exp,'payment_hist_ce')
plot_path_size(tot_amo,'path_size_ce')
plot_fee(tot_amo,'fee_plot_ce')
save_graph(bidirectional_graph,name="GRAPH_ce")
save_data(tot_amo,more_exp ,routed ,no_route  ,g  ,x_dgree ,y_balance ,name_tot='data_tot_ce',name_list_data='data_list_ce')