import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def make(simd="avx2", Olevel="O3"):
    os.system(f"make build simd={simd} Olevel={Olevel}")


def run(n1, n2, n3, num_thread, iteration, b1, b2, b3):
    filename = os.listdir("~/Documents/iso3dfd-st7/bin/")
    p = subprocess.Popen([
        f"~/Documents/iso3dfd-st7/bin/{filename}",
        str(n1),
        str(n2),
        str(n3),
        str(num_thread),
        str(iteration),
        str(b1),
        str(b2),
        str(b3)
    ],
        stdout=subprocess.PIPE)
    p.wait()
    outputs = p.communicate()[0].decode("utf-8").split("\n")
    time = float(outputs[0].split(" ")[-2])
    throughput = float(outputs[1].split(" ")[-2])
    flops = float(outputs[2].split(" ")[-2])
    return time, throughput, flops


class AntColony():

    def __init__(self, alpha, beta, rho, Q, nb_ant, levels):
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.nb_ant = nb_ant

        self.levels = levels
        self.graph = self.__init_graph()

    def __init_graph(self):
        """ Initialize the graph """
        graph = nx.DiGraph()
        # Initialisation des noeuds
        for level, choices in self.levels:
            for choice in choices:
                graph.add_node((level, choice), level=level)
        # Initialisation des liens
        for (name_i, choices_i), (name_j, choices_j) in zip(self.levels, self.levels[1:]):
            for choice_i in choices_i:
                for choice_j in choices_j:
                    graph.add_edge((name_i, choice_i),
                                   (name_j, choice_j), tau=1, nu=1)
        print(graph)
        return graph

    def plot_graph(self):
        """ Show the graph """
        pos = nx.nx_pydot.graphviz_layout(self.graph, prog="dot", root="init")
        edges, tau = zip(*nx.get_edge_attributes(self.graph, 'tau').items())
        nx.draw(self.graph, pos, node_size=10, edgelist=edges,
                edge_color=tau, edge_cmap=plt.cm.plasma)
        plt.show()

    def pick_path(self):
        """ Choose the path of an ant """
        path = [("init", "init")]
        for _ in range(len(self.levels)-1):
            items_view = self.graph[path[-1]].items()
            neighbors = [a for (a, _) in items_view]
            neighbors_idx = np.arange(len(neighbors))
            tau = np.array([e["tau"]
                           for (_, e) in items_view], dtype=np.float32)
            nu = np.array([e["nu"] for (_, e) in items_view], dtype=np.float32)
            weights = (tau**self.alpha) * (nu**self.beta)
            weights /= np.sum(weights)
            path.append(neighbors[np.random.choice(neighbors_idx, p=weights)])
        return path

    def epoch(self):
        pathes = []
        performances = []
        for _ in range(self.nb_ant):
            path = self.pick_path()
            performances.append(
                run(n1=128, n2=128, n3=128, iteration=100, **dict(path[3:]))[0])
        pathes = [path for _, path in sorted(
            zip(performances, pathes), key=lambda pair: pair[0])]

        # Reward best ants
        # ...

        # Update tau
        # ...


alpha = 0
beta = 0
rho = 0
Q = 0
nb_ant = 10


block_min = 1
block_max = 256
block_size = 32


levels = [("init", {"init"}),
          ("simd", {"avx", "avx2", 'avx512', 'sse'}),
          ("Olevel", {"O2", "O3", "Ofast"}),
          ("num_thread", range(1, 32)),
          ("b1", set(np.delete(np.arange(block_min-1, block_max+1, block_size), 0))),
          ("b2", set(np.delete(np.arange(block_min-1, block_max+1, block_size), 0))),
          ("b3", set(np.delete(np.arange(block_min-1, block_max+1, block_size), 0)))

          ]

print(levels[6])

# AntColony(alpha, beta, rho, Q, nb_ant, levels)