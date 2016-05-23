import webapp2


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Main page of TrainDeathToll")


app = webapp2.WSGIApplication([('/', MainPage), ('/index.html', MainPage)], debug=True)

