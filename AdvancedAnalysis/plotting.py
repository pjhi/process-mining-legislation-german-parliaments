import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.decomposition import PCA
import numpy as np




def plot_agreement_scores(df, title):
    """
    Expects a DataFrame with columns:
    - statement_number
    - title
    - government
    - opposition
    - all
    """

    sns.set(style="whitegrid")

    # Create readable statement labels
    df_plotting = df.copy()
    df_plotting["Statement"] = (
        df_plotting["statement_number"].astype(str)
        + ": "
        + df_plotting["title"]
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.35
    x = range(len(df_plotting))

    ax.bar(
        [i - bar_width/2 for i in x],
        df_plotting["government"],
        width=bar_width,
        label="Government",
        color="black"
    )

    ax.bar(
        [i + bar_width/2 for i in x],
        df_plotting["opposition"],
        width=bar_width,
        label="Opposition",
        color="orange"
    )

    ax.bar(
        x,
        df_plotting["all"],
        width=bar_width / 1.5,
        label="Overall",
        color="blue"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(df_plotting["Statement"], rotation=45, ha="right")
    ax.set_ylabel("Agreement Score")
    ax.set_title(title + "\nAgreement per Statement: Government vs Opposition")
    ax.legend()

    plt.tight_layout()
    plt.show()



def plot_agreement_scores_heat_map(df, title):
    """
    Expects a DataFrame with columns:
    - statement_number
    - title
    - government
    - opposition
    - all
    """

    # Create readable statement label
    plot_data = df.copy()
    plot_data["Statement"] = (
        plot_data["statement_number"].astype(str)
        + ": "
        + plot_data["title"]
    )

    # Select only relevant columns
    plot_data = plot_data[
        ["Statement", "government", "opposition", "all"]
    ].set_index("Statement")

    # Custom colormap: white (0), blue (+1)
    colors = ["#FFFFFF", "#3399FF"]
    cmap = LinearSegmentedColormap.from_list("disagree_agree", colors)

    sns.set(style="whitegrid")

    plt.figure(figsize=(10, 12))
    sns.heatmap(
        plot_data,
        annot=True,
        cmap=cmap,
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Agreement Score'}
    )

    plt.title(title + "\nAgreement per Statement: Government vs Opposition")
    plt.xlabel("Group")
    plt.ylabel("Statement")
    plt.tight_layout()
    plt.show()



def plot_topic_embeddings(topics_df, title):
    """
    Plots a 2D PCA projection of topic embeddings.

    Parameters
    ----------
    topics_df : pandas.DataFrame
        Must contain:
        - 'These: Titel'
        - 'embedding' (list/array per row)
        - optionally 'These Nr.'
    """

    # Create labels (include thesis number if available)
    if "These Nr." in topics_df.columns:
        labels = (
            topics_df["These Nr."].astype(str) + ": " +
            topics_df["These: Titel"].str.slice(0, 25)
        ).tolist()
    else:
        labels = topics_df["These: Titel"].str.slice(0, 30).tolist()

    # Convert embeddings column to 2D numpy array
    X = np.vstack(topics_df["embedding"].values)

    # PCA projection to 2D
    X2 = PCA(n_components=2).fit_transform(X)

    # Plot
    plt.figure(figsize=(10, 8))
    plt.scatter(X2[:, 0], X2[:, 1])

    for i, label in enumerate(labels):
        plt.annotate(
            label,
            (X2[i, 0], X2[i, 1]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9
        )

    plt.title(title + "\nTopic Embeddings (PCA projection)")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.tight_layout()
    plt.show()



def plot_multiple_topic_embeddings(dfs, names=None):
    """
    Plots multiple topic DataFrames in one shared PCA projection.

    Parameters
    ----------
    dfs : list of pandas.DataFrame
        Each DataFrame must contain:
        - 'These: Titel'
        - 'embedding' (list/array per row)
        - optionally 'These Nr.'
    names : list of str, optional
        Labels for legend (same length as dfs)
    """

    if names is None:
        names = [f"Group {i+1}" for i in range(len(dfs))]

    # Combine all embeddings to compute ONE shared PCA space
    all_embeddings = np.vstack([
        np.vstack(df["embedding"].values)
        for df in dfs
    ])

    pca = PCA(n_components=2)
    all_projected = pca.fit_transform(all_embeddings)

    # Split projections back to original groups
    sizes = [len(df) for df in dfs]
    splits = np.cumsum(sizes)[:-1]
    projected_groups = np.split(all_projected, splits)

    # Plot
    plt.figure(figsize=(10, 8))

    colors = plt.cm.tab10.colors  # up to 10 distinct colors

    for i, (df, proj, name) in enumerate(zip(dfs, projected_groups, names)):
        plt.scatter(
            proj[:, 0],
            proj[:, 1],
            label=name,
            color=colors[i % len(colors)]
        )

        # Create labels
        if "These Nr." in df.columns:
            labels = (
                df["These Nr."].astype(str) + ": " +
                df["These: Titel"].str.slice(0, 20)
            ).tolist()
        else:
            labels = df["These: Titel"].str.slice(0, 25).tolist()

        for j, label in enumerate(labels):
            plt.annotate(
                label,
                (proj[j, 0], proj[j, 1]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8
            )

    plt.title("Topic Embeddings Comparison (Shared PCA)")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.legend()
    plt.tight_layout()
    plt.show()



def plot_trace_embeddings(dfs, names=None, text_col='Titel', trace_col='case:concept:name'):
    """
    Plots multiple DataFrames of trace embeddings in one shared PCA projection.
    Each trace is represented by one embedding (from your trace-based approach).

    Parameters
    ----------
    dfs : list of pandas.DataFrame
        Each DataFrame must contain:
        - 'embedding' (list/array per row)
        - trace_col (e.g., 'trace_id')
        - text_col (e.g., 'title') for labels
    names : list of str, optional
        Labels for the legend (same length as dfs)
    text_col : str
        Column used for annotation
    trace_col : str
        Column used to group traces
    """

    if names is None:
        names = [f"Group {i+1}" for i in range(len(dfs))]

    # Step 1: For each DataFrame, group by trace_id and pick one row per trace
    grouped_dfs = []
    labels_per_group = []
    for df in dfs:
        trace_df = df.groupby(trace_col).first().reset_index()
        grouped_dfs.append(trace_df)
        labels_per_group.append(trace_df[text_col].tolist())

    # Step 2: Combine all embeddings to compute a shared PCA space
    all_embeddings = np.vstack([np.vstack(gdf['case:embedding'].values) for gdf in grouped_dfs])
    pca = PCA(n_components=2)
    all_projected = pca.fit_transform(all_embeddings)

    # Step 3: Split projections back to groups
    sizes = [len(gdf) for gdf in grouped_dfs]
    splits = np.cumsum(sizes)[:-1]
    projected_groups = np.split(all_projected, splits)

    # Step 4: Plot
    plt.figure(figsize=(12, 8))
    colors = plt.cm.tab10.colors  # up to 10 distinct colors

    for i, (proj, labels, name) in enumerate(zip(projected_groups, labels_per_group, names)):
        plt.scatter(
            proj[:, 0],
            proj[:, 1],
            label=name,
            color=colors[i % len(colors)],
            alpha=0.7,
            s=50
        )

    '''
        # Annotate points
        for j, label in enumerate(labels):
            plt.annotate(
                label[:40],  # limit to first 40 chars
                (proj[j, 0], proj[j, 1]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
                alpha=0.8
            )
    '''

    plt.title("Trace Embeddings Comparison (Shared PCA)", fontsize=16)
    plt.xlabel("PCA Component 1", fontsize=12)
    plt.ylabel("PCA Component 2", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
