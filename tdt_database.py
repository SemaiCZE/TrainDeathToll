#!/usr/bin/env python

from google.appengine.ext import db


def tweets_key():
    return db.Key.from_path('Tweets', 'default')


class Tweet(db.Model):
    """Models one tweet entry in database"""
    tweet_id = db.IntegerProperty(required=True)
    publish_time = db.DateTimeProperty(required=True)
    track_number = db.StringProperty(required=True)
    link = db.LinkProperty()
    desired_end = db.TimeProperty()
    end = db.DateTimeProperty()
    cause = db.StringProperty()
    description = db.StringProperty()


class TrackEventCounterShard(db.Model):
    """Records the number of events for every track"""
    SHARD_COUNT = 10
    shard_number = db.IntegerProperty(required=True)
    track_number = db.StringProperty(required=True)
    event_count = db.IntegerProperty(default=0)
