#!/usr/bin/env python

import twitter
import json
import webapp2
from google.appengine.api import taskqueue


def get_status_info(status):
    text = status.text
    result = dict()

    # Add tweet creation time to results
    result["publish_time"] = status.created_at_in_seconds

    # Handle start and stop tags by first symbol (+ or -)
    if text[0] == u'+':
        tag = "START"
    else:
        tag = "END"
    text = text[1:]

    # Get track number
    result["track_number"] = text[1:4]
    text = text[6:]

    # Get hyperlink from the end
    if text[-23:].startswith(u"https://"):
        result["link"] = text[-23:]
        text = text[:-24]

    # Get desired end of issue
    if text[-13:].startswith(u"Konec v "):
        result["desired_end"] = text[-5:]
        text = text[:-15]

    # Get cause of the issue
    last_dot = text.rfind(u'.', 0, -1)
    result["cause"] = text[last_dot + 2:-1]
    text = text[:last_dot]

    # Remaining part is description of place
    result["description"] = text

    return tag, json.dumps(result, ensure_ascii=False, encoding='utf8')


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

        q = taskqueue.Queue(queue_name)
        tasks = []
        tweets = []

        api = twitter.Api(consumer_key, consumer_secret, access_key, access_secret, cache=None)
        statuses = api.GetUserTimeline(screen_name=twiter_user)
        for status in statuses:
            status_tag, status_data = get_status_info(status)
            tweets.append(status_data)
            tasks.append(taskqueue.Task(payload=status_data, method='PULL', tag=status_tag))

        q.add(tasks)

        self.response.out.write('\n'.join(tweets))


app = webapp2.WSGIApplication([('/read_tweets', ReadTweets)], debug=True)

