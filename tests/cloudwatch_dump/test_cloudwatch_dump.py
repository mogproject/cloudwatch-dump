import unittest
import pytz
import time
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from cloudwatch_dump.cloudwatch_dump import get_time_range
from cloudwatch_dump.util import RichDateTime


class TestCloudwatchDump(unittest.TestCase):
    def setUp(self):
        self.naive = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.utc = pytz.utc
        self.jst = pytz.timezone('Asia/Tokyo').localize(self.naive).tzinfo
        self.pst = pytz.timezone('US/Pacific').localize(self.naive).tzinfo
        self.local_to_utc = timedelta(seconds=time.timezone)

    def test_get_time_range_with_time_str(self):
        start = RichDateTime(2000, 12, 31, 4, 56, 0, 0, tzinfo=tzlocal())
        self.assertEqual(get_time_range('200012310456', 0), (start, start))

        self.assertEqual(get_time_range('200012310456', 5),
                         (start, RichDateTime(2000, 12, 31, 5, 1, 0, 0, tzinfo=tzlocal())))

        self.assertEqual(get_time_range('200012310456', 60),
                         (start, RichDateTime(2000, 12, 31, 5, 56, 0, 0, tzinfo=tzlocal())))

        self.assertEqual(get_time_range('200012310456', 1440),
                         (start, RichDateTime(2001, 1, 1, 4, 56, 0, 0, tzinfo=tzlocal())))

    def test_get_time_range_without_time_str_and_zero_interval(self):
        self.assertRaises(ValueError, lambda: get_time_range(None, 0))

    def test_get_time_range_without_time_str(self):
        x, y = get_time_range(None, 1440)
        self.assertEqual(x.hour, 0)
        self.assertEqual(x.minute, 0)
        self.assertEqual(x.second, 0)
        self.assertEqual(x.microsecond, 0)
        self.assertEqual(x.tzinfo, tzlocal())
        self.assertEqual(y.hour, 0)
        self.assertEqual(y.minute, 0)
        self.assertEqual(y.second, 0)
        self.assertEqual(y.microsecond, 0)
        self.assertEqual(y.tzinfo, tzlocal())
        self.assertEqual(y - x, timedelta(days=1))

        a, b = get_time_range(None, 5)
        self.assertEqual(a.minute % 5, 0)
        self.assertEqual(b.minute % 5, 0)
        self.assertEqual(b - a, timedelta(minutes=5))
