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
    end_tweets = []

    for task in tasks:
        if task.tag == "START":
            start_tweets.append(json.loads(task.payload, encoding='utf8'))
        else:
            end_tweets.append(json.loads(task.payload, encoding='utf8'))

    return start_tweets, end_tweets


@db.transactional
def save_tweets(start_tweets, end_tweets):
    for tweet in start_tweets:
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

    for tweet in end_tweets:
        dtweets = Tweet.all().ancestor(tdt_database.tweets_key()).filter("track_number =", tweet['track_number'])
        if dtweets:
            for dtweet in dtweets:
                dtweet.end = datetime.fromtimestamp(tweet['publish_time'])
                dtweet.put()


class ProcessTweets(webapp2.RequestHandler):
    def get(self):
        queue = taskqueue.Queue(queue_name)
        tasks = queue.lease_tasks(60, 100)
        start_tweets, end_tweets = get_tweets(tasks)

        self.response.out.write('Start tweets:<br>\n')
        for tweet in start_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>End tweets:<br>\n')
        for tweet in end_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>')

        try:
            save_tweets(start_tweets, end_tweets)
            raise Exception('error')
            queue.delete_tasks(tasks)
            self.response.out.write('Tweets processed successfully!<br>')
        except Exception, e:
            self.response.out.write('Error occurred while processing tweets: %s<br>' % e)


app = webapp2.WSGIApplication([('/process_tweets', ProcessTweets)], debug=True)

