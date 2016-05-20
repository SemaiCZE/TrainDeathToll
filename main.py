#!/usr/bin/env python

import twitter
import os

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_key = os.environ.get('ACCESS_KEY')
access_secret = os.environ.get('ACCESS_SECRET')
twiter_user = "cdmimoradnosti"


api = twitter.Api(consumer_key, consumer_secret, access_key, access_secret)
statuses = api.GetUserTimeline(screen_name=twiter_user)
print([s.text for s in statuses])

