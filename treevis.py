import jsonpickle
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


# from greedyconcept import InterestTree, InterestTreeNode


def draw_tree(tree):
    g = nx.DiGraph()

    plt.figure(figsize=(18, 18))

    edges = []
    paths = []
    labels = {}
    # make_list(paths, edges, tree)
    # edges = paths
    get_data(edges, paths, labels, tree)
    print(edges)
    print("\n\n\n\n")
    print(paths)

    g.add_edges_from(edges)

    pos = graphviz_layout(g)  # positions for all nodes

    # nodes
    nx.draw_networkx_nodes(g, pos, node_size=100)
    nx.draw_networkx_nodes(g, pos, nodelist=[tree.user1.username, tree.user2.username], node_color="#ff8c00",
                           node_size=250)

    # edges
    nx.draw_networkx_edges(g, pos, edgelist=edges, width=1.5, arrows=True, arrowsize=2)
    nx.draw_networkx_edges(g, pos, edgelist=paths, width=1.5, edge_color="#007700", arrows=True, arrowsize=2)

    # labels
    nx.draw_networkx_labels(g, pos, font_size=10, font_family="sans-serif", font_weight="bold")
    nx.draw_networkx_edge_labels(g, pos, edge_labels=labels, font_color='red')

    plt.axis("off")
    plt.savefig(f"data/paths/{tree.user1.username}-{tree.user2.username}.pdf")


def make_list(paths, edges, tree):
    for node in tree.all:
        if node.parent is not None:
            edges.append((node.parent.word, node.word))
    for word in tree.start_words:
        edges.append((tree.user1.username, word))
        paths.append((tree.user1.username, word))
    for word in tree.end_words:
        edges.append((tree.user2.username, word))
        paths.append((tree.user2.username, word))
        # else:
        #     edges.append((node.word, None))
    for path in tree.paths:
        for node in path:
            if node.parent is not None:
                paths.append((node.parent, node.word))
    return edges


def get_data(edges, paths, labels, tree):
    for path in tree.paths:
        for node in path:
            if node.parent is not None:
                if node.edge in "end":
                    edges.append((node.parent, node.word))
                    labels[(node.parent, node.word)] = node.relation
                else:
                    edges.append((node.word, node.parent))
                    labels[(node.word, node.parent)] = node.relation
    for word in tree.start_words:
        edges.append((tree.user1.username, word))
    for word in tree.end_words:
        edges.append((tree.user2.username, word))
    print(tree.paths)
    for node in tree.paths[-1]:
        if node.parent is not None:
            if node.edge in "end":
                paths.append((node.parent, node.word))
            else:
                paths.append((node.word, node.parent))


if __name__ == '__main__':
    with open("data/paths/Nick_Offerman-DaveRamsey.json", "r") as file:
        tree = jsonpickle.decode(file.read())
    draw_tree(tree)
    # data = find_path("football", "sewing")
    # data = a_star_path(InterestTreeNode("football"), "sewing")
    # print(data.path)
    # with open(f"data/paths/{data.start}-{data.end}.json", "w") as file:
    #     file.write(jsonpickle.encode(data.path))
    # with open(f"tree.json", "w") as file:
    #     file.write(jsonpickle.encode(data))
