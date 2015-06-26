cloudwatch-dump
===============

Just dump all the CloudWatch metrics.

[![Build Status](https://travis-ci.org/mogproject/cloudwatch-dump.svg?branch=master)](https://travis-ci.org/mogproject/cloudwatch-dump)
[![Coverage Status](https://img.shields.io/coveralls/mogproject/cloudwatch-dump.svg)](https://coveralls.io/r/mogproject/cloudwatch-dump?branch=master)
[![Stories in Ready](https://badge.waffle.io/mogproject/cloudwatch-dump.svg?label=ready&title=Ready)](http://waffle.io/mogproject/cloudwatch-dump) 

### This script does ...

1. Get complete metrics list from [AWS CloudWatch](http://aws.amazon.com/cloudwatch/?nc2=h_ls) in the specified region.
1. For all metrics, fetch ```Average``` and ```Sum``` values for each period within the specified interval.
1. Print metric path, value and timestamp in **[Graphtie](http://graphite.readthedocs.org/en/latest/)-friendly** format

### Dependencies

- Python >= 2.6
- pytz
- python-dateutil
- boto


### Installation

```
pip install git+https://github.com/mogproject/cloudwatch-dump
```

You may need ```sudo``` command.

Then, setup your credentials for reading CloudWatch data.

- Create boto credentials (e.g. ```~/.boto```)
- or set environment variable (```AWS_ACCESS_KEY_ID```, ```AWS_SECRET_ACCESS_KEY```)
- see further for [Boto configuration tutorial](https://boto.readthedocs.org/en/latest/boto_config_tut.html)


### Usage


```
Usage: cloudwatch-dump [options]

Options:
  -h, --help           show this help message and exit
  --region=REGION      the name of the region to connect to (default: us-east-1)
  --time=TIME          start time of the query in format "YYYYMMDDhhmm" localtime
                       (default: calculated by now)
  --interval=INTERVAL  minites of time range in the query (default: 60)
  --period=PERIOD      minites to aggregate in the query (default: 5)
  --check              prints only the metrics and its statistics methods (default: false)
```


### Example

##### 1. ```cloudwatch-dump```

Without arguments, ths script will print all metrics status with the following options.

- region: us-east-1
- time range: last one hour  
 (e.g. if current time is 09:23:45, will be 08:00:00 - 09:00:00)
- aggregation period: 5 minutes
    
Output will look like the following.
    
```
us-east-1.Average.AWS.EC2.i-01234567.NetworkOut 1048.6000000000 1414801800
us-east-1.Average.AWS.EC2.i-01234567.NetworkOut 1053.6000000000 1414802100
us-east-1.Average.AWS.EC2.i-01234567.NetworkOut 1069.0000000000 1414800900
us-east-1.Sum.System.Linux._dev_xvda1.i-01234567.root.DiskSpaceUtilization 35.9955154058 1414802700
us-east-1.Sum.System.Linux._dev_xvda1.i-01234567.root.DiskSpaceUtilization 35.9954661679 1414801500
us-east-1.Sum.System.Linux._dev_xvda1.i-01234567.root.DiskSpaceUtilization 35.9952199780 1414800600
...
```

Note that output is NOT sorted by timestamp.

##### 2. ```cloudwatch-dump --check```

list all the metric names in us-east-1 region.

- Will not fetch actual data from CloudWatch.
    
Output will look like the following.
   
```
start : 2014-11-01 00:00:00+09:00
end   : 2014-11-01 01:00:00+09:00
period: 5 min
will collect metric: us-east-1.Average.AWS.SNS.NotifyMe.PublishSize
will collect metric: us-east-1.Sum.AWS.SNS.NotifyMe.PublishSize
will collect metric: us-east-1.Average.AWS.SNS.NotifyMe.NumberOfMessagesPublished
will collect metric: us-east-1.Sum.AWS.SNS.NotifyMe.NumberOfMessagesPublished
will collect metric: us-east-1.Average.AWS.SNS.NotifyMe.NumberOfNotificationsDelivered
will collect metric: us-east-1.Sum.AWS.SNS.NotifyMe.NumberOfNotificationsDelivered
...
```

##### 3. ```cloudwatch-dump --region us-east-1 --time 201410100000 --interval 1440```

   Fetch whole data on October 10th 2014 (localtime) in ap-northeast-1 region aggregated by 5 minutes.

##### 4. ```cloudwatch-dump --period 1```

   Fetch last one-hour's data aggregated by 1 minute.
  
##### 5. ```cloudwatch-dump -h```

   Prints help message.


### Notes

##### Metric path

Metric path is built as follows.

<pre>region.statistics.namespace[.namespace...][.dimensionValue[.dimensionValue...]].metricName</pre>

- "/" in namespace will be replaced to "."
- "/" in dimension value will be replace to "_" (for Graphite(Whisper) safety) 
- If dimension value equals "/", it will be replaced to "root"
- Dimension values are sorted by dimension keys (in dictionary ascending order).

e.g.

In case region="us-east-1", statistics="Average", namespace="AWS/EC2", dimensionValue="i-01234567", metric="CPUUtilization", metric path will be built as ```us-east-1.Sum.AWS.EC2.i-01234567.CPUUtilization```.

##### Timestamp

Timestamp is represented as epoch time in local timezone.

##### Number of API calls

Note that CloudWatch API call could be [charged](http://aws.amazon.com/cloudwatch/pricing/?nc2=h_ls).

Let's say "n" as the number of metrics in the specified region, the number of total calls will be

- check mode : ```max(1, ceil(n / 500))```
- normal mode: ```max(1, ceil(n / 500)) + 2 * n```

e.g. If ```n = 600```, normal mode consumes ```(2+2*600=) 1,202``` API calls.

*Author of this script shall be irresponsible about the damage under claim for payment under any circumstance.*

##### Execution Timing

Because it takes a time to transfer metrics data from AWS services to CloudWatch, too early execution could cause missing some data.

If the interval is one hour, execution on ```*:01``` would be too early. ```*:05``` is much reasonable for it.  
Or fetch last two hours' data hourly.


### Graphite Integration Example

Shell script example for integrating Graphite (carbon-cache) on localhost, 2003 port.

```
#!/bin/bash

export AWS_ACCESS_KEY_ID="XXXXXX"
export AWS_SECRET_ACCESS_KEY="XXXXXX"

for region in us-east-1 ap-northeast-1; do
  # replace your EC2 instance name to nickname
  cloudwatch-dump $region |
  sed -e '
    s/i-XXXXXXXX/server-1/g
    s/i-YYYYYYYY/server-2/g
    s/i-ZZZZZZZZ/server-3/g' |
  nc localhost 2003
done
```


### Uninstallation

```
pip uninstall cloudwatch-dump
```
