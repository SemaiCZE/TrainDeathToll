#!/usr/bin/env python

import json
import webapp2
import tdt_database
from datetime import datetime
from google.appengine.api import taskqueue
from google.appengine.ext import db
from tdt_database import Tweet


queue_name = "new-tweets"


def get_tweets(tasks):
    start_tweets = []
    start_tasks = []
    end_tweets = []
    end_tasks = []

    for task in tasks:
        if task.tag == "START":
            start_tweets.append(json.loads(task.payload, encoding='utf8'))
            start_tasks.append(task)
        else:
            end_tweets.append(json.loads(task.payload, encoding='utf8'))
            end_tasks.append(task)

    return start_tasks, end_tasks, start_tweets, end_tweets


def save_new_tweet(tweet):
    dtweet = Tweet(
        parent=tdt_database.tweets_key(),
        tweet_id=long(tweet['tweet_id']),
        publish_time=datetime.fromtimestamp(tweet['publish_time']),
        track_number=tweet['track_number']
    )
    if 'link' in tweet:
        dtweet.link = tweet['link']
    if 'desired_end' in tweet:
        dtweet.desired_end = datetime.strptime(tweet['desired_end'], '%H:%M').time()
    if 'cause' in tweet:
        dtweet.cause = tweet['cause']
    if 'description' in tweet:
        dtweet.description = tweet['description']

    dtweet.put()


@db.transactional
def save_start_tweets(start_tweets):
    for tweet in start_tweets:
        save_new_tweet(tweet)


@db.transactional
def save_end_tweets(end_tweets):
    for tweet in end_tweets:
        dtweets = Tweet.all().ancestor(tdt_database.tweets_key()).filter("track_number =", tweet['track_number'])
        if dtweets:
            for dtweet in dtweets:
                dtweet.end = datetime.fromtimestamp(tweet['publish_time'])
                dtweet.put()
        else:
            save_new_tweet(tweet)


class ProcessTweets(webapp2.RequestHandler):
    def get(self):
        queue = taskqueue.Queue(queue_name)
        tasks = queue.lease_tasks(60, 200)
        start_tasks, end_tasks, start_tweets, end_tweets = get_tweets(tasks)

        self.response.out.write('Start tweets:<br>\n')
        for tweet in start_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>End tweets:<br>\n')
        for tweet in end_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>')

        try:
            save_start_tweets(start_tweets)
            queue.delete_tasks(start_tasks)
            self.response.out.write('Start tweets processed successfully!<br>')
        except Exception, e:
            self.response.out.write('Error occurred while processing start tweets: %s<br>' % e)

        try:
            save_end_tweets(end_tweets)
            queue.delete_tasks(end_tasks)
            self.response.out.write('End tweets processed successfully!<br>')
        except Exception, e:
            self.response.out.write('Error occurred while processing end tweets: %s<br>' % e)


app = webapp2.WSGIApplication([('/process_tweets', ProcessTweets)], debug=True)

