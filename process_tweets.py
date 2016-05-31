#!/usr/bin/env python

import json
import random
import webapp2
import tdt_database
from collections import Counter
from datetime import datetime
from google.appengine.ext import db
from tdt_database import Tweet, TrackEventCounterShard, CurrentEventCounter


def get_tweets(tasks):
    start_tweets = []
    end_tweets = []
    task_list = json.loads(tasks, encoding='utf8')

    for task in task_list:
        task_data = json.loads(task)
        if task_data["tag"] == "START":
            start_tweets.append(task_data)
        else:
            end_tweets.append(task_data)

    return start_tweets, end_tweets


def update_track_event_counter(track_number, count):
    shard_number = random.randint(0, TrackEventCounterShard.SHARD_COUNT - 1)
    shard = TrackEventCounterShard.all().filter("shard_number=", shard_number).filter("track_number=", track_number).ancestor(tdt_database.counters_key()).get()

    if shard is None:
        shard = TrackEventCounterShard(
            shard_number=shard_number,
            track_number=track_number,
            parent=tdt_database.counters_key()
        )

    shard.event_count += count
    shard.put()


def update_current_event_counter(track_number, number):
    counter = CurrentEventCounter.all().filter("track_number=", track_number).ancestor(tdt_database.counters_key()).get()

    if counter is None:
        counter = CurrentEventCounter(
            parent=tdt_database.counters_key(),
            track_number=track_number
        )

    counter.balance += number
    counter.put()


def update_counters(track_event_counter, current_event_counter):
    for cnt in track_event_counter:
        update_track_event_counter(cnt, track_event_counter[cnt])

    for cnt in current_event_counter:
        update_current_event_counter(cnt, current_event_counter[cnt])


def save_new_tweet(tweet):
    dtweet = Tweet(
        parent=tdt_database.tweets_key(),
        tweet_id=long(tweet['tweet_id']),
        publish_time=datetime.fromtimestamp(tweet['publish_time']),
        track_number=tweet['track_number'],
        tag=tweet['tag']
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


def save_start_tweets(start_tweets, track_event_counter, current_event_counter):
    for tweet in start_tweets:
        save_new_tweet(tweet)
        track_event_counter[tweet['track_number']] += 1
        current_event_counter[tweet['track_number']] += 1


def save_end_tweets(end_tweets, current_event_counter):
    for tweet in end_tweets:
        save_new_tweet(tweet)
        current_event_counter[tweet['track_number']] -= 1


@db.transactional(xg=True)
def save_tweets(start_tweets, end_tweets):
    track_event_counter = Counter()
    current_event_counter = Counter()

    save_start_tweets(start_tweets, track_event_counter, current_event_counter)
    save_end_tweets(end_tweets, current_event_counter)
    update_counters(track_event_counter, current_event_counter)


class ProcessTweets(webapp2.RequestHandler):
    def post(self):
        tasks = self.request.body
        start_tweets, end_tweets = get_tweets(tasks)
    
        self.response.out.write('Start tweets:<br>\n')
        for tweet in start_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>End tweets:<br>\n')
        for tweet in end_tweets:
            self.response.out.write('&nbsp;&nbsp;%s<br>\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
        self.response.out.write('<br>')
    
        save_tweets(start_tweets, end_tweets)
        self.response.out.write('Tweets processed successfully!<br>')


app = webapp2.WSGIApplication([('/process_tweets', ProcessTweets)], debug=True)

