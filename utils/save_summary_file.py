import re
from pathlib import Path

from sqlalchemy.orm import sessionmaker

import settings
from db.engines import engine_lmartine as engine
from db.models_new import Tweet

'''Save the text of the summary, some tweets are not available to be embbebed'''

Session = sessionmaker(engine, autocommit=True)
session = Session()

event_name = 'libya_hotel'
path_summaries = Path(settings.LOCAL_DATA_DIR_2, 'data', event_name, 'summaries', 'system')
list_files = [file for file in Path(path_summaries, 'ids').iterdir() if file.is_file() and file.name != 'mgraph.tsv']

for file in list_files:
    with file.open('r') as f:
        ids = f.readlines()
        tweets = session.query(Tweet).filter(Tweet.tweet_id.in_(ids)).all()
        with Path(path_summaries, f'{file.name[:-4]}_text.txt').open('w') as text_file:
            tweet_text = [re.sub(r"@\w+", '', re.sub(r"http\S+", '', tweet.text.replace('#', ''))) + '\n' for tweet in
                          tweets]
            text_file.writelines(tweet_text)
