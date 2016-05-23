import webapp2

class NotFound(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Page not found")


app = webapp2.WSGIApplication([('/.*', NotFound)], debug=True)

