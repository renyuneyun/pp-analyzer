from pandas import DataFrame
import plotly.express as px
import seaborn as sns


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


sns.set_palette("muted")


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
    'data extraction': {
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.546, 0.967, 0.927],
            T_RELAXED: [0.722, 0.967, 0.944],
            T_SUPER_RELAXED: [0.761, 0.967, 0.947],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.602, 0.968, 0.927],
            T_RELAXED: [0.635, 0.968, 0.930],
            T_SUPER_RELAXED: [0.699, 0.968, 0.938],
        },
    },
    'data classification': {
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.732, 1, 0.787],
            T_RELAXED: [0.747, 1, 0.975],
            T_SUPER_RELAXED: [0.865, 1, 0.987],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.792, 1, 0.980],
            T_RELAXED: [0.803, 1, 0.981],
            T_SUPER_RELAXED: [0.892, 1, 0.990],
        },
    },
    'purpose recognition': {
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
    'purpose classification': {
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.526, 1, 0.927],
            T_RELAXED: [0.571, 1, 0.934],
            T_SUPER_RELAXED: [0.747, 1, 0.961],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.555, 1, 0.932],
            T_RELAXED: [0.612, 1, 0.940],
            T_SUPER_RELAXED: [0.766, 1, 0.964],
        },
    },
    'action (event) recognition': {
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
        },
    },
    'protection method recognition & classification': {
        T_GPT_4O_MINI_FT: {
            T_SUPER_RELAXED: [0, 0.983, 0.979],
        },
        T_GPT_4O: {
            T_SUPER_RELAXED: [0.265, 0.977, 0.966],
        },
    },
    'first-party/Third-party entity recognition & classification': {
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.470, 0.858, 0.807],
            T_RELAXED: [0.488, 0.858, 0.810],
            T_SUPER_RELAXED: [0.498, 0.858, 0.811],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.544, 0.705, 0.684],
            T_RELAXED: [0.581, 0.705, 0.689],
            T_SUPER_RELAXED: [0.596, 0.705, 0.691],
        },
    },
    'relation recognition/classification': {
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.573, 1, 0.871],
            T_RELAXED: [0.868, 1, 0.960],
            T_SUPER_RELAXED: [0.915, 1, 0.974],
        },
        T_GPT_4O: {
            T_EXACT: [0.601, 1, 0.885],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.706, 1, 0.925],
        },
    },
}


def plot_group_4(data, title=None):
    g = sns.catplot(data=data, x='Metric type', y='Score', hue='Score type', col='Model', kind='bar')
    g.figure.suptitle(title)


def get_data(query_type):
    return from_data_quick(DATA[query_type])


def main(query_type=None, title=None):
    if not query_type:
        query_type = DATA.keys()
    else:
        query_type = [query_type]
    for qt in query_type:
        data_d = get_data(query_type=qt)
        # data_d = get_data(query_type=query_type)
        # Plot all data points, grouped by model
        # fig = px.bar(data_d, x='Model', y='Score', color='Metric type', barmode='group')
        # fig.show()
        plot_group_4(data_d, title=qt)


if __name__ == '__main__':
    main()
