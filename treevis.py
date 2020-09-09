import jsonpickle
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
# from greedyconcept import InterestTree, InterestTreeNode



def draw_tree(tree):
    g = nx.Graph()
    plt.figure(figsize=(18, 18))

    edges = []
    make_list(edges, tree)
    print(edges)

    g.add_edges_from(edges)

    pos = graphviz_layout(g)  # positions for all nodes

    # nodes
    nx.draw_networkx_nodes(g, pos, node_size=100)

    # edges
    nx.draw_networkx_edges(g, pos, edgelist=edges, width=1)

    # labels
    nx.draw_networkx_labels(g, pos, font_size=10, font_family="sans-serif")

    plt.axis("off")
    plt.savefig(f"data/paths/{tree.start}-{tree.end}.pdf")


def make_list(edges, tree):
    for node in tree.all:
        if node.parent is not None:
            edges.append((node.word, node.parent.word))
        # else:
        #     edges.append((node.word, None))
    return edges


if __name__ == '__main__':
    with open("tree.json", "r") as file:
        tree = jsonpickle.decode(file.read())
    draw_tree(tree)
    # data = find_path("football", "sewing")
    # data = a_star_path(InterestTreeNode("football"), "sewing")
    # print(data.path)
    # with open(f"data/paths/{data.start}-{data.end}.json", "w") as file:
    #     file.write(jsonpickle.encode(data.path))
    # with open(f"tree.json", "w") as file:
    #     file.write(jsonpickle.encode(data))
