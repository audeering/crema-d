import os
import pandas as pd

import audata


def convert(
    description: str,
    annotation_root: str,
    data_root: str
) -> audata.Database:
    raise NotImplementedError
    ##################
    # Initialization #
    ##################
    db = audata.Database(
        name='crema-d',
        source='https://sail.usc.edu/iemocap/',
        usage=audata.define.Usage.RESEARCH,
        languages=[audata.utils.str_to_language('en')],
        description=description,
        meta={'pdf': ('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4313618/')})

    db.media['microphone'] = audata.AudioInfo(
        format='wav',
        sampling_rate=16000,
        channels=2
    )

    return db
