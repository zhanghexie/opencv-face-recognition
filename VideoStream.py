from Setting import Setting
import threading
import cv2
import time
import os


class VideoStream:

    # 初始化
    def __init__(self, src, resolution=(820, 480)):
        self.stopped = False
        self.closed = False
        self.last_image = None
        self.run_thread = True
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        (self.grabbed, self.frame) = self.stream.read()
        self.thread = threading.Thread(target=self.video_loop)

    # 视频流
    def video_loop(self):
        while self.closed == False:
            (self.grabbed, self.frame) = self.stream.read()
            time.sleep(1/30)
        self.stream.release()

    # 启动视频流线程
    def run(self):
        self.thread.start()

    # 读取视频流帧
    def read(self):
        if self.stopped:
            return self.grabbed, self.last_image
        self.last_image = self.frame
        return self.grabbed, self.frame

    # 暂停视频流
    def stop(self):
        self.stopped = True

    # 恢复视频流
    def go_on(self):
        self.stopped = False

    # 关闭视频流
    def close(self):
        self.stopped = True
        self.closed = True

    # 获取视频源列表
    def get_sources(self):
        source_list = [0]
        vedio_Paths = [os.path.join(Setting().vedio_path, f)
                       for f in os.listdir(Setting().vedio_path)]
        for vedio_Path in vedio_Paths:
            if os.path.split(vedio_Path)[-1].split('.')[-1] in ['avi','mp4']:
                source_list.append(vedio_Path)
        return source_list
