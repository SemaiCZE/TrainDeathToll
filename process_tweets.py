#!/usr/bin/env python

import json
import random
import webapp2
import tdt_database
from datetime import datetime
from google.appengine.api import taskqueue
from google.appengine.ext import db
from tdt_database import Tweet, TrackEventCounterShard


def get_tweets(tasks):
    start_tweets = []
    start_tasks = []
    end_tweets = []
    end_tasks = []
    task_list = json.loads(tasks, encoding='utf8')

    for task in task_list:
        task_data = json.loads(task)
        if task_data["tag"] == "START":
            start_tweets.append(task_data)
            start_tasks.append(task)
        else:
            end_tweets.append(task_data)
            end_tasks.append(task)

    return start_tasks, end_tasks, start_tweets, end_tweets


def update_track_event_counter(track_number):
    shard_number = random.randint(0, TrackEventCounterShard.SHARD_COUNT - 1)
    shard = TrackEventCounterShard.all().filter("shard_number=", shard_number).filter("track_number=", track_number).ancestor(tdt_database.tweets_key()).get()

    if shard is None:
        shard = TrackEventCounterShard(
            shard_number=shard_number,
            track_number=track_number,
            parent=tdt_database.tweets_key()
        )

    shard.event_count += 1
    shard.put()


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
    update_track_event_counter(tweet['track_number'])


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
    def post(self):
        tasks = self.request.body
        start_tasks, end_tasks, start_tweets, end_tweets = get_tweets(tasks)
    
        self.response.out.write('Start tweets:<br>\n')
        for tweet in start_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>End tweets:<br>\n')
        for tweet in end_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>')
    
        save_start_tweets(start_tweets)
        self.response.out.write('Start tweets processed successfully!<br>')

        save_end_tweets(end_tweets)
        self.response.out.write('End tweets processed successfully!<br>')


app = webapp2.WSGIApplication([('/process_tweets', ProcessTweets)], debug=True)

