import logging
import os
from io import BytesIO
import cloudstorage as gcs
from google.appengine.api import app_identity
import webapp2
from wordcloud import WordCloud
from collections import Counter
from tdt_database import EventDescriptionCounterShard


class MakeWordCloud(webapp2.RedirectHandler):
    def get(self):
        word_frequencies = Counter()

        for shard in EventDescriptionCounterShard.all():
            word_frequencies[shard.word] += shard.frequency

        cloud = WordCloud(background_color="white")
        cloud.generate_from_frequencies(word_frequencies.most_common())

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open("cloud.png",
                            'w',
                            content_type='text/plain',
                            options={},
                            retry_params=write_retry_params)
        image_content = BytesIO()
        cloud.to_image().save(image_content, format="PNG")
        gcs_file.write(image_content.getvalue())
        gcs_file.close()


app = webapp2.WSGIApplication([("/make_word_cloud", MakeWordCloud)], True)