#!/usr/bin/env python

from google.appengine.ext import db


def tweets_key():
    return db.Key.from_path('Tweets', 'default')


def counters_key():
    return db.Key.from_path('Counters', 'default')


class Tweet(db.Model):
    """Models one start tweet entry in database"""
    tweet_id = db.IntegerProperty(required=True)
    publish_time = db.DateTimeProperty(required=True)
    track_number = db.StringProperty(required=True)
    tag = db.StringProperty(required=True)
    link = db.StringProperty()
    desired_end = db.DateTimeProperty()
    cause = db.StringProperty()
    description = db.StringProperty()


class TrackEventCounterShard(db.Model):
    """Records the number of events for every track"""
    SHARD_COUNT = 10
    shard_number = db.IntegerProperty(required=True)
    track_number = db.StringProperty(required=True)
    event_count = db.IntegerProperty(default=0)


class EventCauseCounterShard(db.Model):
    """Records the number of events for every cause of event"""
    SHARD_COUNT = 10
    shard_number = db.IntegerProperty(required=True)
    cause = db.StringProperty(required=True)
    event_count = db.IntegerProperty(default=0)


class CurrentEventCounter(db.Model):
    """Counter for ballance of starts and ends of events"""
    track_number = db.StringProperty(required=True)
    balance = db.IntegerProperty(default=0)