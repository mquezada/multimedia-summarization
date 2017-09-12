"""
workflow:

- seleccionar un evento e de la DB
- seleccionar tweets T de e
- eliminar duplicados (quasi duplicados?) de T => T'
- resolver URLs de T'' => U
- eliminar spam de T' => T''
- generar documentos D desde (U, T)
- obtener representantes de D => R
- Generar representacion vectorial de R => V
- Hacer clusters de V => C
- Ordenar clusters por impacto π(C)
- Obtener representantes desde C => R'
- Presentar R'
"""

from db import datasets
from db import events
from nlp.filter_tweets import filter_tweets
from nlp.tokenizer import Tokenizer
from document_generation.documents import join_tweets, get_representants

from db.engines import engine_of215 as engine

from sqlalchemy.orm import sessionmaker

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s : %(message)s', level=logging.INFO)
tokenizer = Tokenizer()

# custom variables
event_name = "Hurricane Irma"
event_ids = datasets.irma
Session = sessionmaker(engine, autocommit=True)

session = Session()


# seleccionar tweets T de e
tweet_url_list = events.get_tweets(event_name, event_ids, session)

# eliminar spam de T' => T''
filtered_tweet_url_list = filter_tweets(tweet_url_list, tokenizer)
filtered_tweets = [t for t, _ in filtered_tweet_url_list]
events.set_filtered_tweets(filtered_tweets, session)

tweet_urls = events.create_tweet_urls_dict(filtered_tweet_url_list)

# generar documentos D desde (U, T)
groups = join_tweets(tweet_urls)

# obtener representantes de D => R
representants = list(get_representants(groups, tweet_urls))
tweets = events.get_tweets_from_ids(representants, session)