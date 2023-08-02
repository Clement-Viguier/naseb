
from pywr.model import Model
import structout as so
import networkx as nx
# from pywr.nodes import Input, Output, Link

def model_surf_park():
   
    m = Model.load("./models/hydropower_example.json")
    m = Model.load("./models/proto_example.json")
    nx.draw(m.graph)
    stats = m.run()
    print(stats)
    

    # print(m.recorders["turbine1_energy"].values())

    df = m.to_dataframe()
    print(df.head())

    from matplotlib import pyplot as plt

    df.plot(subplots=True)
    plt.show()
