#!/usr/bin/env python
# coding=utf-8

import twitter
import json
import webapp2
import time
import logging
from datetime import datetime, date
from google.appengine.api import taskqueue, memcache
from tdt_database import Tweet


twitter_user = "cdmimoradnosti"
queue_name = "new-tweets"
task_process_script = "/process_tweets"
months_map = {
    u"led": 1,
    u"úno": 2,
    u"bře": 3,
    u"dub": 4,
    u"kvě": 5,
    u"črv": 6,
    u"čer": 7,
    u"srp": 8,
    u"zář": 9,
    u"říj": 10,
    u"lis": 11,
    u"pro": 12
}


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
            for i in range(wanted_parts)]


def get_tweets(twitter_api):
    cache_tweet_id = 'last_tweet_id'

    # Try to get ID of last tweet from memcache
    last_tweet_id = memcache.get(cache_tweet_id)
    logging.info("Last tweet id from memcache: " + str(last_tweet_id))

    # If ID of last tweet is not in memcache, fetch it from database
    if not last_tweet_id:
        last_tweet_db = Tweet.gql("ORDER BY tweet_id DESC").get()  # get returns first entry or None
        if last_tweet_db:
            last_tweet_id = last_tweet_db.tweet_id
            logging.info("Last tweet id from database: " + str(last_tweet_id))

    if last_tweet_id:
        statuses = twitter_api.GetUserTimeline(screen_name=twitter_user, since_id=last_tweet_id, include_rts=False,
                                               exclude_replies=True)
    else:
        statuses = twitter_api.GetUserTimeline(screen_name=twitter_user, count=200, include_rts=False,
                                               exclude_replies=True)

    if statuses:
        last_tweet_id = statuses[0].id
        logging.info("Last tweet id from new tweets: " + str(last_tweet_id))

    # Update the memcache
    memcache.set(cache_tweet_id, last_tweet_id, 604800)  # cache for 1 week
    logging.info("Memcache updated with: " + str(last_tweet_id))

    return statuses


def get_status_info(status):
    text = status.text
    result = dict()

    # Add tweet id which will be used as index in database
    result["tweet_id"] = status.id

    # Add tweet creation time to results
    result["publish_time"] = status.created_at_in_seconds

    # Handle start and stop tags by first symbol (+ or -)
    if text[0] == u'+':
        result["tag"] = "START"
    else:
        result["tag"] = "END"
    text = text[1:]

    # Get track number
    result["track_number"] = text[1:4]
    text = text[6:]

    # Get hyperlink from the end
    try:
        link_index = text.index(u"http")
        result["link"] = text[link_index:]
        text = text[:link_index - 1]
    except ValueError:
        pass

    # Get desired end of issue
    try:
        endtime_index = text.index(u"Konec v")
        endtime_str = text[endtime_index:]
        # trim "Konec v " string from begining
        endtime_str = endtime_str[8:]

        current_time = datetime.now()
        if len(endtime_str) == 5:
            end_time = datetime.strptime(endtime_str, '%H:%M')
            result["desired_end"] = time.mktime(datetime.combine(current_time.date(), end_time.time()).timetuple())
        else:
            end_time = datetime.strptime(endtime_str[-5:], '%H:%M')
            endtime_str = endtime_str[:-8]  # trims " v 09:30" string
            i = endtime_str.find(u".")
            day = endtime_str[:i]
            month = months_map[endtime_str[i + 2:]]
            end_date = date(current_time.year, month, int(day))
            result["desired_end"] = time.mktime(datetime.combine(end_date, end_time.time()).timetuple())
        text = text[:endtime_index - 1]
    except ValueError:
        pass

    # Get cause of the issue
    last_dot = text.rfind(u'.', 0, -2)
    result["cause"] = text[last_dot + 2:-1]
    text = text[:last_dot]

    # Remaining part is description of place
    result["description"] = text

    return json.dumps(result, ensure_ascii=False, encoding='utf8')


class ReadTweets(webapp2.RequestHandler):
    def get(self):
        f = open("env.json", 'r')
        environ = json.loads(f.read())
        f.close()

        consumer_key = environ['CONSUMER_KEY']
        consumer_secret = environ['CONSUMER_SECRET']
        access_key = environ['ACCESS_KEY']
        access_secret = environ['ACCESS_SECRET']

        q = taskqueue.Queue(queue_name)
        tweets = []

        api = twitter.Api(consumer_key, consumer_secret, access_key, access_secret, cache=None)
        statuses = get_tweets(api)
        if statuses:
            for status in statuses:
                status_data = get_status_info(status)
                tweets.append(status_data)
                logging.info("Got new tweet: " + str(status.id))

            # Don't send more than 100 tweets at once
            if len(tweets) >= 100:
                split_tasks = split_list(tweets, wanted_parts=4)
                for item in split_tasks:
                    q.add([taskqueue.Task(payload=json.dumps(item), method='POST', url=task_process_script)])
            else:
                q.add([taskqueue.Task(payload=json.dumps(tweets), method='POST', url=task_process_script)])

        self.response.out.write('<br>\n'.join(tweets))


app = webapp2.WSGIApplication([('/read_tweets', ReadTweets)], debug=True)

