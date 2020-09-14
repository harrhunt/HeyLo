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
    nx.draw_networkx_nodes(g, pos, nodelist=[tree.user1.username, tree.user2.username], node_color="#ff8c00",
                           node_size=250)

    # edges
    nx.draw_networkx_edges(g, pos, edgelist=edges, width=1)

    # labels
    nx.draw_networkx_labels(g, pos, font_size=10, font_family="sans-serif", font_weight="bold")

    plt.axis("off")
    plt.savefig(f"data/paths/{tree.user1.username}-{tree.user2.username}.pdf")


def make_list(edges, tree):
    for node in tree.all:
        if node.parent is not None:
            edges.append((node.parent.word, node.word))
    for word in tree.start_words:
        edges.append((tree.user1.username, word))
    for word in tree.end_words:
        edges.append((tree.user2.username, word))
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
