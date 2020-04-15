# !/usr/bin/env python
# encoding=UTF-8
import boto3
import datetime, time
import io
from PIL import Image

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
    print("the endpoint is:")
    print(endpoint)

    client = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
    try:
        url = client.get_hls_streaming_session_url(
        StreamName=STREAM_NAME,
        PlaybackMode="LIVE"
    )['HLSStreamingSessionURL']
    except Exception:
        print('未找到实时视频流') #如果不是实时视频，这里会报错，但是可以得到endpoint地址，如果报错ResourceNotFoundException就提示没有视频流
        pass
    else:
        return url

#获得HLS协议的endpoint的地址，这里是获得归档流的地址
def getarchivevideourl(STREAM_NAME,howmanyhoursago):
    kvs = boto3.client("kinesisvideo")
    endpoint = kvs.get_data_endpoint(
        APIName="GET_HLS_STREAMING_SESSION_URL",
        StreamName=STREAM_NAME
    )['DataEndpoint']
    print("the archive video url is", endpoint)
    client = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
    try:
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
    except Exception:
        print('未找到归档视频流')  # 如果不是实时视频，这里会报错，但是可以得到endpoint地址，如果报错ResourceNotFoundException就提示没有视频流
        pass
    else:
        return url


#定义在kvs里面的流的名字
STREAM_NAME = "kvs1"


#得到当前用户所有kinesis video stream的信息
getstreaminfo()

#得到当前正在直播的视频流链接，token的默认期为5分钟

url=getlivevideourl(STREAM_NAME)
print(url)


#得到过去几个小时的视频流链接，token的默认器为5分钟，传入的第二个参数为几个小时前
url=getarchivevideourl(STREAM_NAME, 3)
print(url)



#调用ipython显示画面，但有时候显示不出来，或者通过上一步得到的地址在safari浏览器播放
if url:

    from IPython.display import HTML
    HTML(data='<video src="{0}" autoplay="autoplay" controls="controls" width="300" height="400"></video>'.format(url))
else:
    print("未找到视频流")





#下面演示如何用rekognition识别从kvs视频流得到的人脸
#需要先创建好一个stream processor，这个动作目前只能用api来创建，如下示例
#定义好input是kvs，output是kds，然后定义已经识别的人员id，定义匹配程度为85%就认为是这个人
#默认只能创建一个，超出限制会报错
def create_stream_processor()
    client = boto3.client('rekognition')
    response = client.create_stream_processor(
        Input={
            'KinesisVideoStream': {
                'Arn': 'arn:aws:kinesisvideo:us-east-1:201247618887:stream/kvs1/1557896017573'
            }
        },
        Output={
            'KinesisDataStream': {
                'Arn': 'arn:aws:kinesis:us-east-1:201247618887:stream/kds1'
            }
        },
        Name='wangyucam',
        Settings={
            'FaceSearch': {
                'CollectionId': 'wangyu',
                'FaceMatchThreshold': 85.0
            }
        },
        RoleArn='arn:aws:iam::201247618887:role/rekrole'
    )
    print(response)


#rekognition也可以对照片进行识别，把文件放在S3中，指定最大识别的人脸数目，并设定匹配程度
#以下是输出模板,能够识别出大致的年龄区间
'''
Matching faces
FaceId:2ed791ca-c790-45b0-912e-cab7f3a8c7ae
Similarity: 99.30%


Image information: 
wangyu.jpeg
Image Height: 1440
Image Width: 1080
Detected faces for wangyu.jpeg
Face:
No estimated orientation. Check Exif data
The detected face is estimated to be between 23 and 35 years
'''


bucket = 'rekognition-video-console-demo-iad-wangyu'
collectionId = 'wangyu'
fileName = 'wangyu.jpeg'
threshold = 70
maxFaces = 2

client = boto3.client('rekognition')


response = client.search_faces_by_image(CollectionId=collectionId,
                                        Image={'S3Object': {'Bucket': bucket, 'Name': fileName}},
                                        FaceMatchThreshold=threshold,
                                        MaxFaces=maxFaces)

faceMatches = response['FaceMatches']
print('Matching faces')
for match in faceMatches:
    print('FaceId:' + match['Face']['FaceId'])
    print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
    print("\n")


# 识别照片向量
def ShowBoundingBoxPositions(imageHeight, imageWidth, box, rotation):
    left = 0
    top = 0

    if rotation == 'ROTATE_0':
        left = imageWidth * box['Left']
        top = imageHeight * box['Top']

    if rotation == 'ROTATE_90':
        left = imageHeight * (1 - (box['Top'] + box['Height']))
        top = imageWidth * box['Left']

    if rotation == 'ROTATE_180':
        left = imageWidth - (imageWidth * (box['Left'] + box['Width']))
        top = imageHeight * (1 - (box['Top'] + box['Height']))

    if rotation == 'ROTATE_270':
        left = imageHeight * box['Top']
        top = imageWidth * (1 - box['Left'] - box['Width'])

    print('Left: ' + '{0:.0f}'.format(left))
    print('Top: ' + '{0:.0f}'.format(top))
    print('Face Width: ' + "{0:.0f}".format(imageWidth * box['Width']))
    print('Face Height: ' + "{0:.0f}".format(imageHeight * box['Height']))

if __name__ == "__main__":
    photo = 'wangyu.jpeg'
    client = boto3.client('rekognition')

    # 得到照片的分辨率
    image = Image.open(open(photo, 'rb'))
    width, height = image.size

    print('Image information: ')
    print(photo)
    print('Image Height: ' + str(height))
    print('Image Width: ' + str(width))

    # 使用rekognition的detect_faces方法来识别人脸特征
    stream = io.BytesIO()
    if 'exif' in image.info:
        exif = image.info['exif']
        image.save(stream, format=image.format, exif=exif)
    else:
        image.save(stream, format=image.format)
    image_binary = stream.getvalue()

    response = client.detect_faces(Image={'Bytes': image_binary}, Attributes=['ALL'])

    print('Detected faces for ' + photo)
    for faceDetail in response['FaceDetails']:
        print('Face:')
        if 'OrientationCorrection' in response:
            print('Orientation: ' + response['OrientationCorrection'])
            ShowBoundingBoxPositions(height, width, faceDetail['BoundingBox'], response['OrientationCorrection'])

        else:
            print('No estimated orientation. Check Exif data')

        print('The detected face is estimated to be between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years')
        print(str(faceDetail))
