import argparse
import pathlib
import pickle

import hjson
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox


def generate():
    ox.config(log_console=False)

    with open("places.hjson", 'r') as f:
        places = hjson.load(f)

    gdf = ox.geocode_to_gdf(list(places.values()))
    print(gdf.display_name)

    for place in places.keys():
        graph_filename = pathlib.Path(f'{place.replace(" ", "-")}.pkl')
        if graph_filename.exists():
            continue

        print(f"Generate data for {place}")

        graph_directed = ox.graph_from_place(place, network_type="drive")
        graph_undirected = ox.add_edge_bearings(ox.get_undirected(graph_directed))
        bin_counts, bin_edges = ox.bearing._bearings_distribution(graph_undirected, 36, 1)
        entropy = ox.bearing.orientation_entropy(graph_undirected)

        data = {
            'name':       place,
            'bin_counts': bin_counts,
            'bin_edges':  bin_edges,
            'entropy':    entropy,
        }

        with open(graph_filename, 'wb') as f:
            pickle.dump(data, f)


def plot():
    with open("saved_data.pkl", 'rb') as f:
        data = pickle.load(f)

    n = len(data)
    ncols = int(np.ceil(np.sqrt(n)))
    nrows = int(np.ceil(n / ncols))
    figsize = (ncols * 5, nrows * 5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, subplot_kw={"projection": "polar"})

    for ax, (name, d) in zip(axes.flat, data.items()):
        graph = d['graph']
        ox.bearing.plot_orientation(graph, ax=ax, title=name, area=True)

    # add figure title and save image
    suptitle_font = {
        "family":     "DejaVu Sans",
        "fontsize":   60,
        "fontweight": "normal",
        "y":          1,
    }
    fig.suptitle("City Street Network Orientation", **suptitle_font)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.35)
    fig.savefig("images/street-orientations.png", facecolor="w", dpi=500, bbox_inches="tight")
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    generate_parser = subparsers.add_parser('generate')
    generate_parser.set_defaults(func=generate)
    plot_parser = subparsers.add_parser('plot')
    plot_parser.set_defaults(func=plot)

    args = parser.parse_args()
    args.func(args)
