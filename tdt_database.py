#!/usr/bin/env python

from google.appengine.ext import db


def tweets_key():
    return db.Key.from_path('Tweets', 'default')

class Tweet(db.Model):
    """Models one tweet entry in database"""
    tweet_id = db.IntegerProperty(required=True)
    publish_time = db.DateTimeProperty(required=True)
    track_number = db.TextProperty(required=True)
    link = db.LinkProperty()
    desired_end = db.TimeProperty()
    end = db.DateTimeProperty()
    cause = db.TextProperty()
    description = db.TextProperty()
