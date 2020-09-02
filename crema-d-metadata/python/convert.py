import os
import pandas as pd

import audata


def convert(
    description: str,
    annotation_root: str,
    data_root: str
) -> audata.Database:
    ##################
    # Initialization #
    ##################
    db = audata.Database(
        name='crema-d',
        source='https://github.com/CheyneyComputerScience/CREMA-D',
        usage=audata.define.Usage.RESEARCH,
        languages=[audata.utils.str_to_language('en')],
        description=description,
        meta={'pdf': ('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4313618/')})

    db.media['microphone'] = audata.AudioInfo(
        format='wav',
        sampling_rate=16000,
        channels=1
    )

    ###########
    # Parsing #
    ###########
    metadata = pd.read_csv(os.path.join(
        annotation_root, 'metadata', 'VideoDemographics.csv'))
    tabulated = pd.read_csv(os.path.join(
        annotation_root, 'metadata', 'processedResults', 'tabulatedVotes.csv'))
    summarized = pd.read_csv(os.path.join(
        annotation_root, 'metadata', 'processedResults', 'summaryTable.csv'))
    metadata = metadata.set_index('ActorID').rename(columns={
        "Age": "age",
        "Race": "race",
        "Sex": "sex",
        "Ethnicity": "ethnicity"
    })
    sex_dict = {
        "Female": audata.core.define.Gender.FEMALE,
        "Male": audata.core.define.Gender.MALE
    }
    metadata["sex"] = metadata["sex"].apply(lambda x: sex_dict[x])

    summarized['Actor'] = summarized['FileName'].apply(
        lambda x: x.split('_')[0])
    summarized['Sentence'] = summarized['FileName'].apply(
        lambda x: x.split('_')[1])
    summarized['Emotion'] = summarized['FileName'].apply(
        lambda x: x.split('_')[2])
    summarized['Intensity'] = summarized['FileName'].apply(
        lambda x: x.split('_')[3])
    summarized['file'] = summarized.apply(
        lambda x: os.path.join(x['Actor'], x['FileName'] + '.wav'), axis=1)
    summarized.set_index('file', inplace=True)

    tabulated['Actor'] = tabulated['fileName'].apply(lambda x: x.split('_')[0])
    tabulated['file'] = tabulated.apply(lambda x: os.path.join(
        x['Actor'], x['fileName'] + '.wav'), axis=1)
    tabulated.set_index('file', inplace=True)

    ###########
    # Schemes #
    ###########
    sentence_map_dict = {
        "IEO": "It's eleven o'clock",
        "TIE": "That is exactly what happened",
        "IOM": "I'm on my way to the meeting",
        "IWW": "I wonder what this is about",
        "TAI": "The airplane is almost full",
        "MTI": "Maybe tomorrow it will be cold",
        "IWL": "I would like a new alarm clock",
        "ITH": "I think I have a doctor's appointment",
        "DFA": "Don't forget a jacket",
        "ITS": "I think I've seen this before",
        "TSI": "The surface is slick",
        "WSI": "We'll stop in a couple of minutes"
    }

    db.schemes['sentence'] = audata.Scheme(
        dtype=audata.core.define.DataType.STRING,
        labels=sentence_map_dict
    )

    db.schemes['emotion'] = audata.Scheme(
        labels=[
            "anger",
            "happiness",
            "fear",
            "disgust",
            "neutral",
            "sadness"
        ]
    )
    db.schemes['emotion.intensity'] = audata.Scheme(
        labels=[
            "low",
            "mid",
            "high",
            "unspecified"
        ]
    )
    db.schemes['emotion.value'] = audata.Scheme(
        dtype=audata.core.define.DataType.FLOAT,
        minimum=0,
        maximum=100
    )

    db.schemes['emotion.agreement'] = audata.Scheme(
        dtype=audata.core.define.DataType.FLOAT,
        minimum=0,
        maximum=1
    )

    db.schemes['speaker'] = audata.Scheme(
        labels=metadata.to_dict()
    )

    ##########
    # Tables #
    ##########
    db.tables['speaker'] = audata.Table(
        files=summarized.index
    )
    db.tables['speaker']['speaker'] = audata.Column(
        scheme_id='speaker'
    )
    db.tables['speaker']['speaker'].set(summarized['Actor'])

    db.tables['sentence'] = audata.Table(
        files=summarized.index
    )
    db.tables['sentence']['sentence'] = audata.Column(
        scheme_id='sentence'
    )
    db.tables['sentence']['sentence'].set(summarized['Sentence'])

    emotion_dict = {
        "NEU": "neutral",
        "ANG": "anger",
        "HAP": "happiness",
        "DIS": "disgust",
        "SAD": "sadness",
        "FEA": "fear"
    }

    db.tables['emotion'] = audata.Table(
        files=summarized.index
    )
    db.tables['emotion']['emotion'] = audata.Column(
        scheme_id='emotion',
        description='Emotion the actors were asked to present'
    )
    db.tables['emotion']['emotion'].set(
        summarized['Emotion'].apply(lambda x: emotion_dict[x]))

    db.tables['emotion']['emotion.intensity'] = audata.Column(
        scheme_id='emotion.intensity',
        description='Intensity of emotion the actors were asked to present'

    )

    intensity_dict = {
        "LO": "low",
        "MD": "mid",
        "HI": "high",
        "XX": "unspecified"
    }

    db.tables['emotion']['emotion.intensity'].set(
        summarized['Intensity'].apply(lambda x: intensity_dict[x]))

    emotion_dict = {
        "N": "neutral",
        "A": "anger",
        "H": "happiness",
        "D": "disgust",
        "S": "sadness",
        "F": "fear"
    }

    modality_dict = {
        'Voice': '1',
        'Face': '2',
        'MultiModal': '3'
    }

    for modality in ['Voice', 'Face', 'MultiModal']:
        max_emotions = summarized[f'{modality}Vote'].apply(
            lambda x: len(x.split(':'))).max()

        db.tables[f'emotion.{modality.lower()}'] = audata.Table(
            files=summarized.index,
            description=f'Perceived emotion when taking into account the {modality.lower()} modality'
        )

        db.tables[f'emotion.{modality.lower()}']['emotion'] = audata.Column(
            scheme_id='emotion',
            description='Primary perceived emotion'
        )
        db.tables[f'emotion.{modality.lower()}']['emotion'].set(
            summarized[f'{modality}Vote'].apply(
                lambda x: emotion_dict[x.split(':')[0]])
        )

        db.tables[f'emotion.{modality.lower()}']['emotion.level'] = audata.Column(
            scheme_id='emotion.value',
            description='Primary perceived emotion level'
        )
        db.tables[f'emotion.{modality.lower()}']['emotion.level'].set(
            summarized[f'{modality}Level'].apply(
                lambda x: x.split(':')[0]).astype(float)
        )

        db.tables[f'emotion.{modality.lower()}']['emotion.agreement'] = audata.Column(
            scheme_id='emotion.agreement',
            description='Annotator agreement'
        )
        db.tables[f'emotion.{modality.lower()}']['emotion.agreement'].set(
            tabulated.loc[tabulated['Unnamed: 0'].apply(
                lambda x: str(x)[0] == modality_dict[modality]), 'agreement']
        )

        for emotion_index in range(1, max_emotions):

            def map_secondary_emotion(x, index):
                try:
                    return emotion_dict[x.split(':')[index]]
                except IndexError:
                    return None

            def map_secondary_emotion_level(x, index):
                try:
                    return float(x.split(':')[index])
                except IndexError:
                    return None

            db.tables[f'emotion.{modality.lower()}'][f'emotion.{emotion_index}'] = audata.Column(
                scheme_id='emotion',
                description=f'Secondary emotion (order: {emotion_index})'
            )
            db.tables[f'emotion.{modality.lower()}'][f'emotion.{emotion_index}'].set(
                summarized[f'{modality}Vote'].apply(
                    lambda x: map_secondary_emotion(x, emotion_index))
            )

            db.tables[f'emotion.{modality.lower()}'][f'emotion.{emotion_index}.level'] = audata.Column(
                scheme_id='emotion.value',
                description=f'Secondary emotion (order: {emotion_index})'
            )
            db.tables[f'emotion.{modality.lower()}'][f'emotion.{emotion_index}.level'].set(
                summarized[f'{modality}Level'].apply(
                    lambda x: map_secondary_emotion_level(x, emotion_index))
            )

    return db
