#!/usr/bin/env python

from google.appengine.ext import db


def tweets_key():
    return db.Key.from_path('Tweets', 'default')

class Tweet(db.Model):
    """Models one tweet entry in database"""
    publish_time = db.DateTimeProperty(required=True)
    track_number = db.TextProperty(required=True)
    link = db.LinkProperty(required=True)
    desired_end = db.TimeProperty()
    end = db.DateTimeProperty()
    cause = db.TextProperty()
    description = db.TextProperty()
