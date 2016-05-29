import webapp2
from webapp2_extras import jinja2


class MainPage(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)

    def get(self):
        self.render_response("stats.html")


app = webapp2.WSGIApplication([('/', MainPage), ('/index.html', MainPage)], debug=True)

