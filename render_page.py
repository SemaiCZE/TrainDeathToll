import webapp2
from webapp2_extras import jinja2
from collections import Counter
from tdt_database import Tweet, TrackEventCounterShard


class MainPage(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)

    def get(self):
        current_events = Tweet.gql("WHERE end = :none ORDER BY publish_time", none = None).fetch(100)
        track_event_counter = Counter()

        for entry in TrackEventCounterShard.all():
            track_event_counter[entry.track_number] += entry.event_count

        self.render_response(
            "stats.html",
            current_events=current_events,
            frequent_tracks=track_event_counter.most_common(10),
            frequent_tracks_max=track_event_counter.most_common(1)[0][1]
        )


app = webapp2.WSGIApplication([('/', MainPage), ('/index.html', MainPage)], debug=True)

