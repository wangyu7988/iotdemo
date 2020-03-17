**AWS iot CN 是适用于Arduino平台的示例代码，使用Arduino开发板，按照注释进行配置：**
1. 填入对应的wifi信息，以及iot endpoint地址
2. 填入在aws iot平台创建的事物名字，以及创建事物时下载的key的信息，请严格按照注释说明的格式
3. 指定led对应针脚，不同品牌的开发板针脚不一样，请参考开发板说明

在aws iot平台端利用自带的测试工具发送给对应事物的影子信息，比如想亮灯，就将led状态改成1，如下实例：
iotdemo是模拟创建的事物名字

订阅的主题是：$aws/things/iotdemo/shadow/update
发送的内容是：{"state": {"desired": {"led":1}}}

附aws iot vlog，可以参考视频教材
https://mp.weixin.qq.com/s/dHk3-zoL0187yRCnt_6jyg


**kvs.py 是用于演示使用aws kinesis video stream的实例代码，用于模拟将视频流传输到云端并获取播放地址的过程**
1. 首先需要在aws端创建一个stream，示例中用kvs1来表示
2. 需要具备将视频流传输到云端的设备，官方提供了一些创建者库，可以参考https://docs.aws.amazon.com/zh_cn/kinesisvideostreams/latest/dg/producer-sdk-cpp.html
3. 视频流传输之后，可以通过示例代码中的方法获取视频信息

