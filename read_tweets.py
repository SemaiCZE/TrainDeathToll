#!/usr/bin/env python

import twitter
import json
import webapp2
from google.appengine.api import taskqueue


def get_status_info(status):
    return "START", status.text


class ReadTweets(webapp2.RequestHandler):
    def get(self):
        f = open("env.json", 'r')
        environ = json.loads(f.read())
        f.close()

        consumer_key = environ['CONSUMER_KEY']
        consumer_secret = environ['CONSUMER_SECRET']
        access_key = environ['ACCESS_KEY']
        access_secret = environ['ACCESS_SECRET']
        twiter_user = "cdmimoradnosti"
        queue_name = "new-tweets"

        q = taskqueue.Queue('new-tweets')
        tasks = []

        api = twitter.Api(consumer_key, consumer_secret, access_key, access_secret, cache=None)
        statuses = api.GetUserTimeline(screen_name=twiter_user)
        for status in statuses:
            status_tag, status_data = get_status_info(status)
            tasks.append(taskqueue.Task(payload=status_data, method='PULL', tag=status_tag))

        q.add(tasks)

        self.response.out.write('')


app = webapp2.WSGIApplication([('/read_tweets', ReadTweets)], debug=True)

