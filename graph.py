# graph representation
import networkx as nx

def create_sample_graph():
    G = nx.Graph()
    edges = [
        ('A', 'B'), ('A', 'C'), ('B', 'D'),
        ('C', 'D'), ('C', 'E'), ('D', 'E')
    ]
    G.add_edges_from(edges)
    return G
