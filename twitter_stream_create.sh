#!/bin/bash
TWITTER_STREAM_PIPE_PATH=$1
TWITTER_USERNAME=$2
TWITTER_PASSWORD=$3
TWITTER_STREAM_QUERYSTRING=$4

while [ 1 ]
do
  if ! [ -a $TWITTER_STREAM_PIPE_PATH ];
  then
    mkfifo $TWITTER_STREAM_PIPE_PATH;
  fi
  curl https://stream.twitter.com/1/statuses/filter.json?$TWITTER_STREAM_QUERYSTRING -u $TWITTER_USERNAME:$TWITTER_PASSWORD > $TWITTER_STREAM_PIPE_PATH
done