
import cv2
import os
import numpy as np
import pickle as pk
from Setting import Setting
import requests
import threading
import time
 


class FaceTools:

    # 初始化函数
    def __init__(self):
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            grid_x=16, grid_y=16)
        self.face_recognizer.read(Setting().train_result_path)
        self.face_detector = cv2.CascadeClassifier(
            Setting().face_classification_file_path)
        self.eyes_detector = cv2.CascadeClassifier(
            Setting().eyes_classification_file_path)
        self.predict_number = 0
        self.number = 0
        self.face_id = None
        self.usrs_dict = None
        self.open_dict()
        self.predict_dict = {}
        # 加载人脸姓名和编号对应字典

    # 1人脸检测，会标记并返回检测到的所有人脸
    def face_detection(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.2, 5)
        eyes = self.eyes_detector.detectMultiScale(gray, 1.2, 5)
        max_face = self.max_matrix(faces)
        max_eye = self.max_matrix(eyes)
        self.plot_rectangle(img, max_face)
        self.plot_rectangle(img, max_eye)
        return img

    # 2收集人脸，只会标记并返回检测到的最大的人脸
    def face_collect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.2, 8)
        max_face = self.max_matrix(faces)
        self.plot_rectangle(img, max_face)
        return img, max_face

    # 3保存人脸图片，
    def face_save(self, img, max_face):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if max_face[2] > 30:
            self.number += 1
            print(self.number)
            print(Setting().face_image_path + "/people." +
                  str(int(self.face_id)) + '.' + str(self.number) + ".jpg")
            cv2.imwrite(Setting().face_image_path + "/people." + str(int(self.face_id)) + '.' + str(self.number) +
                        ".jpg", gray[max_face[1]:max_face[1]+max_face[3], max_face[0]:max_face[0]+max_face[2]])
        return

    # 4传入识别器，训练并保存结果，返回可识别的人脸个数
    def face_train(self):
        thread = threading.Thread(target=self.face_train_thread)
        thread.start()

    def face_train_thread(self):
        img_Paths = [os.path.join(Setting().face_image_path, f)
                     for f in os.listdir(Setting().face_image_path)]
        faces = []
        ids = []
        for img_Path in img_Paths:
            img = cv2.imread(img_Path, cv2.IMREAD_GRAYSCALE)
            img_numpy = np.array(img, 'uint8')
            user_id = os.path.split(img_Path)[-1].split('.')[1]
            if user_id in self.usrs_dict.keys():
                user_id = int(user_id)
                faces.append(img_numpy)
                ids.append(user_id)
        before = time.time()
        self.face_recognizer.train(np.array(faces), np.array(ids))
        print('训练时间：' + str(time.time()-before))
        self.face_recognizer.write(Setting().train_result_path)
        print('写入时间：' + str(time.time()-before))
        print("\n【通知】训练完成。请继续在此进行您的输入：")
        return

    # 5人脸识别,在识别出的人脸上添加姓名
    def face_recognize(self, img):
        user_id = 0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
        for(x, y, w, h) in faces:
            before = time.time()
            user_id, accuracy = self.face_recognizer.predict(
                gray[y:y+h, x:x+w])
            if (accuracy < 500):
                name = self.usrs_dict[str(user_id)]
                # accuracy = "{0}".format(round(accuracy))
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                start = ''
                if accuracy <= 300:
                    start = '*****'
                elif accuracy <= 350:
                    start = '****'
                elif accuracy <= 400:
                    start = '***'
                elif accuracy <= 450:
                    start = '**'
                else:
                    start = '*'
                print('\r识别张数：'+str(self.predict_number)+'\t\t识别时间：' + str(time.time()-before),end = '')
                cv2.putText(img, str(name), (x+10, y-10),
                            cv2.FONT_ITALIC, 1, (255, 255, 255), 2)
                cv2.putText(img, start, (x+10, y+h-10),
                            cv2.FONT_ITALIC, 1, (255, 255, 0), 1)
                if user_id in self.predict_dict.keys():
                    self.predict_dict[user_id]+=1
                else:
                    self.predict_dict[user_id]=1
                self.predict_number+=1
                if self.predict_number == 800:
                    self.predict_number = 0
                    print('\n'+str(self.predict_dict)+'\n')
            if user_id == 1 and accuracy >= 350:
                user_id = 0
        return str(user_id), img

    # 6给管理员微信发消息
    def sent_message(self, text, desp):
        api = "https://sc.ftqq.com/SCU49966T86fbbaab6ea4aa743daa86f0fb0749695cc3ab663ce4a.send"
        # 1 添加新用户
        # 2 管理员登陆
        data = {
            "text": text,
            "desp": desp
        }
        requests.post(api, data=data)

    # 找出面积最大的矩形
    def max_matrix(self, matrixs):
        max_matrix = [0, 0, 0, 0]
        for [x, y, w, h] in matrixs:
            if w*h >= max_matrix[2]*max_matrix[3]:
                max_matrix = [x, y, w, h]
        return max_matrix

    # 给图片绘制矩形
    def plot_rectangle(self, img, matrix):
        cv2.rectangle(img, (matrix[0], matrix[1]), (matrix[0] +
                                                    matrix[2], matrix[1]+matrix[3]), (255, 0, 0), 2)

    # 字典转字符串
    def dict_str(self):
        message = ''
        for key, value in self.usrs_dict.items():
            message = message+"0"*(6-len(key))+key+":   "+value + "\n"
        return message

    # 加载用户字典
    def open_dict(self):
        try:
            with open(Setting().usrs_info_path, 'rb') as usr_file:
                self.usrs_dict = pk.load(usr_file)
        except FileNotFoundError:
            with open(Setting().usrs_info_path, 'wb') as usr_file:
                self.usrs_dict = {'1': 'ZhngHexuan', '3': "RenTianyi"}
                pk.dump(self.usrs_dict, usr_file)
        usr_file.close()

    # 保存用户字典
    def save_dict(self):
        try:
            with open(Setting().usrs_info_path, 'wb') as usr_file:
                    pk.dump(self.usrs_dict, usr_file)
        except FileNotFoundError:
            print("出现错误")
            usr_file.close()

# print("jieshu")
# while True:
#     pass
# cam = cv2.VideoCapture(0) # 初始化摄像头
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 设置视频宽度
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 设置视频高度
# _,img = cam.read()
# img = ft.face_recognize(img)
# cv2.imshow("image",img)
# cv2.waitKey(0)
