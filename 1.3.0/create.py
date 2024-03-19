import os
import random
import pandas as pd

import audb
import audeer
import audformat
import audiofile
import util
import trainDevTestSplit

# make it reproducible
random.seed(23)

image_dir = "images/"


def main():
    name = "crema-d"
    previous_version = "1.2.0"

    build_dir = "../build"
    build_dir = audeer.mkdir(build_dir)

    audb.load_to(
        build_dir,
        name,
        version=previous_version,
        num_workers=8,
        only_metadata=True,
        verbose=True,
    )
    db = audformat.Database.load(build_dir)

    # get age, gender and emotion info
    df = db["files"].get()
    df_emo = pd.concat(
        [
            db["emotion.categories.train"].get(),
            db["emotion.categories.dev"].get(),
            db["emotion.categories.test"].get(),
        ]
    )
    df["age"] = db["files"]["speaker"].get(map="age").astype("int")
    df["gender"] = db["files"]["speaker"].get(map="sex")
    #    df["duration"] = df.index.to_series().map(lambda x: audiofile.duration(x))
    df = df[df["gender"] != "other"]
    df = df[df["corrupted"] != True]
    audeer.mkdir(image_dir)
    util.describe_df(df, f"{image_dir}all.png")
    df["emotion"] = df_emo["emotion.0"].values
    df = df[df.emotion.isin(["neutral"])]
    util.describe_df(df, f"{image_dir}all_neutral.png")
    df = util.limit_speakers(df)
    util.describe_df(df, f"{image_dir}all_limited.png")

    # create split sets
    splits = {}
    df_train, df_dev, df_test = trainDevTestSplit.split_df(df)
    splits["train"] = df_train
    splits["dev"] = df_dev
    splits["test"] = df_test
    # plot distributions
    for split in ["train", "dev", "test"]:
        print(f"split: {split}")
        util.describe_df(splits[split], f"{image_dir}{split}.png")

    # fill the database with new tables
    age_tables_name = "age."
    for split in splits.keys():
        db[f"{age_tables_name}{split}"] = audformat.Table(
            splits[split].index,
            description=f"Table selected for age and binary gender balance from the emotionally neutral samples, max 20 samples per speaker.",
        )
        for field in ["speaker"]:
            db[f"{age_tables_name}{split}"][field] = audformat.Column(scheme_id=field)
            db[f"{age_tables_name}{split}"][field].set(splits[split][field])

    db.save(build_dir)


if __name__ == "__main__":
    main()
