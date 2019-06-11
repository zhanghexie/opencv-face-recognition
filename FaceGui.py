"""
添加功能
# 大升级
# 后台管理系统
# 微信推送服务
# 加载视频
# 多线程提速画面，发消息，训练模型
1，管理员后台管理
2，计数功能
"""
from Setting import Setting
from VideoStream import VideoStream
from FaceTools import FaceTools as ft
from PIL import Image, ImageTk
import pickle as pk
import tkinter.messagebox
import tkinter as tk
import threading
import time
import gc as gc
import cv2
import os


class Face_App:

    # 初始化函数
    def __init__(self):
        self.face_tools = ft()
        self.vs = VideoStream(0)
        self.vs.run()
        self.frame = None
        self.thread = None
        self.guanliyuan_accept_login = True
        self.run_manage = False
        self.change_list = self.vs.get_sources()
        self.source_number = 0
        self.update_label_flag = True

        # 主界面
        self.root = tk.Tk()
        self.root.wm_resizable(False, False)  # 使窗口尺寸不变
        self.root.wm_title("基于机器视觉的人脸识别系统")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.close)

        # 人脸画面
        self.face_image = tk.Label()
        self.face_image.pack(side="top", padx=10, pady=10)

        # 添加人脸按钮相关
        self.add_button_var = tk.StringVar()
        self.add_button_var.set("添加人脸")
        self.press_add = False
        self.add_button = tk.Button(
            self.root, textvariable=self.add_button_var, command=self.add)

        # 切换源按钮相关
        self.is_vedio_source = True
        self.change_source_var = tk.StringVar()
        self.change_source_var.set("切换图像")
        self.press_change_source = False
        self.change_source_button = tk.Button(
            self.root, textvariable=self.change_source_var, command=self.change_source)

        # 人脸识别按钮相关
        self.recognize_button_var = tk.StringVar()
        self.recognize_button_var.set("人脸识别")
        self.press_recognize = False
        self.recognize_button = tk.Button(
            self.root, textvariable=self.recognize_button_var, command=self.recognize)
        self.max_face = []

        # 人脸检测按钮相关
        self.detect_button_var = tk.StringVar()
        self.detect_button_var.set("人脸检测")
        self.press_detect = False
        self.detect_button = tk.Button(
            self.root, textvariable=self.detect_button_var, command=self.detect)

        # 姓名编号输入界面
        self.frame_h = tk.Frame(self.root)
        self.frame_l = tk.Frame(self.root)
        self.name_label = tk.Label(self.frame_h, text="姓名：")
        self.id_label = tk.Label(self.frame_l, text="编号：")
        self.name_entry = tk.Entry(self.frame_h)
        self.id_entry = tk.Entry(self.frame_l)
        self.ok_button = tk.Button(
            self.root, text="确认", width=20, command=self.save_id)

        # 是我按钮
        self.is_me_var = tk.StringVar()
        self.is_me_var.set("是我")
        self.is_me_button = tk.Button(
            self.root, textvariable=self.is_me_var, command=self.is_me)
        self.press_is_me_button = False

        # 不是我按钮
        self.not_me_button = tk.Button(
            self.root, text="不是我", command=self.not_me)
        self.press_not_me_button = False

        # 线程相关
        self.run_thread = True
        self.thread = threading.Thread(target=self.video_loop)
        self.thread.start()
        self.last_img = None
        self.last_max_face = [0, 0, 0, 0]
        self.pack_all_button()
        self.root.mainloop()

    # 视频循环流
    def video_loop(self):
        try:
            print("启动画面")
            while self.run_thread:
                if self.press_change_source:
                    self.change_sources()
                    self.press_change_source = False
                self.grabbed, self.frame = self.vs.read()
                if self.grabbed:
                    self.update_img(self.frame)
                elif self.run_thread == True:
                    self.change_sources()
                else:
                    break
        except RuntimeError:
            print("视频流出现异常")

    # 根据用户所选功能能的不同，将每一帧画面进行不同处理
    def update_img(self, img):
        if self.press_recognize:
            user_id, new_img = self.face_tools.face_recognize(img)
            self.update_label(new_img)
            if user_id == '1' and self.guanliyuan_accept_login == True and self.is_vedio_source == True and self.press_recognize and self.source_number == 0:
                if tk.messagebox.askokcancel(message="你好像是管理员,你要登录吗？"):
                    self.guanliyuan_accept_login = True
                    self.run_manage = True
                    self.run_thread = False
                    tk.messagebox.showinfo(message="请关闭本页面在终端进行操作。")
                else:
                    self.guanliyuan_accept_login = False
        elif self.press_detect:
            new_img = self.face_tools.face_detection(img)
            self.update_label(new_img)
        elif self.press_add:
            if self.update_label_flag:
                new_img, self.max_face = self.face_tools.face_collect(img)
                self.update_label(new_img)
            if self.max_face[2] > 10:
                self.vs.stop()
                self.update_label_flag = False
            if self.press_is_me_button:
                self.press_is_me_button = False
                self.update_label_flag = True
                self.face_tools.face_save(img, self.max_face)
                self.is_me_var.set(
                    "是我" + " (" + str(self.face_tools.number) + ")")
                self.vs.go_on()
            elif self.press_not_me_button:
                self.update_label_flag = True
                self.press_not_me_button = False
                self.vs.go_on()
        else:
            self.update_label(img)

    # 更新显示画面
    def update_label(self, new_img):
        cv2image = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)  # 将图像转换成Image对象
        imgtk = ImageTk.PhotoImage(image=current_image)
        if imgtk == None:
            tk.messagebox.showerror(message="更新画面出现异常请关闭程序。")
            return
        if self.face_image is None:
            self.face_image = tk.Label(image=imgtk)
            self.face_image.image = imgtk
            self.face_image.pack(side="top", padx=10, pady=10)
        else:
            if self.run_thread == False:
                return
            self.face_image.configure(image=imgtk)
            self.face_image.image = imgtk

    # 人脸识别按钮对应程序
    def recognize(self):
        if self.press_recognize == False:
            is_recognize = tk.messagebox.askokcancel(
                title='', message="确定要开始识别吗?")
            if is_recognize:
                self.press_recognize = True
                self.destroy_all_button()
                self.recognize_button_var.set("取消识别")
                self.recognize_button.pack(
                    fill="both", expand="yes", padx=200, pady=10)
                print("识别")
        else:
            is_cancel_recognize = tk.messagebox.askokcancel(
                title='', message="确定要取消识别吗?")
            if is_cancel_recognize:
                print('\n'+str(self.face_tools.predict_dict)+'\n')
                self.face_tools.predict_dict = {}
                self.face_tools.predict_number = 0
                self.press_recognize = False
                self.guanliyuan_accept_login = True
                self.destroy_all_button()
                self.recognize_button_var.set("人脸识别")
                self.pack_all_button()
                print("取消识别")

    # 人脸检测按钮对应程序
    def detect(self):

        if self.press_detect == False:
            is_detect = tk.messagebox.askokcancel(
                title='', message="确定要开始检测吗?")  # return True 0r False
            if is_detect:
                self.press_detect = True
                self.destroy_all_button()
                self.detect_button_var.set("取消检测")
                self.detect_button.pack(
                    fill="both", expand="yes", padx=200, pady=10)
                print("人脸检测")
        else:
            is_cancel_detect = tk.messagebox.askokcancel(
                title='', message="确定要取消检测吗?")  # return True 0r False
            if is_cancel_detect:
                self.press_detect = False
                self.detect_button_var.set("人脸检测")
                self.destroy_all_button()
                self.pack_all_button()
                print("取消检测")

    # 添加人脸/停止添加按钮对应程序
    def add(self):
        if self.press_add == False:
            is_add = tk.messagebox.askokcancel(
                title='', message="确定要添加人脸吗?")  # return True 0r False
            if is_add:
                self.press_add = True
                self.destroy_all_button()
                self.add_button_var.set("停止添加")
                self.get_name_id()
                print("人脸识别")
        else:
            is_cancel_add = tk.messagebox.askokcancel(
                title='', message="确定要停止添加吗?")  # return True 0r False
            if is_cancel_add:
                self.face_tools.number = 0
                self.is_me_var.set("是我" )
                self.update_label_flag = True
                self.press_add = False
                self.destroy_all_button()
                self.add_button_var.set("添加人脸")
                self.pack_all_button()
                self.face_tools.face_train()
                tk.messagebox.showinfo(message="已添加新的人脸，正在重新训练模型！")
                self.vs.go_on()
                print("添加完成")

    # 切换视频源
    def change_source(self):
        if self.press_change_source == False:
            self.press_change_source = True

    # 是我按钮对应程序
    def is_me(self):
        self.press_not_me_button = False
        self.press_is_me_button = True

    # 不是我按钮对应程序
    def not_me(self):
        self.press_not_me_button = True
        self.press_is_me_button = False

    # 得到姓名及编号
    def get_name_id(self):
        self.frame_h.pack()
        self.frame_l.pack()
        self.name_label.pack(side="left", fill="both", padx=5, pady=5)
        self.name_entry.pack(side="right", fill="both", padx=5, pady=5)
        self.id_label.pack(side="left", fill="both", padx=5, pady=5)
        self.id_entry.pack(side="right", fill="both", padx=5, pady=5)
        self.ok_button.pack(side="bottom", fill="y", ipadx=5, pady=5)

    # 保存id
    def save_id(self):
        get_name = self.name_entry.get()
        get_id = self.id_entry.get()
        if get_id != "" and get_name != "" and len(get_id) <= 6 and len(get_name) <= 20:
            if get_id.isdigit():
                if get_id in self.face_tools.usrs_dict.keys():
                    tk.messagebox.showinfo(
                        message="此id已使用，如果你再使用会影响之前用户!\n请联系管理员操作。")
                    meaage = "有一个名为%s的用户想使用已被使用编号%s被拒绝。" % (get_name, get_id)
                    self.face_tools.sent_message("有人要有已有编号", meaage)
                    return
                self.face_tools.usrs_dict[str(int(get_id))] = get_name
                self.face_tools.save_dict()
                meaage = "有一个名为%s，编号为%s的用户录入了人脸信息。" % (get_name, get_id)
                self.face_tools.sent_message("有新人脸添加", meaage)
                self.face_tools.face_id = get_id
                print("已经保存了您的姓名和编号")
                print(self.face_tools.usrs_dict)
                self.destroy_all_button()
                self.press_not_me_button = True
                self.is_me_button.pack(
                    side="left", fill="both", expand="yes", padx=5, pady=5)
                self.not_me_button.pack(
                    side="left", fill="both", expand="yes", padx=5, pady=5)
                self.add_button.pack(
                    side="right", fill="both", expand="yes", padx=5, pady=5)
            else:
                tk.messagebox.showinfo(message="编号只能为数字哦！")
        else:
            tk.messagebox.showinfo(message="姓名和编号都不能为空且符合字数要求哦！")

    # 切换视频源
    def change_sources(self):
        self.source_number += 1
        if self.source_number == len(self.change_list):
            self.source_number = 0
        self.vs.close()
        self.vs = VideoStream(self.change_list[self.source_number])
        self.vs.run()

    # 放置初始四大按钮
    def pack_all_button(self):
        self.add_button.pack(side="right", fill="both",
                             expand="yes", padx=10, pady=10)
        self.detect_button.pack(side="right", fill="both",
                                expand="yes", padx=10, pady=10)
        self.recognize_button.pack(
            side="right", fill="both", expand="yes", padx=10, pady=10)
        self.change_source_button.pack(
            side="right", fill="both", expand="yes", padx=10, pady=10)

    # 删除所有按钮
    def destroy_all_button(self):
        self.recognize_button.pack_forget()
        self.add_button.pack_forget()
        self.detect_button.pack_forget()
        self.frame_h.pack_forget()
        self.frame_l.pack_forget()
        self.name_label.pack_forget()
        self.name_entry.pack_forget()
        self.id_label.pack_forget()
        self.id_entry.pack_forget()
        self.ok_button.pack_forget()
        self.is_me_button.pack_forget()
        self.not_me_button.pack_forget()
        self.change_source_button.pack_forget()

    # 关闭vedio_loop线程
    def close(self):
        if self.run_manage:
            self.vs.close()
            self.root.destroy()
            print("关闭窗口")
            return
        self.run_thread = False
        is_quit = tk.messagebox.askyesno(title='请求确认', message="确定退出了吗？")
        if is_quit:
            self.vs.close()
            self.root.destroy()
        else:
            self.run_thread = True
            self.thread = threading.Thread(target=self.video_loop)
            self.thread.start()
