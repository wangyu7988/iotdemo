import boto3
import datetime, time


#显示几个小时之前的时间戳，用于获得kvs片段
def hoursago(howmanyhours):

    hoursago = (datetime.datetime.now() - datetime.timedelta(hours = howmanyhours))
    timeStamp = int(time.mktime(hoursago.timetuple()))

    return timeStamp

#获得视频流的信息，主要获得视频流endpoint的地址
def getstreaminfo():
    kvs = boto3.client("kinesisvideo")
    response = kvs.list_streams()

    for i in range(len(response['StreamInfoList'])):

      streaminfo = response['StreamInfoList'][i]
      for key,value in streaminfo.items():
         print(key,':',value)
      streamname = streaminfo['StreamName']
      datapointinfo = kvs.get_data_endpoint(StreamName=streamname, APIName='GET_MEDIA')
      datapoint = datapointinfo['DataEndpoint']
      print(datapoint)

#获得HLS协议的endpoint的地址，这里是获得实时流的地址
def getlivevideourl(STREAM_NAME):
    kvs = boto3.client("kinesisvideo")
    endpoint = kvs.get_data_endpoint(
        APIName="GET_HLS_STREAMING_SESSION_URL",
        StreamName=STREAM_NAME
    )['DataEndpoint']
    client = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)

    url = client.get_hls_streaming_session_url(
        StreamName=STREAM_NAME,
        PlaybackMode="LIVE"
    )['HLSStreamingSessionURL']

    return url

#获得HLS协议的endpoint的地址，这里是获得归档流的地址
def getarchivevideourl(STREAM_NAME,howmanyhoursago):
    kvs = boto3.client("kinesisvideo")
    endpoint = kvs.get_data_endpoint(
        APIName="GET_HLS_STREAMING_SESSION_URL",
        StreamName=STREAM_NAME
    )['DataEndpoint']
    client = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)

    url = client.get_hls_streaming_session_url(
          StreamName=STREAM_NAME,
          PlaybackMode = 'ON_DEMAND',
          HLSFragmentSelector={
          'FragmentSelectorType': 'PRODUCER_TIMESTAMP',
          'TimestampRange': {
          'StartTimestamp': hoursago(howmanyhoursago),
          'EndTimestamp': hoursago(0)
           }
          }
          )['HLSStreamingSessionURL']
    return url


#定义在kvs里面的流的名字
STREAM_NAME = "kvs1"


#得到当前用户所有kinesis video stream的信息
getstreaminfo()

#得到当前正在直播的视频流链接，token的默认期为5分钟

print(getlivevideourl(STREAM_NAME))


#得到过去几个小时的视频流链接，token的默认器为5分钟，传入的第二个参数为几个小时前
print(getarchivevideourl(STREAM_NAME, 3))



#调用ipython显示画面，但有时候显示不出来，或者通过上一步得到的地址在safari浏览器播放
from IPython.display import HTML
HTML(data='<video src="{0}" autoplay="autoplay" controls="controls" width="300" height="400"></video>'.format(url))



