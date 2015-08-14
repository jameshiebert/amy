import datetime
import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.views import (
    PublishedEvents,
)
from api.serializers import EventSerializer
from workshops.models import (
    Event,
    Host,
)


class TestListingPastEvents(APITestCase):
    view = PublishedEvents
    url = 'api:events-published'

    def setUp(self):
        past = datetime.date(1993, 8, 30)
        today = datetime.date.today()
        future = datetime.date(2030, 3, 25)
        delta_2d = datetime.timedelta(days=2)
        delta_1d = datetime.timedelta(days=1)
        host = Host.objects.create(domain='host.edu', fullname='Host EDU')

        # past event
        self.event1 = Event.objects.create(
            slug='event1', start=past - delta_2d, end=past - delta_1d,
            host=host, latitude=3, longitude=-2, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
            url='http://url1/',
        )
        # ongoing event
        self.event2 = Event.objects.create(
            slug='event2', start=today - delta_2d, end=today + delta_2d,
            host=host, latitude=3, longitude=-2, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
            url='http://url2/',
        )
        # future event
        self.event3 = Event.objects.create(
            slug='event3', start=future - delta_2d, end=future + delta_2d,
            host=host, latitude=3, longitude=-2, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
            url='http://url3/',
        )
        # event with missing start
        self.event4 = Event.objects.create(
            slug='event4', end=past + delta_2d,
            host=host, latitude=3, longitude=-2, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
            url='http://url4/',
        )
        # event with missing URL
        self.event5 = Event.objects.create(
            slug='event5', start=future - delta_2d, end=future + delta_2d,
            host=host, latitude=3, longitude=-2, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
        )
        # event with missing both start and URL
        self.event8 = Event.objects.create(
            slug='event8', end=future + delta_1d,
            host=host, latitude=3.1, longitude=-1.9, venue='University',
            address='On the street', country='US', contact='sb@sth.edu',
        )

        self.expecting = [
            {
                'slug': 'event3',
                'start': '2030-03-23',
                'end': '2030-03-27',
                'humandate': 'Mar 23-27, 2030',
                'latitude': 3,
                'longitude': -2,
                'venue': 'University',
                'address': 'On the street',
                'country': 'US',
                'url': 'http://url3/',
                'contact': 'sb@sth.edu',
            },
            {
                'slug': 'event2',
                'start': '{:%Y-%m-%d}'.format(self.event2.start),
                'end': '{:%Y-%m-%d}'.format(self.event2.end),
                'humandate': EventSerializer.human_readable_date(
                    self.event2.start, self.event2.end
                ),
                'latitude': 3,
                'longitude': -2,
                'venue': 'University',
                'address': 'On the street',
                'country': 'US',
                'url': 'http://url2/',
                'contact': 'sb@sth.edu',
            },
            {
                'slug': 'event1',
                'start': '1993-08-28',
                'end': '1993-08-29',
                'humandate': 'Aug 28-29, 1993',
                'latitude': 3,
                'longitude': -2,
                'venue': 'University',
                'address': 'On the street',
                'country': 'US',
                'url': 'http://url1/',
                'contact': 'sb@sth.edu',
            },
        ]

    def test_serialization(self):
        # test calling the view directly, with "fake" request object (None)
        view = self.view()
        response = view.get(None)
        self.assertEqual(response.data, self.expecting)

    def test_view(self):
        # test only JSON output
        url = reverse(self.url)
        response = self.client.get(url, format='json')
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(content), self.expecting)
