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
            for i, (score, metric) in enumerate(zip(v2, [T_F1, T_F1_NON_EMPTY, T_F1_EMPTY])):
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
        },
    },
    'data classification': {
        T_GPT_4O_MINI: {
            T_SUPER_RELAXED: [0.309, 0.809, 0.684],
        },
        T_GPT_4O_MINI_FT: {
            T_EXACT: [0.732, 1, 0.787],
            T_RELAXED: [0.747, 1, 0.975],
        },
        T_GPT_4O_FT: {
            T_EXACT: [0.792, 1, 0.980],
            T_RELAXED: [0.803, 1, 0.981],
        },
    },
}


def plot_group_4(data, title=None):
    g = sns.catplot(data=data, x='Metric type', y='Score', hue='Score type', col='Model', kind='bar')
    g.figure.suptitle(title)


def get_data(query_type):
    return from_data_quick(DATA[query_type])


def main(query_type='data extraction', title='Data extraction'):
    data_d = get_data(query_type=query_type)
    # Plot all data points, grouped by model
    # fig = px.bar(data_d, x='Model', y='Score', color='Metric type', barmode='group')
    # fig.show()
    plot_group_4(data_d, title=title)


if __name__ == '__main__':
    main()