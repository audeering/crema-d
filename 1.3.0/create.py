"""
create.py

add new age tables to the databases

* per speaker use 10-20 random sentences of about 2-10 seconds
* split into train test dev, should be age/gender balanced
* make two versions: one with emotion acted samples and one with neutral
* so all in all 6 new tables

"""

import os
import pandas as pd
import audb
import audeer
import audformat


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

    splits = ["train", "dev", "test"]
    for split in splits:
        pass
    db.save(build_dir)


if __name__ == "__main__":
    main()
