from document_generation import expand_urls
from db.models_new import Tweet, TweetURL, ShortURL, ExpandedURL
from db.engines import engine_of215 as engine
from tqdm import tqdm
from sqlalchemy.orm import sessionmaker
import logging
import spacy

max_size = 2048

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s : %(message)s', level=logging.INFO)
Session = sessionmaker(engine)

session = Session()
nlp = spacy.load('en', parser=False, tagger=False, entity=False, matcher=False)
batch_size = 10000
n_threads = 64

while True:
    tweets = session.query(Tweet).filter(~Tweet.url_expanded).limit(batch_size).all()
    logger.info(f"read {len(tweets)} tweets")

    info, short_tweet = expand_urls.expand_urls(nlp, tweets, n_threads=n_threads)
    info_items = list(info.items())

    logger.info(f"saving {len(info_items)} _new urls")
    urls_to_save = []

    for short, (long, title, clean) in tqdm(info_items):
        expanded = session.query(ExpandedURL).filter(ExpandedURL.expanded_clean.like(clean.strip() + "%")).first()

        if not expanded:
            expanded = ExpandedURL(expanded_url=long, title=title[:max_size], expanded_clean=clean)
            session.add(expanded)

        url = ShortURL(short_url=short, expanded_id=expanded.id)
        session.add(url)
        urls_to_save.append(url)

    for url, (short, _) in tqdm(list(zip(urls_to_save, info_items))):
        tweet_ids = short_tweet[short]
        for tweet_id in tweet_ids:
            tweet_url = TweetURL(tweet_id=tweet_id, url_id=url.id)
            session.add(tweet_url)

    for _tweet in tweets:
        _tweet.url_expanded = True

    logger.info("saving changes into db")
    session.commit()
    logger.info("done")





