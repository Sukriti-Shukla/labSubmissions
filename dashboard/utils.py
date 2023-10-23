from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def plot_experiment_data(df):
    if df.shape[1] == 2:  # Check if the dataframe has exactly 2 columns
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title('Plot of Column 1 vs Column 2')
        graph = get_graph()
        plt.close()
        return graph
    return None
