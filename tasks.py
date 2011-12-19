import os
import urllib

import oauth2 as oauth
from celery.task import task

import dumb_frotz

from private_settings import (
    ZORK_PATH,
    ZORK_SAVE_PATH_BASE,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_USER_KEY,
    TWITTER_USER_SECRET,
)


def paginate_tweet_content(username, content):
    prefix = '@%s' % username
    prefix_length = len(prefix) + 1
    suffix = '[%d/%%d]'
    suffix_length = len((suffix % 1) % 10) + 1 # assume < 100 pages

    if len(content) < 140 - prefix_length:
        # fast-path for no pagination
        return [' '.join((prefix, content))]

    tokens = content.split(' ')
    page_num = 0
    tweets = []
    while tokens:
        page_tokens = [prefix]
        while tokens and len(
                ' '.join(page_tokens + [tokens[0]])) < 140 - suffix_length:
            try:
                page_tokens.append(tokens.pop())
            except IndexError:
                # all tokens have been used
                break
        page_num += 1
        page_tokens.append(suffix % page_num)
        tweets.append(' '.join(page_tokens))
    return [t % page_num for t in tweets]

@task
def run_zork(tweet_id, username, tweet_content):
    save_path = os.path.join(ZORK_SAVE_PATH_BASE, 'zork_%s.sav' % username)
    command = tweet_content.replace('@playzork', '').strip()
    output = dumb_frotz.execute(ZORK_PATH, command=command,
        save_path=save_path)

    # now reply with the output
    consumer = oauth.Consumer(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    token = oauth.Token(TWITTER_USER_KEY, TWITTER_USER_SECRET)
    client = oauth.Client(consumer, token=token)
    base_url = 'http://api.twitter.com/1/statuses/update.json'

    tweets = paginate_tweet_content(username, output)
    for tweet in tweets:
        params = {
            'status': tweet,
            'in_reply_to_status_id': tweet_id,
        }
        url = '%s?%s' % (base_url, urllib.urlencode(params))
        client.request(url, method='POST')

