import webapp2
from webapp2_extras import jinja2
from tdt_database import Tweet


class MainPage(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)

    def get(self):
        current_events = Tweet.gql("WHERE end = :none ORDER BY publish_time", none = None).fetch(100)
        self.render_response("stats.html", current_events = current_events)


app = webapp2.WSGIApplication([('/', MainPage), ('/index.html', MainPage)], debug=True)

