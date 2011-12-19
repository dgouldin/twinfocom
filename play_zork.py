#!/usr/bin/env python
from twitter_stream_consume import twitter_stream
from private_settings import TWITTER_USERNAME, TWITTER_PASSWORD
from tasks import run_zork

def handler(tweet):
    tweet_id = tweet['id_str']
    username = tweet['user']['screen_name']
    content = tweet['text']

    print '[%s] %s' % (username, content)
    run_zork.delay(tweet_id, username, content)

twitter_stream(TWITTER_USERNAME, TWITTER_PASSWORD, handler, track='@playzork')

