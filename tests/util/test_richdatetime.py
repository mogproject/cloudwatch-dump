import unittest
from cloudwatchdump.util import RichDateTime
import pytz
import time
from datetime import datetime, timedelta
from dateutil.tz import tzlocal


class TestRichDateTime(unittest.TestCase):
    def setUp(self):
        naive = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.utc = pytz.utc
        self.jst = pytz.timezone('Asia/Tokyo').localize(naive).tzinfo
        self.pst = pytz.timezone('US/Pacific').localize(naive).tzinfo
        self.local_to_utc = timedelta(seconds=time.timezone)

    def test_new_with_empty_args(self):
        self.assertRaises(TypeError, lambda: RichDateTime())

    def test_new_without_tzinfo(self):
        self.assertRaises(ValueError, lambda: RichDateTime(2000))

    def test_new_without_month(self):
        self.assertRaises(TypeError, lambda: RichDateTime(2000, tzinfo=self.utc))

    def test_new_without_day(self):
        self.assertRaises(TypeError, lambda: RichDateTime(2000, 12, tzinfo=self.utc))

    def test_new_with_illegal_date(self):
        self.assertRaises(ValueError, lambda: RichDateTime(2000, 12, 32, tzinfo=self.utc))

    def test_new_date_only(self):
        dt = RichDateTime(2000, 12, 31, tzinfo=self.utc)
        self.assertEqual(dt, datetime(2000, 12, 31, 0, 0, 0, 0, self.utc))

    def test_new_date_with_time(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, 890, self.utc))

    def test_new_with_localtime(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=tzlocal())
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, 890, tzlocal()))

    def test_new_with_specified_timezone(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.jst)
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, 890, self.jst))

    def test_epoch_with_utc(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt.epoch(), 978238567)

    def test_epoch_with_localtime(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=tzlocal())
        self.assertEqual(dt.epoch(), 978238567)

    def test_epoch_with_specified_timezone(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.jst)
        self.assertEqual(dt.epoch(), 978238567)

    def test_set_local_with_utc(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt.to_local(), datetime(2000, 12, 31, 4, 56, 7, 890, tzlocal()) - self.local_to_utc)

    def test_set_local_with_localtime(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=tzlocal())
        self.assertEqual(dt.to_local(), datetime(2000, 12, 31, 4, 56, 7, 890, tzlocal()))

    def test_set_local_with_specified_timezone(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.pst)
        offset = self.pst.utcoffset(datetime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.pst))
        self.assertEqual(dt.to_local(), datetime(2000, 12, 31, 4, 56, 7, 890, tzlocal()) - offset - self.local_to_utc)

    def test_mod_by_illegal_type(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertRaises(TypeError, lambda: dt % 0)

    def test_mod_by_zero(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertRaises(ValueError, lambda: dt % timedelta(0))

    def test_mod_by_minus(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertRaises(ValueError, lambda: dt % timedelta(seconds=-1))

    def test_mod_by_minimum(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt % timedelta(seconds=1), datetime(2000, 12, 31, 4, 56, 7, tzinfo=self.utc))

    def test_mod_by_day(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt % timedelta(days=1), datetime(2000, 12, 31, 0, 0, 0, tzinfo=self.utc))

    def test_mod_by_hour(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt % timedelta(hours=1), datetime(2000, 12, 31, 4, 0, 0, tzinfo=self.utc))

    def test_mod_by_five_min(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt % timedelta(minutes=5), datetime(2000, 12, 31, 4, 55, 0, tzinfo=self.utc))

    def test_mod_by_prime(self):
        dt = RichDateTime(2000, 12, 31, 4, 56, 7, 890, tzinfo=self.utc)
        self.assertEqual(dt % timedelta(minutes=7), datetime(2000, 12, 31, 4, 53, 0, tzinfo=self.utc))

    def test_from_datetime_naive_to_naive(self):
        dt = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.assertRaises(ValueError, lambda: RichDateTime.from_datetime(dt))

    def test_from_datetime_naive_to_local(self):
        dt = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.assertEqual(RichDateTime.from_datetime(dt, tzlocal()), datetime(2000, 12, 31, 4, 56, 7, 890, tzlocal()))

    def test_from_datetime_naive_to_utc(self):
        dt = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.assertEqual(RichDateTime.from_datetime(dt, self.utc), datetime(2000, 12, 31, 4, 56, 7, 890, self.utc))

    def test_from_datetime_naive_to_specified_timezone(self):
        dt = datetime(2000, 12, 31, 4, 56, 7, 890)
        self.assertEqual(RichDateTime.from_datetime(dt, self.jst), datetime(2000, 12, 31, 4, 56, 7, 890, self.jst))
        self.assertEqual(RichDateTime.from_datetime(dt, self.pst), datetime(2000, 12, 31, 4, 56, 7, 890, self.pst))

    def test_from_datetime_aware_without_change(self):
        for tz in [tzlocal(), self.utc, self.jst, self.pst]:
            dt = datetime(2000, 12, 31, 4, 56, 7, 890, tz)
            rtd = RichDateTime.from_datetime(dt)
            self.assertEqual(rtd, dt)
            self.assertEqual(rtd.tzinfo, tz)

    def test_from_datetime_aware_with_change(self):
        tz = [tzlocal(), self.utc, self.jst, self.pst]
        for tz1, tz2 in ((tz1, tz2) for tz1 in tz for tz2 in tz):
            dt = datetime(2000, 12, 31, 4, 56, 7, 890, tz1)
            rtd = RichDateTime.from_datetime(dt, tz2)
            self.assertEqual(rtd, dt)
            self.assertEqual(rtd.tzinfo, tz2)

    def test_now_without_tzinfo(self):
        dt = RichDateTime.now()
        self.assertEqual(dt.tzinfo, tzlocal())
        self.assertTrue(dt <= datetime.now(tzlocal()))

    def test_now_with_tzinfo(self):
        dt = RichDateTime.now(self.utc)
        self.assertEqual(dt.tzinfo, self.utc)
        self.assertTrue(dt <= datetime.now(tzlocal()))

    def test_strptime_without_tzinfo(self):
        dt = RichDateTime.strptime('20001231045607', '%Y%m%d%H%M%S')
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, tzinfo=tzlocal()))
        self.assertEqual(dt.tzinfo, tzlocal())

    def test_strptime_with_utc(self):
        dt = RichDateTime.strptime('20001231045607', '%Y%m%d%H%M%S', self.utc)
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, tzinfo=self.utc))
        self.assertEqual(dt.tzinfo, self.utc)

    def test_strptime_with_specified_timezone(self):
        dt = RichDateTime.strptime('20001231045607', '%Y%m%d%H%M%S', self.jst)
        self.assertEqual(dt, datetime(2000, 12, 31, 4, 56, 7, tzinfo=self.jst))
        self.assertEqual(dt.tzinfo, self.jst)
