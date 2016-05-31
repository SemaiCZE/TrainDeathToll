import webapp2
from webapp2_extras import jinja2
from collections import Counter
from tdt_database import Tweet, TrackEventCounterShard
from google.appengine.api import memcache


def get_current_events():
    cache_events_id = "current_events_id"
    cached_events = memcache.get(cache_events_id)

    if cached_events:
        current_events = cached_events
    else:
        current_events = list(Tweet.gql("WHERE end = :none ORDER BY publish_time DESC", none=None).run(limit=100))
        memcache.add(cache_events_id, current_events, 120)  # Cache for 2 minutes

    return current_events


def get_track_event_counter():
    counter_id = "track_event_counter_id"
    cached_counter = memcache.get(counter_id)

    if cached_counter:
        track_event_counter = cached_counter
    else:
        track_event_counter = Counter()
        for entry in TrackEventCounterShard.all():
            track_event_counter[entry.track_number] += entry.event_count

        memcache.add(counter_id, track_event_counter, 120)  # Cache for 2 minutes

    return track_event_counter


class MainPage(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)

    def get(self):
        current_events = get_current_events()
        track_event_counter = get_track_event_counter()

        self.render_response(
            "stats.html",
            current_events=current_events,
            frequent_tracks=track_event_counter.most_common(10),
            frequent_tracks_max=track_event_counter.most_common(1)[0][1]
        )


app = webapp2.WSGIApplication([('/', MainPage), ('/index.html', MainPage)], debug=True)

