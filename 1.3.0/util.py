import pandas as pd
import matplotlib.pyplot as plt

num_workers = 8


# plot sex distribution, age and duration
def describe_df(df, file_path):
    title = f"# samples: {df.shape[0]}, # speakers: {df.speaker.nunique()}"
    if "duration" in df:
        fig, axes = plt.subplots(nrows=2, ncols=2)
        df["age"].plot(kind="hist", ax=axes[0, 0], title="age")

        #    df["duration"].plot(kind="hist", ax=axes[0, 1], title="duration")
        df.groupby("gender")["speaker"].nunique().plot(kind="pie", ax=axes[1, 0])
        df_speakers = pd.DataFrame()
        pd.options.mode.chained_assignment = None  # default='warn'
        for s in df.speaker.unique():
            df_speaker = df[df.speaker == s]
            df_speaker["samplenum"] = df_speaker.shape[0]
            df_speakers = pd.concat([df_speakers, df_speaker.head(1)])
        df_speakers["samplenum"].value_counts().sort_values().plot(
            kind="bar",
            stacked=True,
            title=f"samples per speaker",
            rot=0,
            ax=axes[1, 1],
        )
    else:
        fig, axes = plt.subplots(nrows=1, ncols=3)
        df["age"].plot(kind="hist", ax=axes[0], title="age")
        df.groupby("gender")["speaker"].nunique().plot(kind="pie", ax=axes[1])
        df_speakers = pd.DataFrame()
        pd.options.mode.chained_assignment = None  # default='warn'
        for s in df.speaker.unique():
            df_speaker = df[df.speaker == s]
            df_speaker["samplenum"] = df_speaker.shape[0]
            df_speakers = pd.concat([df_speakers, df_speaker.head(1)])
        df_speakers["samplenum"].value_counts().sort_values().plot(
            kind="bar",
            stacked=True,
            title=f"samples per speaker",
            rot=0,
            ax=axes[2],
        )

    fig.suptitle(title)
    plt.tight_layout()
    fig.savefig(file_path)


def limit_speakers(df, max=20):
    """
    Limit the number of samples per speaker to max.
    """
    df_ret = pd.DataFrame()
    for s in df.speaker.unique():
        s_df = df[df["speaker"].eq(s)]
        if s_df.shape[0] < max:
            df_ret = pd.concat([df_ret, s_df])
        else:
            df_ret = pd.concat([df_ret, s_df.sample(max)])
    return df_ret
