from Setting import Setting
from FaceTools import FaceTools
import matplotlib.pyplot as plt
import pickle as pk
import cv2 as cv
import os
import shutil
import time


class Manage:

    # 初始化函数
    def __init__(self):
        self.users_dict = None
        self.face_tools = None
        self.show_users_dict = {}
        self.quit = False

    # 1展示全部用户
    def show_users(self):
        self.get_show_users_dict()
        print('-'*54)
        print("编号\t\t姓名\t\t\t\t图片数\t")
        for user_id in sorted(self.show_users_dict.keys()):
            print('\n' + user_id+"\t\t" + self.show_users_dict[user_id][0] + '\t\t' + str(
                self.show_users_dict[user_id][1]) + "\t")
            time.sleep(0.1)
        print('-'*54)

    # 2通过id展示用户头像
    def show_user_image_by_id(self):
        chanage = False
        while True:
            id_search = input("\n>请输入要查找的编号，或输入b退出，或输入s查看用户表：")
            if id_search == 'b':
                break
            if id_search == 's':
                self.show_users()
                continue
            if (not id_search.isdigit()) or len(str(int(id_search))) > 6:
                print("【错误】请输入合法（小于等于6位数字）编号。")
                continue
            if id_search not in self.users_dict.keys():
                print("【错误】数据库中没有改编号用户。")
                continue
            img_paths = [os.path.join(Setting().face_image_path, f)
                         for f in os.listdir(Setting().face_image_path)]
            for img_path in img_paths:
                user_id = int(os.path.split(img_path)[-1].split('.')[1])
                if user_id == int(id_search):
                    img = plt.imread(img_path)
                    plt.title(self.users_dict[id_search] +
                              ":" + os.path.split(img_path)[-1])
                    plt.imshow(img, cmap="gray")
                    plt.axis('off')
                    plt.show()
                    command = input(
                        "\n>>直接按回车键（其他）查看下一张，输入d删除本张照片，输入b退出查看该编号：")
                    while command == 'd':
                        if input("\n>>>按回车确认，输入其他取消：") == '':
                            os.remove(img_path)
                            chanage = True
                            print("【通知】已经成功删除。")
                            command = input("\n>>直接按回车键（其他）查看下一张，输入b退出查看该编号：")
                            if command == 'd':
                                command = ''
                        else:
                            print("【通知】已经取消删除。")
                            command = input(
                                "\n>>直接按回车键（其他）查看下一张，输入d删除本张照片，输入b退出查看该编号：")
                    if command == 'b':
                        break
                    else:
                        continue
        if chanage:
            print("【通知】由于您删除了图片，正在重新训练模型")
            self.face_tools.face_train()
        self.press_enter_continue()

    # 3通过姓名查看id
    def show_user_image_by_name(self):
        while True:
            name = input("\n>请输入要查找的姓名，或输入b退出，或输入s查看用户表：")
            if name == 'b':
                break
            if name == 's':
                self.show_users()
                continue
            if not len(name) in range(2, 21):
                print("【错误】这不是一个合法（2~20字符）用户名。")
                continue
            if not name in self.users_dict.values():
                print("【错误】没有改用户名。")
                continue
            ids = []
            for key, value in self.users_dict.items():
                if value == name:
                    ids.append(key)
            img_paths = [os.path.join(Setting().face_image_path, f)
                         for f in os.listdir(Setting().face_image_path)]
            show_paths = {}
            for id_search in ids:
                for img_path in img_paths:
                    user_id = int(os.path.split(img_path)[-1].split('.')[1])
                    if user_id == int(id_search):
                        show_paths[user_id] = img_path
                        break
            size = len(show_paths)
            i = 1
            plt.figure()
            for key, value in show_paths.items():
                img = plt.imread(value)
                plt.subplot(1, size, i)
                i = i+1
                plt.title("id: " + str(key))
                plt.imshow(img, cmap='gray'),
                plt.axis('off')
            plt.show()
        self.press_enter_continue()

    # 4删除用户
    def delete_user(self):
        change = False
        while True:
            delete_id = input("\n>请输入要删除的编号，或输入b退出，或输入s查看用户表：")
            if delete_id == 'b':
                break
            if delete_id == 's':
                self.show_users()
                continue
            if (not delete_id.isdigit()) or len(str(int(delete_id))) > 6:
                print("【错误】请输入合法（小于等于6位数字）编号。")
                continue
            if not delete_id in self.users_dict.keys():
                print("【错误】无此编号")
                continue
            img_paths = [os.path.join(Setting().face_image_path, f)
                         for f in os.listdir(Setting().face_image_path)]
            delete_paths = []
            for img_path in img_paths:
                user_id = int(os.path.split(img_path)[-1].split('.')[1])
                if user_id == int(delete_id):
                    delete_paths.append(img_path)
            command = ''
            while True:
                command = input("\n>>按回车将图片移动到回收站，或输入d直接删除，或输入b返回：")
                if command == 'b':
                    break
                if command == 'd':
                    if input("\n>>>按回车确认，输入其他取消：") == '':
                        change = True
                        self.users_dict.pop(delete_id)
                        self.save_users_dict()
                        for img_path in delete_paths:
                            try:
                                os.remove(img_path)
                            except Exception:
                                print("【错误】出现异常")
                                break 
                        print("【通知】已成功删除")
                        break
                    else:
                        print("【通知】已取消删除")
                        continue
                else:
                    if input("\n>>>按回车确认放入回收站，输入其他取消：") == '':
                        change = True
                        self.users_dict.pop(delete_id)
                        self.save_users_dict()
                        for img_path in delete_paths:
                            dst = os.path.join(
                                Setting().recycle_path, os.path.split(img_path)[-1])
                            try:
                                shutil.move(img_path, dst)
                            except Exception:
                                print("【错误】出现异常")
                                break
                        print("【通知】已成功移入回收站")
                        break
                    else:
                        print("【通知】已取消移入回收站")
                        continue
        if change:
            print("【通知】数据发生变化，正在重新训练模型……")
            self.face_tools.face_train()
        self.press_enter_continue()

    # 5修改姓名
    def alter_name(self):
        while True:
            alter_id = input("\n>请输入要改的编号，或输入b退出，或输入s查看用户表：")
            if alter_id == 'b':
                break
            if alter_id == 's':
                self.show_users()
                continue
            if (not alter_id.isdigit()) or len(str(int(alter_id))) > 6:
                print("【错误】请输入合法（小于等于6位数字）编号。")
                continue
            if alter_id not in self.users_dict.keys():
                print("【错误】数据库中没有改编号用户。")
                continue
            new_name = ""
            while True:
                new_name = input(
                    "\n>>输入"+self.users_dict[alter_id]+"更改后姓名，或数如b返回：")
                if new_name == 'b':
                    break
                if len(new_name) in range(2, 21):
                    if input("\n>>>按回车确认修改，输入任意内容取消：") == '':
                        self.users_dict[alter_id] = new_name
                        self.save_users_dict()
                        print("【通知】修改完成，结果如下")
                        self.show_users()
                        break
                    else:
                        print("【通知】已经取消修改。")
                        continue
                else:
                    print("【错误】这不是一个合法（2~20字符）用户名。")

        self.press_enter_continue()

    # 6修改编号
    def alter_id(self):
        change = False
        while True:
            alter_id = input("\n>请输入要改的编号，或输入s查看用户表，或输入b退出：")
            if alter_id == 'b':
                break
            if alter_id == 's':
                self.show_users()
                continue
            if (not alter_id.isdigit()) or len(str(int(alter_id))) > 6:
                print("\n【错误】请输入合法（小于等于6位数字）编号。")
                continue
            if alter_id not in self.users_dict.keys():
                print("\n【错误】数据库中没有改编号用户。")
                continue
            new_id = ''
            while True:
                new_id = input("\n>>请输入新的编号,或输入b返回：")
                if new_id == 'b':
                    break
                if (not alter_id.isdigit()) or (len(str(int(new_id))) > 6):
                    print("\n【错误】请输入合法（小于等于6位数字）编号。")
                    continue
                if new_id in self.users_dict.keys():
                    print("\n【错误】这个编号已被" +
                          self.users_dict[new_id]+"使用。如果他们是一个人请通过合并人员功能进行操作。")
                    continue
                else:
                    if input("\n>>>按回车确认修改，输入任意内容取消：") == '':
                        change = True
                        print("\n【通知】以成功修改,结果如下")
                        self.users_dict[new_id] = self.users_dict[alter_id]
                        self.users_dict.pop(alter_id)
                        self.save_users_dict()
                        self.rename_photo([alter_id], new_id)
                        print("\n【通知】修改成功,结果如下：")
                        self.show_users()
                        break
                    else:
                        print("\n【通知】已取消修改")
        if change:
            print("\n【通知】数据发生变化，正在重新训练模型……")
            self.face_tools.face_train()
            self.press_enter_continue()

    # 7合并人员
    def combine_users(self):
        change = False
        while True:
            command = input("\n>按回车（或输入未用字符）开始输入要合并编号，或输入s查看用户表，或输入b退出：")
            if command == 'b':
                break
            if command == 's':
                self.show_users()
                continue
            while True:
                users_id = []
                i = 1
                back = False
                # 取得要合并的编号
                while True:
                    user_id = input("\n>>请输入第%s个编号，或按回车完成停止添加,或输入b退出：" % (i))
                    if user_id == 'b':
                        back = True
                        break
                    if user_id == '':
                        break
                    if (not user_id.isdigit()) or len(str(int(user_id))) > 6:
                        print("【错误】请输入合法（小于等于6位数字）编号。")
                        continue
                    if user_id not in self.users_dict.keys():
                        print("【错误】数据库中没有改编号用户。")
                        continue
                    if user_id in self.users_dict.keys():
                        if user_id not in users_id:
                            i += 1
                            users_id.append(user_id)
                        else:
                            print("【错误】已经输入过了。")
                    else:
                        print("【错误】数据库不存在这个编号。")
                if back == True:
                    break
                if len(users_id) < 2:
                    print("【错误】合并人数要大于等于2。")
                    continue
                # 取得合并后的编号
                new_id = ""
                while True:
                    new_id = input("\n>>请输入合并后的编号(小于6字符，不要与其它编号重复)，或输入b退出：")
                    if new_id == 'b':
                        back = True
                        break
                    if new_id in users_id:
                        break
                    if (not new_id.isdigit()) or len(str(int(new_id))) > 6:
                        print("【错误】请输入合法（小于等于6位数字）编号。")
                        continue
                    if new_id in self.users_dict.keys():
                        print("【错误】已存在该编号。")
                        continue
                    break
                if back == True:
                    break
                # 取得合并后的姓名
                new_name = ""
                while True:
                    new_name = input("\n>>请输入合并后的姓名(小于20字符)，或输入b退出：")
                    if new_name == 'b':
                        back = True
                        break
                    if len(new_name) <= 20 and len(new_id) > 0:
                        break
                    print("【错误】输入不符合姓名格式要求。")
                if back == True:
                    break
                # 最后确认
                if input("\n>>>将合并编号为%s的%s个用户合并为%s：%s，按回车确认，输入其它取消：" % (str(users_id), len(users_id), new_id, new_name)) != '':
                    print("【通知】已取消合并")
                    continue
                change = True
                for user_id in users_id:
                    self.users_dict.pop(user_id)
                self.users_dict[new_id] = new_name
                self.save_users_dict()
                self.rename_photo(users_id, new_id)
                print("【通知】数据以改变，会在后台重新训练模型。")
                self.show_users()
                back = True
                break
        if change:
            self.face_tools.face_train()
        self.press_enter_continue()

    # 打印分隔符
    def press_enter_continue(self):
        input("-"*51 + "\n按回车继续")

    # 打印欢迎字符画
    def welcome(self):
        s = '$$\\      $$\\ $$$$$$$$\\ $$\\        $$$$$$\\   $$$$$$\\  $$\\      $$\\ '+'\n$$ | $\\  $$ |$$  _____|$$ |      $$  __$$\\ $$  __$$\\ $$$\\    $$$ |'+'\n$$ |$$$\\ $$ |$$ |      $$ |      $$ /  \\__|$$ /  $$ |$$$$\\  $$$$ |'+'\n$$ $$ $$\\$$ |$$$$$\\    $$ |      $$ |      $$ |  $$ |$$\\$$\\$$ $$ |' + \
            '\n$$$$  _$$$$ |$$  __|   $$ |      $$ |      $$ |  $$ |$$ \\$$$  $$ |'+'\n$$$  / \\$$$ |$$ |      $$ |      $$ |  $$\\ $$ |  $$ |$$ |\\$  /$$ |' + \
            '\n$$  /   \\$$ |$$$$$$$$\\ $$$$$$$$\\ \\$$$$$$  | $$$$$$  |$$ | \\_/ $$ |' + \
            '\n\\__/     \\__|\\________|\\________| \\______/  \\______/ \\__|     \\__|'
        print(s)

    # 字典转换为便于输出的样式
    def get_show_users_dict(self):
        s = {}
        for user_id, user_name in self.users_dict.items():
            s["0"*(6-len(user_id))+user_id] = [user_name +
                                               " "*(20-len(user_name)), 0]
        img_paths = [os.path.join(Setting().face_image_path, f)
                     for f in os.listdir(Setting().face_image_path)]
        for img_path in img_paths:
            user_id = os.path.split(img_path)[-1].split('.')[1]
            if user_id in self.users_dict:
                s["0"*(6-len(user_id))+user_id][1] += 1
        self.show_users_dict = s

    # 打开文件程序
    def open_users_dict(self):
        try:
            with open(Setting().usrs_info_path, 'rb') as usr_file:
                self.users_dict = pk.load(usr_file)
                usr_file.close()
        except FileNotFoundError:
            print("【异常】出现严重错误，数据可能会坏。")

    # 将修改保存至文件
    def save_users_dict(self):
        try:
            with open(Setting().usrs_info_path, 'wb') as usr_file:
                pk.dump(self.users_dict, usr_file)
        except FileNotFoundError:
            print("【异常】出现错误")
        usr_file.close()

    # 重命名图片
    def rename_photo(self, users_id, new_id):
        img_paths = [os.path.join(Setting().face_image_path, f)
                     for f in os.listdir(Setting().face_image_path)]
        i = 0
        for img_path in img_paths:
            user_id = os.path.split(img_path)[-1].split('.')[1]
            if user_id in users_id:
                i += 1
                os.rename(img_path, Setting().face_image_path +
                          "/temp." + str(i) + ".jpg")
        i = 0
        img_paths = [os.path.join(Setting().face_image_path, f)
                     for f in os.listdir(Setting().face_image_path)]
        for img_path in img_paths:
            flag = os.path.split(img_path)[-1].split('.')[0]
            if flag == 'temp':
                i += 1
                os.rename(img_path, (Setting().face_image_path +
                                     "/people." + new_id + '.' + str(i) + ".jpg"))

    # 管理员登录
    def login(self):
        for i in range(1, 4):
            name = input("\n请输入管理员编号：")
            password = input("\n请输入8位管理员密码：")
            hh = input("\n按回车键进入")
            if name == "" and password == "" and hh == " ":
                self.face_tools.sent_message(
                    "\n身份验证", "有人登录了管理员账户，如果不是您请赶快采取行动。")
                print("\n"*50)
                break
            print("【错误】密码或用户名错误")
            if i == 3:
                print("【警告】滚！！！")
                # self.face_tools.sent_message("安全通知","有人试图登录管理员账户被拒")
                return

    # 主循环入口，选择功能
    def run(self):
        self.open_users_dict()
        self.face_tools = FaceTools()
        print("\n"*100)
        self.welcome()
        print("\n\n")
        # 管理员登录
        self.login()
        # 功能循环
        while self.quit == False:
            print('\n'*100)
            print('='*51)
            print('[1]展示全部用户      \t\t[2]通过编号查看用户\t\t\t\n')
            print('[3]通过姓名查看用户  \t\t[4]删除用户\t\t\t\n')
            print('[5]修改姓名           \t\t[6]修改编号\t\t\t\n')
            print('[7]合并人员          \t\t[8]退出\t\t\t')
            print('='*51)
            instruct = ''
            while True:
                instruct = input("\n请输入指令(数字)编号：")
                if instruct in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    break
                print("【错误】请输入1~8的数字。")
            if int(instruct) == 8:  # [8]退出
                self.quit = True
                print("已退出")
                break
            print('\n'*100)
            if int(instruct) == 1:  # [1]展示全部用户
                self.show_users()
                self.press_enter_continue()
            elif int(instruct) == 2:  # [2]通过编号查看用户
                self.show_user_image_by_id()
            elif int(instruct) == 3:  # [3]通过姓名查看用户
                self.show_user_image_by_name()
            elif int(instruct) == 4:  # [4]删除用户
                self.delete_user()
            elif int(instruct) == 5:  # [5]修改姓名
                self.alter_name()
            elif int(instruct) == 6:  # [6]修改编号
                self.alter_id()
            elif int(instruct) == 7:  # [7]合并人员
                self.combine_users()

if __name__=="__main__":
    g = Manage()
    g.run()
