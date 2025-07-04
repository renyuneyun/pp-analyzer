import pandas as pd
from pandas import DataFrame
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


T_EXACT = 'Exact'
T_RELAXED = 'Relaxed'  # Typically LCS=0.9
T_SUPER_RELAXED = 'Super relaxed'  # Typically LCS=0.3

T_GPT_4O_MINI = 'gpt-4o-mini'
T_GPT_4O = 'gpt-4o'
T_GPT_4O_MINI_FT = 'gpt-4o-mini (fine-tuned)'
T_GPT_4O_FT = 'gpt-4o (fine-tuned)'

T_F1 = 'F1 (overall)'
T_F1_NON_EMPTY = 'F1 (non-empty)'
T_F1_EMPTY = 'F1 (empty)'

colour = ["#F3D266", "#96C37D", "#2F7FC1"]
sns.set_palette(colour)


def from_data_quick(data):
    data_converted = {}
    for model, v1 in data.items():
        data_converted[model] = {}
        for metric_type, v2 in v1.items():
            data_converted[model][metric_type] = {}
            for i, (score, metric) in enumerate(zip(v2, [T_F1_NON_EMPTY, T_F1_EMPTY, T_F1])):
                data_converted[model][metric_type][metric] = score

    res = []  # List to be converted to DataFrame
    for model, v1 in data_converted.items():
        for metric_type, v2 in v1.items():
            for metric, score in v2.items():
                res.append({
                    'Model': model,
                    'Metric type': metric_type,
                    'Score type': metric,
                    'Score': score,
                })
            # res.append({
            #     'Model': model,
            #     'Metric type': metric_type,
            #     T_F1: v2[T_F1],
            #     T_F1_NON_EMPTY: v2[T_F1_NON_EMPTY],
            #     T_F1_EMPTY: v2[T_F1_EMPTY],
            # })
    return DataFrame(res)


