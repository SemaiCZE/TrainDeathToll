#!/usr/bin/env python

import json
import webapp2
from google.appengine.api import taskqueue
from google.appengine.ext import db


queue_name = "new-tweets"


class Tweet(db.Model):
    """Models one tweet entry in database"""
    publish_time = db.DateTimeProperty(required=True)
    track_number = db.IntegerProperty(required=True)
    link = db.LinkProperty(required=True)
    desired_end = db.DateTimeProperty()
    cause = db.TextProperty()
    description = db.TextProperty()


def get_tasks(queue):
    tasks = queue.lease_tasks(3600, 100)
    return tasks

def get_tweets(tasks):
    tweets = []
    return tweets

def save_tweets(tweets):
    return True

class ProcessTweets(webapp2.RequestHandler):
    def get(self):
        queue = taskqueue.Queue(queue_name)
        tasks = get_tasks(queue)
        tweets = get_tweets(tasks)
        if save_tweets(tweets):
            queue.delete_tasks(tasks)
            self.response.out.write('Tweets processed successfully!\n')
        else:
            self.response.out.write('Error occured while processing tweets\n')


app = webapp2.WSGIApplication([('/process_tweets', ProcessTweets)], debug=True)

