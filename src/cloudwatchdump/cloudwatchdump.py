#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
import pytz
from boto.ec2 import cloudwatch
from util import RichDateTime


def get_time_range(time_str, interval):
    """
    Returns pair of RichDateTime.
    """
    d = timedelta(minutes=interval)
    if time_str:
        # parse string as localtime
        t = RichDateTime.strptime(time_str, '%Y%m%d%H%M')
    else:
        # get current time in localtime
        t = (RichDateTime.now() % d) - d
    return (t, t + d)


def get_metrics(region):
    """
    Get all metrics in specified region.
    """
    client = cloudwatch.connect_to_region(region)
    if not client:
        raise Exception('Failed to connect to region: %s' % region)
    buf = []
    next_token = None
    while True:
        if next_token:
            result = client.list_metrics(next_token=next_token)
        else:
            result = client.list_metrics()
        buf += list(result)
        if not result.next_token:
            break
        next_token = result.next_token
    return buf


def metric_to_tag(metric, statistics):
    """
    Create tag string from metric and statistics.
    """
    buf = []
    buf.append(metric.connection.region.name)
    buf.append(statistics)
    buf += metric.namespace.split('/')
    for x in sorted(metric.dimensions.items()):
        # replace slash for whisper safety
        buf += ('root' if s == '/' else s.replace('/', '_') for s in x[1])
    buf.append(metric.name)
    return '.'.join(buf)


def get_metric_statistics(metric, start_time, end_time, statistics, unit, period):
    """
    Execute CloudWatch API to fetch statistics data.
    """
    datapoints = metric.query(start_time, end_time, statistics, unit, period)

    def f(datapoint):
        # read timestamp as UTC
        t = RichDateTime.from_datetime(datapoint['Timestamp'], pytz.utc)
        return (metric, statistics, datapoint[statistics], t)

    return map(f, datapoints)


def get_data(metrics, statistics_list, start, end, period_in_min):
    """
    Get summerized CloudWatch metric status,
    then generate tuples of metric, statistics, value, and timestamp in UTC.
    """
    p = timedelta(minutes=period_in_min)

    params = ((m, start, end, s, None, p.seconds) for m in metrics for s in statistics_list)
    return (data for param in params for data in get_metric_statistics(*param))


def print_data(data):
    """
    Output value of one datapoint.
    Timestamp is converted to localtime.
    """
    m, s, v, t = data
    print('%s %.10f %d' % (metric_to_tag(m, s), v, t.to_local().epoch()))


def parse_args():
    """
    Parse command line arguments
    """
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        '--region', dest='region', default='us-east-1', type='string',
        help='the name of the region to connect to'
    )
    parser.add_option(
        '--time', dest='time', default=None, type='string',
        help='start time of the query in format "YYYYMMDDhhmm" localtime'
    )
    parser.add_option(
        '--interval', dest='interval', default=60, type='int',
        help='minites of time range in the query'
    )
    parser.add_option(
        '--period', dest='period', default=5, type='int',
        help='minites to aggregate in the query'
    )
    parser.add_option(
        '--check', action='store_true', dest='check', default=False,
        help='prints only the metrics and its statistics methods'
    )
    return parser.parse_args()


def main():
    """
    Main function
    """
    statistics_list = ['Average', 'Sum']

    # get command line arguments
    options, args = parse_args()

    # calculate time range
    start, end = get_time_range(options.time, options.interval)

    # get metrics list
    metrics = get_metrics(options.region)
    query_params = ((m, s) for m in metrics for s in statistics_list)

    if options.check:
        # print all query params when check mode
        print('start : %s' % start)
        print('end   : %s' % end)
        print('period: %s min' % options.period)
        for q in query_params:
            print('will collect metric: %s' % (metric_to_tag(q[0], q[1])))
    else:
        # fetch and print metrics statistics
        for data in get_data(metrics, statistics_list, start, end, options.period):
            print_data(data)


if __name__ == '__main__':
    main()
