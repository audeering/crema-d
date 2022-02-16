import json
import shutil
import os

import audb
import audeer
import audformat

name = 'crema-d'
previous_version = '1.0.5'
source_dir = '../source_dir'
source_dir = audeer.mkdir(source_dir)

build_dir = '../build'
build_dir = audeer.mkdir(build_dir)

audb.load_to(
    source_dir,
    name,
    version=previous_version,
    num_workers=8,
    cache_root=None,
    verbose=True
)
db = audformat.Database.load(source_dir)

with open('speaker_splits.json', 'r') as fp:
    speaker_splits = json.load(fp)

split_mapping = {
    'train': audformat.define.SplitType.TRAIN,
    'dev': audformat.define.SplitType.DEVELOP,
    'test': audformat.define.SplitType.TEST
}

full_speaker_df = db['speaker'].get()
full_emotions_df = db['emotion'].get()

for split, speakers in speaker_splits.items():
    split_speaker_df = full_speaker_df[full_speaker_df['speaker'].isin(speakers)]
    split_index = split_speaker_df.index

    db.splits[split] = audformat.Split(type=split_mapping[split],
                                       description=f'Unofficial speaker-independent {split} split')

    split_emotion_df = full_emotions_df.loc[split_index, :]

    db[f'emotion.{split}'] = audformat.Table(split_index, split_id=split)
    db[f'emotion.{split}']['emotion'] = audformat.Column(scheme_id='emotion')
    db[f'emotion.{split}']['emotion'].set(split_emotion_df['emotion'])

    db[f'emotion.{split}']['emotion.intensity'] = audformat.Column(scheme_id='emotion.intensity')
    db[f'emotion.{split}']['emotion.intensity'].set(split_emotion_df['emotion.intensity'])

db.drop_tables('emotion')

all_speakers = full_speaker_df['speaker'].unique()
for speaker in all_speakers:
    speaker_dir = str(speaker)
    shutil.copytree(
        os.path.join(source_dir, speaker_dir),
        os.path.join(build_dir, speaker_dir),
    )
db.save(build_dir)