DATA = {
    'Data Recognition': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.140, 0.880, 0.764],
            T_RELAXED: [0.185, 0.880, 0.771],
            T_SUPER_RELAXED: [0.195, 0.880, 0.773],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.546, 0.967, 0.927],
            T_RELAXED: [0.722, 0.967, 0.944],
            T_SUPER_RELAXED: [0.761, 0.967, 0.947],
        },
        T_GPT_4O: {
            T_EXACT: [0.276, 0.923, 0.839],
            T_RELAXED: [0.372, 0.923, 0.852],
            T_SUPER_RELAXED: [0.391, 0.923, 0.854],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.602, 0.968, 0.927],
            T_RELAXED: [0.635, 0.968, 0.930],
            T_SUPER_RELAXED: [0.699, 0.968, 0.938],
        },
    },
    'Data Classification': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.675, 1, 0.949],
            T_RELAXED: [0.680, 1, 0.950],
            T_SUPER_RELAXED: [0.781, 1, 0.966],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.732, 1, 0.787],
            T_RELAXED: [0.747, 1, 0.975],
            T_SUPER_RELAXED: [0.865, 1, 0.987],
        },
        T_GPT_4O: {
            T_EXACT: [0.668, 1, 0.948],
            T_RELAXED: [0.705, 1, 0.954],
            T_SUPER_RELAXED: [0.829, 1, 0.973],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.792, 1, 0.980],
            T_RELAXED: [0.803, 1, 0.981],
            T_SUPER_RELAXED: [0.892, 1, 0.990],
        },
    },
    'Purpose Recognition': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.070, 0.889, 0.713],
            T_RELAXED: [0.202, 0.889, 0.741],
            T_SUPER_RELAXED: [0.316, 0.889, 0.766],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.598, 0.938, 0.886],
            T_RELAXED: [0.729, 0.938, 0.906],
            T_SUPER_RELAXED: [0.773, 0.938, 0.913],
        },
        T_GPT_4O: {
            T_EXACT: [0.326, 0.934, 0.825],
            T_RELAXED: [0.501, 0.934, 0.856],
            T_SUPER_RELAXED: [0.610, 0.934, 0.876],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.558, 0.970, 0.907],
            T_RELAXED: [0.655, 0.970, 0.922],
            T_SUPER_RELAXED: [0.704, 0.970, 0.929],
        },
    },
    'Purpose Classification': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.563, 1, 0.906],
            T_RELAXED: [0.601, 1, 0.914],
            T_SUPER_RELAXED: [0.762, 1, 0.949],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.526, 1, 0.927],
            T_RELAXED: [0.571, 1, 0.934],
            T_SUPER_RELAXED: [0.747, 1, 0.961],
        },
        T_GPT_4O: {
            T_EXACT: [0.505, 1, 0.893],
            T_RELAXED: [0.582, 1, 0.910],
            T_SUPER_RELAXED: [0.750, 1, 0.946],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.555, 1, 0.932],
            T_RELAXED: [0.612, 1, 0.940],
            T_SUPER_RELAXED: [0.766, 1, 0.964],
        },
    },
    'Action Recognition': {
        T_GPT_4O_MINI: {
            T_EXACT: [0, 0.840, 0.706],
            T_RELAXED: [0.369, 0.840, 0.765],
            T_SUPER_RELAXED: [0.377, 0.840, 0.766],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.642, 0.766, 0.750],
            T_RELAXED: [0.651, 0.766, 0.751],
            T_SUPER_RELAXED: [0.664, 0.766, 0.753],
        },
        T_GPT_4O: {
            T_EXACT: [0, 0.878, 0.758],
            T_RELAXED: [0.372, 0.878, 0.809],
            T_SUPER_RELAXED: [0.372, 0.878, 0.808],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.596, 0.847, 0.817],
            T_RELAXED: [0.615, 0.847, 0.819],
            T_SUPER_RELAXED: [0.615, 0.847, 0.819],
        },
    },
    # 'protection method recognition & classification': {
    #     T_GPT_4O_MINI_FT: {
    #         T_SUPER_RELAXED: [0, 0.983, 0.979],
    #     },
    #     T_GPT_4O: {
    #         T_SUPER_RELAXED: [0.265, 0.977, 0.966],
    #     },
    # },
    'Party Recognition': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.259, 0.741, 0.655],
            T_RELAXED: [0.325, 0.741, 0.667],
            T_SUPER_RELAXED: [0.354, 0.741, 0.672],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.470, 0.858, 0.807],
            T_RELAXED: [0.488, 0.858, 0.810],
            T_SUPER_RELAXED: [0.498, 0.858, 0.811],
        },
        T_GPT_4O: {
            T_EXACT: [0.380, 0.607, 0.565],
            T_RELAXED: [0.472, 0.607, 0.582],
            T_SUPER_RELAXED: [0.519, 0.607, 0.591],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.544, 0.705, 0.684],
            T_RELAXED: [0.581, 0.705, 0.689],
            T_SUPER_RELAXED: [0.596, 0.705, 0.691],
        },
    },
    'Relation Recognition': {
        T_GPT_4O_MINI: {
            T_EXACT: [0.387, 1, 0.824],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.573, 1, 0.871],
            # T_RELAXED: [0.868, 1, 0.960],
            # T_SUPER_RELAXED: [0.915, 1, 0.974],
        },
        T_GPT_4O: {
            T_EXACT: [0.601, 1, 0.885],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.706, 1, 0.925],
        },
    },
}


def plot_group_4(data, title: str):
    g = sns.catplot(data=data, x='Metric type', y='Score', hue='Score type', col='Model', kind='bar', width=0.6, aspect=1, legend_out=True)

    for ax in g.axes.ravel():
    # add annotations
        for c in ax.containers:
            ax.bar_label(c, label_type='edge', fontsize=10, rotation=300)
        ax.margins(y=0.2)

    g.figure.suptitle(title, fontsize=16, x=0.5, y=1.15)
    g.set_titles("{col_name}", size=14, x=0.5, y=1.1)
    g.set(ylim=(0, 1), yticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    # plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1])
    g.set_xlabels(fontsize=13)
    g.set_ylabels(fontsize=13)
    g.set_xticklabels(fontsize=12)
    # g.set_yticklabels(fontsize=12)
    filename = title.replace(' ', '-').lower()
    g.savefig(filename + ".pdf", dpi=300)
    g.savefig(filename + ".png", dpi=300)


def get_data(query_type):
    return from_data_quick(DATA[query_type])


def main(query_type=None, title=None):
    # if not query_type:
    #     query_type = DATA.keys()
    # else:
    #     query_type = [query_type]
    # for qt in query_type:
    #     data_d = get_data(query_type=qt)
    #     # data_d = get_data(query_type=query_type)
    #     # Plot all data points, grouped by model
    #     # fig = px.bar(data_d, x='Model', y='Score', color='Metric type', barmode='group')
    #     # fig.show()
    #     plot_group_4(data_d, title=qt)



if __name__ == '__main__':
    main()
