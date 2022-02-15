# --*--coding：UTF-8 --*--
# 姓名：汪季轩
# 项目名称：软件课设test
# 开发时间：2021年11月15日20:56:57

import xlwt
import xlrd
import sys
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPalette, QBrush, QPixmap, QFont, QRegExpValidator
from PyQt5.QtCore import Qt, QThread, QRegExp, pyqtSignal, QMutex
from qtawesome import icon
# pickle序列化、反序列化工具，相当于DB
import pickle
from threading import Thread
import requests
from lxml import etree
from lxml.html import fromstring
import re
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import numpy as np
import pandas as pd
import collections
import jieba
import wordcloud
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
from snownlp import SnowNLP
from neo4j_test import CreateGraph

proxies = {}
qmut = QMutex()  # 线程访问顺序锁
movie_urls = []  # 广度搜索所有电影url
now_ID = ''
rank = []
title_ch = []
title_en = []
year = []
score = []
director = []
actor = []
genre = []
country = []
language = []
length = []
comment = []
movies = []

# 线程：广度爬取TOP250的电影详情信息页url
class PAThread(QThread):
    # trigger = pyqtSignal(str)

    def __init__(self, url):
        super(PAThread, self).__init__()
        self.url = url

    def run(self):
        # qmut.lock()
        try:
            global movie_urls
            global proxies
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            resp = requests.get(url=self.url, headers=headers, proxies=proxies)
            # try: # debug
            #     if resp.status_code == 200:
            #         print("成功获取html!")
            # except:
            #     print("爬取失败~")
            #     return None
            # 转换类型
            html = etree.HTML(resp.text)
            lis = html.xpath('/html/body/div[3]/div[1]/div/div[1]/ol/li')
            # 获取所有电影url
            for i in lis:
                movie_url = i.xpath('./div/div[1]/a//@href')
                # list转换成str
                movie_url = ''.join(movie_url)
                movie_urls.append(movie_url)
            # print(movie_urls)
            # qmut.unlock()

        except:
            print('url获取异常')

# 线程：解析每个电影的url，将详细数据存到缓存列表
class WorkThread(QThread):
    # trigger = pyqtSignal(str)

    def __init__(self, url):
        super(WorkThread, self).__init__()
        self.url = url

    def run(self):
        try:
            global proxies
            global rank
            global title_ch
            global title_en
            global year
            global score
            global director
            global actor
            global genre
            global country
            global language
            global length
            global comment
            global movies
            # print(f'爬取成功~{self.url}')
            # proxies = {
            #     'https': 'http://112.195.155.230:4256'
            # }
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            resp = requests.get(url=self.url, headers=headers, proxies=proxies)

            # 转换类型 数据解析
            movie = []
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, features='lxml')
                tree = fromstring(resp.text)
                try:
                    title_tmp = ''.join(tree.xpath('//*[@id="content"]/h1/span[1]/text()'))
                    # 分割中文与英文名称
                    title_tmp = re.split(' ', title_tmp, 1)
                    movie.append(title_tmp[0])
                    movie.append(title_tmp[1])
                except:
                    movie.append(' ')
                    # movie.append('title_en_error')
                try:
                    movie.append(''.join(tree.xpath('//*[@id="content"]/div[1]/span[1]/text()')))
                except:
                    movie.append('rank_error')
                try:
                    movie.append(re.search('(?<=(<span class="year">\()).*(?=(\)</span>))', resp.text).group())
                except:
                    movie.append('year_error')
                try:
                    movie.append(''.join(tree.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()')))
                except:
                    movie.append('score_error')
                try:
                    director_tmp = tree.xpath('//*[@id="info"]/span[1]')[0].text_content()
                    director_tmp = director_tmp.strip('导演: ')
                    movie.append(director_tmp)
                except:
                    movie.append('director_error')
                try:
                    actor_tmp = tree.xpath('//*[@id="info"]/span[3]')[0].text_content()
                    actor_tmp = actor_tmp.strip('主演: ')
                    movie.append(actor_tmp)
                except:
                    movie.append('actor_error')
                try:
                    genres = soup.find_all('span', {'property': 'v:genre'})
                    genre_temp = []
                    for each in genres:
                        genre_temp.append(each.get_text())
                    movie.append('/'.join(genre_temp))
                except:
                    movie.append('genre_error')
                try:
                    movie.append(soup.find(text='制片国家/地区:').parent.next_sibling)
                except:
                    movie.append('country_error')
                try:
                    movie.append(soup.find(text='语言:').parent.next_sibling)
                except:
                    movie.append('language_error')
                try:
                    movie.append(soup.find('span', {'property': 'v:runtime'}).get_text())
                except:
                    movie.append('length_error')
                try:
                    movie.append(''.join(tree.xpath('//*[@id="hot-comments"]/div[1]/div/p/span/text()')))
                except:
                    movie.append('comment_error')
                print(title_tmp)
            else:
                print(f'{self.url}爬取错误403')
                movie.append('title_ch')
                movie.append('title_en')
                movie.append('rank')
                movie.append('year')
                movie.append('score')
                movie.append('director')
                movie.append('actor')
                movie.append('genre')
                movie.append('country')
                movie.append('language')
                movie.append('length')
                movie.append('comment')
            movies.append(movie)
            print(f'当前进度：---{len(movies) * 0.4}%')
        except:
            print(f'{self.url}爬取错误_异常')
            print(f'当前进度：---{len(movies) * 0.4}%')


# GUI界面 登录窗口
class LoginPage(QWidget):
    '''用户注册、登录窗口'''
    def __init__(self):
        # 继承QWidget类
        super(LoginPage, self).__init__()
        # 设置窗口标题
        self.setWindowTitle('面向豆瓣电影的知识图谱的设计与实现')
        # 设置窗口图标
        self.setWindowIcon(QIcon("./img/shouye_.ico"))
        # 设置只显示窗口关闭按钮
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        # 设置窗口大小，固定大小
        # self.resize(400, 400)
        self.setFixedSize(300, 300)
        # 设置窗口背景图片
        self.window_pale = QPalette()
        self.window_pale.setBrush(self.backgroundRole(), QBrush(QPixmap("./img/preview1.jpg")))
        self.setPalette(self.window_pale)
        # 设置label
        self.label_0 = QLabel('用户登录界面')
        # 设置label居中
        self.label_0.setAlignment(Qt.AlignCenter)
        # 设置字体样式
        self.label_0.setFont(QFont('宋体', 12, QFont.Bold))
        self.name_label = QLabel('用户名')
        self.password_label = QLabel('密码')
        # 单行文本输入框
        self.name_line = QLineEdit()
        self.password_line = QLineEdit()
        # 输入框文本初始化
        self.name_line.setPlaceholderText('请在此处输入用户名')
        self.password_line.setPlaceholderText('请在此输入密码')
        # 设置密码隐藏
        self.password_line.setEchoMode(QLineEdit.Password)
        # 检查单行文本框输入状态
        self.name_line.textChanged.connect(self.check_input)
        self.password_line.textChanged.connect(self.check_input)
        # 按钮
        self.login_button = QPushButton('登录')
        self.login_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.exit_button = QPushButton('退出')
        self.exit_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.register_button = QPushButton('注册')
        self.register_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 按钮初始化
        # 先设置登录按钮不可点击，输入用户名和密码后方可点击
        self.login_button.setEnabled(False)
        # 登录按钮点击信号绑定槽
        self.login_button.clicked.connect(self.login)
        # 注册按钮点击信号绑定槽
        self.register_button.clicked.connect(self.register)
        # 退出按钮点击信号绑定槽
        self.exit_button.clicked.connect(self.close)
        # 登录界面状态复选框
        self.remember_name = QCheckBox('记住用户名')
        self.remember_password = QCheckBox('记住密码')
        self.auto_login = QCheckBox('自动登录')
        # 复选框初始化
        self.remember_name.stateChanged.connect(self.remember_name_func)
        self.remember_password.stateChanged.connect(self.remember_password_func)
        self.auto_login.stateChanged.connect(self.auto_login_func)
        # 布局
        # 水平布局
        self.h1_layout = QHBoxLayout()
        self.h2_layout = QHBoxLayout()
        # 网格布局
        self.grid_layout = QGridLayout()
        # 垂直布局
        self.v_layout = QVBoxLayout()
        # 页面布局初始化
        # 网格布局初始化
        self.grid_layout.setSpacing(20)
        self.grid_layout.addWidget(self.name_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.name_line, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.password_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.password_line, 1, 1, 1, 1)
        # 水平布局初始化1 加载三个按钮
        self.h1_layout.addWidget(self.login_button)
        self.h1_layout.addWidget(self.register_button)
        self.h1_layout.addWidget(self.exit_button)
        # 水平布局初始化2 加载三个复选框
        self.h2_layout.addStretch(1)
        self.h2_layout.addWidget(self.remember_name)
        self.h2_layout.addWidget(self.remember_password)
        self.h2_layout.addWidget(self.auto_login)
        # 垂直布局初始化
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.label_0)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.grid_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h2_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h1_layout)
        self.v_layout.addStretch(1)
        # 最终布局
        self.setLayout(self.v_layout)
        # 登录界面状态初始化：是否自动登录等
        self.login_init()

    # 检查文本输入框的方法
    def check_input(self):
        # 当用户名及密码输入框均有内容时，设置登录按钮为可点击状态，否则，不可点击
        if self.name_line.text() and self.password_line.text():
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)

    # 登录方法
    def login(self):
        global now_ID
        # 获取输入的用户名和密码
        name, password = self.name_line.text(), self.password_line.text()
        # 向本地服务端发送请求
        try:
            # 读取本地用户名单文件
            with open('./test_data/users.pkl', 'rb') as f:
                users = pickle.load(f)
        except:
            QMessageBox.warning(self, '警告', '暂无用户数据，请先注册！')
            return
        # 登录
        if name in users.keys():
            if password == users[name][0]:
                # 检查用户登录状态
                self.check_login_state()
                now_ID = self.name_line.text()
                self.main_page = MainPage()
                self.main_page.show()
                self.hide()
            else:
                QMessageBox.warning(self, '警告', '密码错误，请重新输入！')
        else:
            QMessageBox.warning(self, '警告', '用户不存在，请先注册！')
        # 登录时未选择记住ID复选框，先清除login.pkl，然后写入0（非login_init，这是考虑登录后login.pkl会发生改变，
        # 导致login_init时无法实现取消保存ID）
        if not self.remember_name.isChecked():
            try:
                os.remove('./test_tmpdata/login.pkl')
            except:
                pass
            with open('./test_tmpdata/login.pkl', 'wb') as f:
                pickle.dump(0, f)


    # 检查用户状态方法,登录的时候查看复选框是否保存数据
    def check_login_state(self):
        self.remember_name_func()
        self.remember_password_func()
        self.auto_login_func()

    # 注册方法
    def register(self):
        # 打开用户注册界面
        self.register_page = RegisterPage()
        # 注册页面的注册成功信号绑定，在登录页面输入注册成功后的ID和密码
        self.register_page.successful_signal.connect(self.successful_func)
        self.register_page.exec()

    # 注册成功，登录界面载入刚刚注册的数据
    def successful_func(self, data):
        # 将注册成功的账号和密码写入登录页面
        self.name_line.setText(data[0])
        self.password_line.setText(data[1])

    # 记住用户名到tmp_data
    def remember_name_func(self):
        if self.remember_name.isChecked():
            name = self.name_line.text()
            with open('./test_tmpdata/login.pkl', 'wb') as f:
                pickle.dump(name, f)  # 向f中写入name
        else:
            # 未选择记住ID复选框，先清除login.pkl，然后写入0
            try:
                os.remove('./test_tmpdata/login.pkl')
            except:
                pass
            with open('./test_tmpdata/login.pkl', 'wb') as f:
                pickle.dump(0, f)



    # 记住用户名和密码到tmp_data
    def remember_password_func(self):
        if self.remember_password.isChecked():
            # 记住密码则用户名也记住
            self.remember_name.setChecked(True)
        data  = [self.name_line.text(), self.password_line.text()]
        with open('./test_tmpdata/login.pkl', 'wb') as f:  # 写入数据
            pickle.dump(data, f)
        # 如果未选择保存密码复选框，只写入ID字符串，不会在login_init启动保存密码
        if not self.remember_password.isChecked():
            try:
                with open('./test_tmpdata/login.pkl', 'wb') as f:  # 写入数据
                    pickle.dump(self.name_line.text(), f)
            except:
                pass

    # 自动登录，保存数据，仅保存上一次的登录用户
    def auto_login_func(self):
        # 选中自动登录复选框 保存数据到auto.pkl
        if self.auto_login.isChecked():
            data = [self.name_line.text(), self.password_line.text()]
            with open('./test_tmpdata/auto.pkl', 'wb') as f:
                pickle.dump(data, f)
        # 否则 删除自动登录数据
        else:
            try:
                os.remove('./test_tmpdata/auto.pkl')
            except:
                pass

    # 页面登录信息初始化，包括自动登录等
    def login_init(self):
        # 尝试读取记住用户名，或记住用户密码保存文件数据(上一次)
        try:
            with open('./test_tmpdata/login.pkl', 'rb') as f:
                data = pickle.load(f)
            # 如果数据是字符串类型，则是保存用户名
            if isinstance(data, str):
                self.name_line.setText(data)
                self.remember_name.setChecked(True)
            # 否则，是保存用户名及密码的列表
            else:
                self.name_line.setText(data[0])
                self.password_line.setText(data[1])
                self.remember_name.setChecked(True)
                self.remember_password.setChecked(True)
        except:
            pass
        # 尝试读取自动登录保存的数据
        try:
            with open('./test_tmpdata/auto.pkl', 'rb') as f:
                data2 = pickle.load(f)
            self.name_line.setText(data2[0])
            self.password_line.setText(data2[1])
            self.login()
            self.auto_login.setChecked(True)

        except:
            pass


# GUI界面 注册对话窗口
class RegisterPage(QDialog):
    # 自定义注册成功信号,传递列表信息
    successful_signal = pyqtSignal(list)
    def __init__(self):
        super(RegisterPage, self).__init__()
        self.setWindowTitle('用户注册')
        self.setWindowIcon(QIcon('./img/hetongguanli.ico'))
        self.setFixedSize(450, 250)
        # 设置窗口背景图片
        self.window_pale = QPalette()
        self.window_pale.setBrush(self.backgroundRole(), QBrush(QPixmap("./img/preview1.jpg")))
        self.setPalette(self.window_pale)
        self.label_0 = QLabel('欢迎注册')
        # 设置字体
        self.label_0.setFont(QFont('宋体', 12, QFont.Bold))
        self.label_0.setAlignment(Qt.AlignCenter)
        self.name_label = QLabel('用户账号/ID：')
        self.password1_label = QLabel('用户密码：')
        self.password2_label = QLabel('重复密码：')
        # 其他用户信息label控件
        self.nick_label = QLabel('昵称：')
        self.gender_label = QLabel('性别：')
        # 单行文本输入框
        self.name_line = QLineEdit()
        self.password1_line = QLineEdit()
        # 再次输入密码的单行文本输入款为自定义的文本输入框
        self.password2_line = MyLineEdit()
        self.nick_line = QLineEdit()
        # 性别单选框
        self.male_button = QRadioButton('男')
        self.female_button = QRadioButton('女')
        # 单行文本输入框初始化
        self.line_init()
        # 用户其他信息控件尺寸调整
        self.nick_label.setMinimumWidth(60)
        self.nick_line.setMaximumWidth(150)
        # 按钮
        self.register_button = QPushButton('注册')
        self.register_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.cancel_button = QPushButton('取消')
        self.cancel_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 按钮初始化方法
        self.pushbutton_init()
        # 布局管理器 四大块 其中前三大块最终放在第四块垂直布局中
        self.h1_layout = QHBoxLayout()
        self.h2_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()
        self.v_layout = QVBoxLayout()
        # 页面布局初始化
        self.layout_init()

    # 页面布局初始化方法
    def layout_init(self):
        # 网格布局
        # 设置网格布局中控件间距
        self.grid_layout.setSpacing(20)
        self.grid_layout.addWidget(self.name_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.name_line, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.password1_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.password1_line, 1, 1, 1, 1)
        self.grid_layout.addWidget(self.password2_label, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.password2_line, 2, 1, 1, 1)
        # 水平布局1
        self.h1_layout.addWidget(self.register_button)
        self.h1_layout.addWidget(self.cancel_button)
        # 水平布局2
        self.h2_layout.addWidget(self.nick_label)
        self.h2_layout.addSpacing(12)
        self.h2_layout.addWidget(self.nick_line)
        self.h2_layout.addSpacing(10)
        self.h2_layout.addWidget(self.gender_label)
        self.h2_layout.addWidget(self.male_button)
        self.h2_layout.addWidget(self.female_button)
        # 垂直布局
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.label_0)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.grid_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h2_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h1_layout)
        self.v_layout.addStretch(1)
        # 设置最终布局
        self.setLayout(self.v_layout)

    # 单行文本输入框初始化方法、槽函数绑定、正则校验等
    def line_init(self):
        # 单行文本输入框内容变化绑定按钮显示
        self.name_line.textChanged.connect(self.check_input)
        self.password1_line.textChanged.connect(self.check_input)
        self.password2_line.textChanged.connect(self.check_input)
        # 设置密码显示方式：隐藏
        self.password1_line.setEchoMode(QLineEdit.Password)
        self.password2_line.setEchoMode(QLineEdit.Password)
        # 注册提示
        self.name_line.setPlaceholderText('输入用户名账号，字母数字，不可为中文或特殊字符。')
        self.password1_line.setPlaceholderText('密码为6到18位数字字母及下划线，以字母开头。')
        self.password2_line.setPlaceholderText('请再次输入并确认密码！')
        # 设置文本框校验器
        # 姓名文本框校验器设置
        # 1、创建正则表达式限定输入内容
        name_RegExp = QRegExp("[0-9A-Za-z]*")
        # 2、创建文本框校验器
        name_validator = QRegExpValidator(name_RegExp)
        # 3、文本输入框绑定创建的校验器
        self.name_line.setValidator(name_validator)
        # 设置密码文本输入框校验器
        password_val = QRegExpValidator(QRegExp("^[a-zA-Z]\w{5,17}$"))
        self.password1_line.setValidator(password_val)
        self.password2_line.setValidator(password_val)
        # 检查密码输入,验证密码输入位数，两次密码输入是否一致。
        self.password2_line.focus_out.connect(self.check_password)

    # 按钮初始化方法
    def pushbutton_init(self):
        # 设置注册按钮为不可点击状态，绑定槽函数
        self.register_button.setEnabled(False)
        self.register_button.clicked.connect(self.register_func)
        # 取消按钮绑定取消注册槽函数
        self.cancel_button.clicked.connect(self.cancel_func)

    # 检查输入方法,只有在三个文本输入框都有文字时，注册按钮才为可点击状态
    def check_input(self):
        if (self.name_line.text() and self.password1_line.text()
                and self.password2_line.text()):
            self.register_button.setEnabled(True)
        else:
            self.register_button.setEnabled(False)

    # 取消注册方法
    # 如果用户在注册界面输入了数据，提示用户是否确认取消注册，如未输入数据则直接退出。
    def cancel_func(self):
        if (self.name_line.text() or self.password1_line.text()
                or self.password2_line.text()):
            choice = QMessageBox.information(self, '提示', '是否取消注册？', QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.close()
            else:
                return
        else:
            self.close()

    # 检查用户输入密码合法性方法
    def check_password(self):
        password_1 = self.password1_line.text()
        password_2 = self.password2_line.text()

        if len(password_1) < 6:
            QMessageBox.warning(self, '警告', '密码位数小于6')
            self.password1_line.setText('')
            self.password2_line.setText('')
        else:
            if password_1 == password_2:
                pass
            else:
                QMessageBox.warning(self, '警告', '两次密码输入结果不一致！')
                self.password1_line.setText('')

    # 用户注册方法
    def register_func(self):
        # 先获取注册用户ID，检查用户ID是否存在
        ID = self.name_line.text()
        try:
            with open('./test_data/users.pkl', 'rb') as f1:
                users = pickle.load(f1)
        except:
            users = {}

        # 如果用户ID已存在，提示用户ID已被注册
        if ID in users.keys():
            QMessageBox.information(self, '提示', '该用户ID已被注册！')
        # 否则收集用户注册信息
        else:
            gender = self.gender_data()
            user_data = [self.password1_line.text(),
                         self.nick_line.text(),
                         gender]
            # 写入用户信息字典
            users[ID] = user_data
            with open('./test_data/users.pkl', 'wb') as f2:
                pickle.dump(users, f2)
            # 提醒用户注册成功，询问是否登录
            choice = QMessageBox.information(self, '提示', '注册成功，是否登录？', QMessageBox.Yes | QMessageBox.No)
            # 如选择是，关闭注册页面，并在登录页面用户ID显示注册ID,密码
            if choice == QMessageBox.Yes:
                # 注册后立刻登录，将注册的用户ID和密码直接通过信号emit回该RegisterPage对象，并显示
                self.successful_signal.emit([self.name_line.text(),
                                             self.password1_line.text()])
                self.close()
            # 如选择否，直接关闭注册页面。
            else:
                self.close()

    # 用户性别信息收集,男为1，女为2，未选择为0
    def gender_data(self):
        if self.male_button.isChecked():
            gender = 1
        elif self.female_button.isChecked():
            gender = 2
        else:
            gender = 0
        return gender


# GUI输入框焦点重写：重写输入框类，重写焦点转移事件,让焦点转移时发出一个自定义信号。
class MyLineEdit(QLineEdit):
    focus_out = pyqtSignal(str)
    def focusOutEvent(self, QFocusEvent):
        super(MyLineEdit, self).focusOutEvent(QFocusEvent)
        self.focus_out.emit(self.text())


# GUI界面 登录后主界面窗口
class MainPage(QWidget):
    def __init__(self):
        global now_ID
        super(MainPage, self).__init__()
        self.setWindowTitle('面向豆瓣电影的知识图谱的设计与实现')
        self.setWindowIcon(QIcon("./img/shouye_.ico"))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setFixedSize(500, 500)
        # 设置窗口背景图片
        self.window_pale = QPalette()
        self.window_pale.setBrush(self.backgroundRole(), QBrush(QPixmap("./img/preview4.jpg")))
        self.setPalette(self.window_pale)
        self.label_0 = QLabel('面向豆瓣电影的知识图谱系统')
        self.label_0.setAlignment(Qt.AlignCenter)
        self.label_0.setFont(QFont('宋体', 12, QFont.Bold))
        self.state_id = QLabel()
        self.state_id.setText('                当前登录ID：')
        self.state_id.setFont(QFont('楷体', 12, QFont.Bold))
        self.id_label = QLabel()
        self.id_label.setText(now_ID)
        self.id_label.setFont(QFont('楷体', 12, QFont.Bold))
        # 按钮
        self.pa_button = QPushButton('加载豆瓣电影信息')
        self.pa_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.map_button = QPushButton('导出数据构建知识图谱')
        self.map_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.word_freq_button = QPushButton('获取词频统计')
        self.word_freq_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.motion_button = QPushButton('获取情感分析')
        self.motion_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.back_button = QPushButton('返回登录界面')
        self.back_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.exit_button = QPushButton('退出')
        self.exit_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 按钮初始化
        # 爬虫按钮初始化，绑定槽函数pa
        self.pa_button.clicked.connect(self.pa)
        # 知识图谱按钮点击信号绑定槽
        self.map_button.clicked.connect(self.get_excel_map)
        # 词频统计按钮点击信号绑定槽
        self.word_freq_button.clicked.connect(self.get_word_freq)
        # 情感分析按钮点击信号绑定槽
        self.motion_button.clicked.connect(self.get_motion)
        # 返回登录界面按钮
        self.back_button.clicked.connect(self.get_back)
        # 退出按钮点击信号绑定槽
        self.exit_button.clicked.connect(self.close)
        # 布局
        # 水平布局
        self.h1_layout = QHBoxLayout()
        self.h2_layout = QHBoxLayout()
        # 网格布局
        self.grid_layout = QGridLayout()
        # 垂直布局
        self.v_layout = QVBoxLayout()
        # 页面布局初始化
        # 网格布局初始化
        self.grid_layout.setSpacing(20)
        self.grid_layout.addWidget(self.state_id, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.id_label, 0, 1, 1, 1)
        # 水平布局初始化1 加载三个按钮
        self.h1_layout.addWidget(self.pa_button)
        self.h1_layout.addWidget(self.map_button)
        self.h1_layout.addWidget(self.word_freq_button)
        # 水平布局初始化2 加载三个按钮
        self.h2_layout.addWidget(self.motion_button)
        self.h2_layout.addWidget(self.back_button)
        self.h2_layout.addWidget(self.exit_button)
        # 垂直布局初始化
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.label_0)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.grid_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h1_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h2_layout)
        self.v_layout.addStretch(1)
        # 最终布局
        self.setLayout(self.v_layout)

    def pa(self):
        global movie_urls
        global proxies
        # top250页面广度获取电影url,不用多线程，没必要，页面较少（10页）
        # get_proxy()
        for i in range(10):
            url = f'https://movie.douban.com/top250?start={i*25}&filter='
            PAThread(url).run()
            print(f'第{i}页url爬取完毕~')
            # sleep(0.1)

        # 爬取到的url：调试用：
        movie_urls = ['https://movie.douban.com/subject/1292052/', 'https://movie.douban.com/subject/1291546/', 'https://movie.douban.com/subject/1292720/', 'https://movie.douban.com/subject/1292722/', 'https://movie.douban.com/subject/1295644/', 'https://movie.douban.com/subject/1292063/', 'https://movie.douban.com/subject/1291561/', 'https://movie.douban.com/subject/1295124/', 'https://movie.douban.com/subject/3541415/', 'https://movie.douban.com/subject/3011091/', 'https://movie.douban.com/subject/1889243/', 'https://movie.douban.com/subject/1292064/', 'https://movie.douban.com/subject/1292001/', 'https://movie.douban.com/subject/3793023/', 'https://movie.douban.com/subject/2131459/', 'https://movie.douban.com/subject/1291549/', 'https://movie.douban.com/subject/1307914/', 'https://movie.douban.com/subject/25662329/', 'https://movie.douban.com/subject/1292213/', 'https://movie.douban.com/subject/5912992/', 'https://movie.douban.com/subject/1291841/', 'https://movie.douban.com/subject/1849031/', 'https://movie.douban.com/subject/1296141/', 'https://movie.douban.com/subject/1291560/', 'https://movie.douban.com/subject/3319755/', 'https://movie.douban.com/subject/6786002/', 'https://movie.douban.com/subject/1293172/', 'https://movie.douban.com/subject/1851857/', 'https://movie.douban.com/subject/20495023/', 'https://movie.douban.com/subject/1292365/', 'https://movie.douban.com/subject/1295038/', 'https://movie.douban.com/subject/1291552/', 'https://movie.douban.com/subject/1300267/', 'https://movie.douban.com/subject/21937452/', 'https://movie.douban.com/subject/2129039/', 'https://movie.douban.com/subject/26387939/', 'https://movie.douban.com/subject/30170448/', 'https://movie.douban.com/subject/26752088/', 'https://movie.douban.com/subject/1293182/', 'https://movie.douban.com/subject/1308807/', 'https://movie.douban.com/subject/1929463/', 'https://movie.douban.com/subject/1291858/', 'https://movie.douban.com/subject/1299398/', 'https://movie.douban.com/subject/1291583/', 'https://movie.douban.com/subject/1305487/', 'https://movie.douban.com/subject/1291828/', 'https://movie.douban.com/subject/1298624/', 'https://movie.douban.com/subject/1291572/', 'https://movie.douban.com/subject/1293839/', 'https://movie.douban.com/subject/1296736/', 'https://movie.douban.com/subject/3742360/', 'https://movie.douban.com/subject/1291571/', 'https://movie.douban.com/subject/21937445/', 'https://movie.douban.com/subject/1418019/', 'https://movie.douban.com/subject/1291843/', 'https://movie.douban.com/subject/1299131/', 'https://movie.douban.com/subject/1291548/', 'https://movie.douban.com/subject/1301753/', 'https://movie.douban.com/subject/25958717/', 'https://movie.douban.com/subject/1292000/', 'https://movie.douban.com/subject/27060077/', 'https://movie.douban.com/subject/1291818/', 'https://movie.douban.com/subject/1306029/', 'https://movie.douban.com/subject/1900841/', 'https://movie.douban.com/subject/1485260/', 'https://movie.douban.com/subject/1292220/', 'https://movie.douban.com/subject/1293350/', 'https://movie.douban.com/subject/3008247/', 'https://movie.douban.com/subject/1292402/', 'https://movie.douban.com/subject/26580232/', 'https://movie.douban.com/subject/1292224/', 'https://movie.douban.com/subject/1292849/', 'https://movie.douban.com/subject/1294408/', 'https://movie.douban.com/subject/1303021/', 'https://movie.douban.com/subject/1652587/', 'https://movie.douban.com/subject/3442220/', 'https://movie.douban.com/subject/1780330/', 'https://movie.douban.com/subject/1293544/', 'https://movie.douban.com/subject/3011235/', 'https://movie.douban.com/subject/1292262/', 'https://movie.douban.com/subject/2334904/', 'https://movie.douban.com/subject/1292343/', 'https://movie.douban.com/subject/11525673/', 'https://movie.douban.com/subject/1292656/', 'https://movie.douban.com/subject/1291832/', 'https://movie.douban.com/subject/1292679/', 'https://movie.douban.com/subject/1294371/', 'https://movie.douban.com/subject/1292223/', 'https://movie.douban.com/subject/1302425/', 'https://movie.douban.com/subject/1297192/', 'https://movie.douban.com/subject/1300299/', 'https://movie.douban.com/subject/1787291/', 'https://movie.douban.com/subject/1298070/', 'https://movie.douban.com/subject/1865703/', 'https://movie.douban.com/subject/6985810/', 'https://movie.douban.com/subject/1292370/', 'https://movie.douban.com/subject/26799731/', 'https://movie.douban.com/subject/1291543/', 'https://movie.douban.com/subject/10777687/', 'https://movie.douban.com/subject/1294639/', 'https://movie.douban.com/subject/5322596/', 'https://movie.douban.com/subject/1291544/', 'https://movie.douban.com/subject/1418834/', 'https://movie.douban.com/subject/1292215/', 'https://movie.douban.com/subject/2149806/', 'https://movie.douban.com/subject/1306249/', 'https://movie.douban.com/subject/1297630/', 'https://movie.douban.com/subject/1297359/', 'https://movie.douban.com/subject/1291999/', 'https://movie.douban.com/subject/25814705/', 'https://movie.douban.com/subject/1291875/', 'https://movie.douban.com/subject/1296339/', 'https://movie.douban.com/subject/1292434/', 'https://movie.douban.com/subject/3395373/', 'https://movie.douban.com/subject/1293359/', 'https://movie.douban.com/subject/1296996/', 'https://movie.douban.com/subject/11026735/', 'https://movie.douban.com/subject/21318488/', 'https://movie.douban.com/subject/1292337/', 'https://movie.douban.com/subject/1300992/', 'https://movie.douban.com/subject/25814707/', 'https://movie.douban.com/subject/1297447/', 'https://movie.douban.com/subject/1291990/', 'https://movie.douban.com/subject/1297052/', 'https://movie.douban.com/subject/4202302/', 'https://movie.douban.com/subject/1305164/', 'https://movie.douban.com/subject/5989818/', 'https://movie.douban.com/subject/2353023/', 'https://movie.douban.com/subject/1292274/', 'https://movie.douban.com/subject/3072124/', 'https://movie.douban.com/subject/10577869/', 'https://movie.douban.com/subject/1291579/', 'https://movie.douban.com/subject/1291545/', 'https://movie.douban.com/subject/4268598/', 'https://movie.douban.com/subject/4917726/', 'https://movie.douban.com/subject/1316510/', 'https://movie.douban.com/subject/3287562/', 'https://movie.douban.com/subject/1294240/', 'https://movie.douban.com/subject/1418200/', 'https://movie.douban.com/subject/1858711/', 'https://movie.douban.com/subject/25986180/', 'https://movie.douban.com/subject/21360417/', 'https://movie.douban.com/subject/26628357/', 'https://movie.douban.com/subject/1307315/', 'https://movie.douban.com/subject/6307447/', 'https://movie.douban.com/subject/1395091/', 'https://movie.douban.com/subject/26325320/', 'https://movie.douban.com/subject/4920389/', 'https://movie.douban.com/subject/27010768/', 'https://movie.douban.com/subject/1306861/', 'https://movie.douban.com/subject/1295399/', 'https://movie.douban.com/subject/1303037/', 'https://movie.douban.com/subject/10437779/', 'https://movie.douban.com/subject/1309055/', 'https://movie.douban.com/subject/1417598/', 'https://movie.douban.com/subject/1302467/', 'https://movie.douban.com/subject/10463953/', 'https://movie.douban.com/subject/1291557/', 'https://movie.douban.com/subject/1291822/', 'https://movie.douban.com/subject/26611804/', 'https://movie.douban.com/subject/1292208/', 'https://movie.douban.com/subject/1907966/', 'https://movie.douban.com/subject/1291585/', 'https://movie.douban.com/subject/26683290/', 'https://movie.douban.com/subject/1578507/', 'https://movie.douban.com/subject/10533913/', 'https://movie.douban.com/subject/1297574/', 'https://movie.douban.com/subject/1793929/', 'https://movie.douban.com/subject/1295409/', 'https://movie.douban.com/subject/25917973/', 'https://movie.douban.com/subject/3792799/', 'https://movie.douban.com/subject/1293181/', 'https://movie.douban.com/subject/1304447/', 'https://movie.douban.com/subject/25895901/', 'https://movie.douban.com/subject/1959195/', 'https://movie.douban.com/subject/24750126/', 'https://movie.douban.com/subject/1297518/', 'https://movie.douban.com/subject/25773932/', 'https://movie.douban.com/subject/1292401/', 'https://movie.douban.com/subject/2209573/', 'https://movie.douban.com/subject/1300374/', 'https://movie.douban.com/subject/1292328/', 'https://movie.douban.com/subject/27622447/', 'https://movie.douban.com/subject/10808442/', 'https://movie.douban.com/subject/6534248/', 'https://movie.douban.com/subject/1291578/', 'https://movie.douban.com/subject/1978709/', 'https://movie.douban.com/subject/4848115/', 'https://movie.douban.com/subject/1862151/', 'https://movie.douban.com/subject/1828115/', 'https://movie.douban.com/subject/1293318/', 'https://movie.douban.com/subject/1291870/', 'https://movie.douban.com/subject/1293460/', 'https://movie.douban.com/subject/3011051/', 'https://movie.douban.com/subject/1309163/', 'https://movie.douban.com/subject/1307811/', 'https://movie.douban.com/subject/1292226/', 'https://movie.douban.com/subject/1293908/', 'https://movie.douban.com/subject/1308857/', 'https://movie.douban.com/subject/1296909/', 'https://movie.douban.com/subject/1302827/', 'https://movie.douban.com/subject/1867345/', 'https://movie.douban.com/subject/4739952/', 'https://movie.douban.com/subject/27059130/', 'https://movie.douban.com/subject/25980443/', 'https://movie.douban.com/subject/26430107/', 'https://movie.douban.com/subject/1291879/', 'https://movie.douban.com/subject/1292329/', 'https://movie.douban.com/subject/26787574/', 'https://movie.douban.com/subject/1291844/', 'https://movie.douban.com/subject/1307106/', 'https://movie.douban.com/subject/25724855/', 'https://movie.douban.com/subject/3075287/', 'https://movie.douban.com/subject/1303394/', 'https://movie.douban.com/subject/1310177/', 'https://movie.douban.com/subject/1292287/', 'https://movie.douban.com/subject/3592854/', 'https://movie.douban.com/subject/1461403/', 'https://movie.douban.com/subject/1293964/', 'https://movie.douban.com/subject/5300054/', 'https://movie.douban.com/subject/1438652/', 'https://movie.douban.com/subject/2222996/', 'https://movie.douban.com/subject/1428175/', 'https://movie.douban.com/subject/25807345/', 'https://movie.douban.com/subject/1300117/', 'https://movie.douban.com/subject/1304141/', 'https://movie.douban.com/subject/1419936/', 'https://movie.douban.com/subject/1295865/', 'https://movie.douban.com/subject/1307856/', 'https://movie.douban.com/subject/27119724/', 'https://movie.douban.com/subject/1308767/', 'https://movie.douban.com/subject/1959877/', 'https://movie.douban.com/subject/3443389/', 'https://movie.douban.com/subject/1305690/', 'https://movie.douban.com/subject/1937946/', 'https://movie.douban.com/subject/1304102/', 'https://movie.douban.com/subject/2363506/', 'https://movie.douban.com/subject/1760622/', 'https://movie.douban.com/subject/25934014/', 'https://movie.douban.com/subject/6874403/', 'https://movie.douban.com/subject/5908478/', 'https://movie.douban.com/subject/26614893/', 'https://movie.douban.com/subject/2213597/', 'https://movie.douban.com/subject/25864085/', 'https://movie.douban.com/subject/25954475/', 'https://movie.douban.com/subject/25921812/', 'https://movie.douban.com/subject/26393561/', 'https://movie.douban.com/subject/2297265/', 'https://movie.douban.com/subject/1307394/', 'https://movie.douban.com/subject/1292528/']

        # movie_urls = ['https://movie.douban.com/subject/1292052/', 'https://movie.douban.com/subject/1291546/',
        #  'https://movie.douban.com/subject/1292720/', 'https://movie.douban.com/subject/1295644/',
        #  'https://movie.douban.com/subject/1292722/', 'https://movie.douban.com/subject/1292063/',
        #  'https://movie.douban.com/subject/1291561/', 'https://movie.douban.com/subject/1295124/',
        #  'https://movie.douban.com/subject/3541415/', 'https://movie.douban.com/subject/3011091/',
        #  'https://movie.douban.com/subject/1889243/', 'https://movie.douban.com/subject/1292064/',
        #  'https://movie.douban.com/subject/1292001/', 'https://movie.douban.com/subject/3793023/',
        #  'https://movie.douban.com/subject/2131459/', 'https://movie.douban.com/subject/1291549/',
        #  'https://movie.douban.com/subject/1307914/', 'https://movie.douban.com/subject/25662329/',
        #  'https://movie.douban.com/subject/1292213/', 'https://movie.douban.com/subject/5912992/',
        #  'https://movie.douban.com/subject/1291841/', 'https://movie.douban.com/subject/1849031/',
        #  'https://movie.douban.com/subject/1291560/', 'https://movie.douban.com/subject/1296141/',
        #  'https://movie.douban.com/subject/3319755/', 'https://movie.douban.com/subject/6786002/',
        #  'https://movie.douban.com/subject/1293172/', 'https://movie.douban.com/subject/1851857/',
        #  'https://movie.douban.com/subject/20495023/', 'https://movie.douban.com/subject/1292365/',
        #  'https://movie.douban.com/subject/1291552/', 'https://movie.douban.com/subject/1295038/',
        #  'https://movie.douban.com/subject/1300267/', 'https://movie.douban.com/subject/30170448/',
        #  'https://movie.douban.com/subject/21937452/', 'https://movie.douban.com/subject/2129039/',
        #  'https://movie.douban.com/subject/26387939/', 'https://movie.douban.com/subject/1293182/',
        #  'https://movie.douban.com/subject/1308807/', 'https://movie.douban.com/subject/26752088/',
        #  'https://movie.douban.com/subject/1929463/', 'https://movie.douban.com/subject/1291858/',
        #  'https://movie.douban.com/subject/1299398/', 'https://movie.douban.com/subject/1291583/',
        #  'https://movie.douban.com/subject/1291828/', 'https://movie.douban.com/subject/1305487/',
        #  'https://movie.douban.com/subject/1298624/', 'https://movie.douban.com/subject/1291572/',
        #  'https://movie.douban.com/subject/1293839/', 'https://movie.douban.com/subject/1296736/',
        #  'https://movie.douban.com/subject/3742360/', 'https://movie.douban.com/subject/1291571/',
        #  'https://movie.douban.com/subject/21937445/', 'https://movie.douban.com/subject/1418019/',
        #  'https://movie.douban.com/subject/1299131/', 'https://movie.douban.com/subject/1301753/',
        #  'https://movie.douban.com/subject/1291548/', 'https://movie.douban.com/subject/1291843/',
        #  'https://movie.douban.com/subject/1292000/', 'https://movie.douban.com/subject/25958717/',
        #  'https://movie.douban.com/subject/27060077/', 'https://movie.douban.com/subject/1291818/',
        #  'https://movie.douban.com/subject/1306029/', 'https://movie.douban.com/subject/1900841/',
        #  'https://movie.douban.com/subject/1485260/', 'https://movie.douban.com/subject/1293350/',
        #  'https://movie.douban.com/subject/1292220/', 'https://movie.douban.com/subject/3008247/',
        #  'https://movie.douban.com/subject/1292402/', 'https://movie.douban.com/subject/26580232/',
        #  'https://movie.douban.com/subject/1292224/', 'https://movie.douban.com/subject/1292849/',
        #  'https://movie.douban.com/subject/1294408/', 'https://movie.douban.com/subject/1303021/',
        #  'https://movie.douban.com/subject/1652587/', 'https://movie.douban.com/subject/3442220/',
        #  'https://movie.douban.com/subject/1780330/', 'https://movie.douban.com/subject/1293544/',
        #  'https://movie.douban.com/subject/1292262/', 'https://movie.douban.com/subject/3011235/',
        #  'https://movie.douban.com/subject/2334904/', 'https://movie.douban.com/subject/1292343/',
        #  'https://movie.douban.com/subject/11525673/', 'https://movie.douban.com/subject/1292656/',
        #  'https://movie.douban.com/subject/1291832/', 'https://movie.douban.com/subject/1292679/',
        #  'https://movie.douban.com/subject/1292223/', 'https://movie.douban.com/subject/1294371/',
        #  'https://movie.douban.com/subject/1302425/', 'https://movie.douban.com/subject/1297192/',
        #  'https://movie.douban.com/subject/1787291/', 'https://movie.douban.com/subject/1300299/',
        #  'https://movie.douban.com/subject/1298070/', 'https://movie.douban.com/subject/1865703/',
        #  'https://movie.douban.com/subject/1292370/', 'https://movie.douban.com/subject/6985810/',
        #  'https://movie.douban.com/subject/26799731/', 'https://movie.douban.com/subject/1294639/',
        #  'https://movie.douban.com/subject/10777687/', 'https://movie.douban.com/subject/1291543/',
        #  'https://movie.douban.com/subject/1418834/', 'https://movie.douban.com/subject/5322596/',
        #  'https://movie.douban.com/subject/1291544/', 'https://movie.douban.com/subject/1292215/',
        #  'https://movie.douban.com/subject/1306249/', 'https://movie.douban.com/subject/1297630/',
        #  'https://movie.douban.com/subject/1297359/', 'https://movie.douban.com/subject/2149806/',
        #  'https://movie.douban.com/subject/1291999/', 'https://movie.douban.com/subject/25814705/',
        #  'https://movie.douban.com/subject/1291875/', 'https://movie.douban.com/subject/1296339/',
        #  'https://movie.douban.com/subject/1292434/', 'https://movie.douban.com/subject/3395373/',
        #  'https://movie.douban.com/subject/1293359/', 'https://movie.douban.com/subject/21318488/',
        #  'https://movie.douban.com/subject/1292337/', 'https://movie.douban.com/subject/11026735/',
        #  'https://movie.douban.com/subject/25814707/', 'https://movie.douban.com/subject/1296996/',
        #  'https://movie.douban.com/subject/1300992/', 'https://movie.douban.com/subject/1297447/',
        #  'https://movie.douban.com/subject/1297052/', 'https://movie.douban.com/subject/1291990/',
        #  'https://movie.douban.com/subject/4202302/', 'https://movie.douban.com/subject/1305164/',
        #  'https://movie.douban.com/subject/5989818/', 'https://movie.douban.com/subject/2353023/',
        #  'https://movie.douban.com/subject/1292274/', 'https://movie.douban.com/subject/3072124/',
        #  'https://movie.douban.com/subject/10577869/', 'https://movie.douban.com/subject/1291545/',
        #  'https://movie.douban.com/subject/4268598/', 'https://movie.douban.com/subject/1291579/',
        #  'https://movie.douban.com/subject/4917726/', 'https://movie.douban.com/subject/1316510/',
        #  'https://movie.douban.com/subject/3287562/', 'https://movie.douban.com/subject/1418200/',
        #  'https://movie.douban.com/subject/1294240/', 'https://movie.douban.com/subject/1858711/',
        #  'https://movie.douban.com/subject/21360417/', 'https://movie.douban.com/subject/25986180/',
        #  'https://movie.douban.com/subject/26628357/', 'https://movie.douban.com/subject/1307315/',
        #  'https://movie.douban.com/subject/6307447/', 'https://movie.douban.com/subject/26325320/',
        #  'https://movie.douban.com/subject/1395091/', 'https://movie.douban.com/subject/4920389/',
        #  'https://movie.douban.com/subject/1295399/', 'https://movie.douban.com/subject/1306861/',
        #  'https://movie.douban.com/subject/27010768/', 'https://movie.douban.com/subject/1303037/',
        #  'https://movie.douban.com/subject/1417598/', 'https://movie.douban.com/subject/10437779/',
        #  'https://movie.douban.com/subject/10463953/', 'https://movie.douban.com/subject/1291557/',
        #  'https://movie.douban.com/subject/1302467/', 'https://movie.douban.com/subject/1309055/',
        #  'https://movie.douban.com/subject/1291822/', 'https://movie.douban.com/subject/1292208/',
        #  'https://movie.douban.com/subject/1291585/', 'https://movie.douban.com/subject/26611804/',
        #  'https://movie.douban.com/subject/1907966/', 'https://movie.douban.com/subject/1578507/',
        #  'https://movie.douban.com/subject/1297574/', 'https://movie.douban.com/subject/26683290/',
        #  'https://movie.douban.com/subject/10533913/', 'https://movie.douban.com/subject/1793929/',
        #  'https://movie.douban.com/subject/1295409/', 'https://movie.douban.com/subject/25917973/',
        #  'https://movie.douban.com/subject/3792799/', 'https://movie.douban.com/subject/1304447/',
        #  'https://movie.douban.com/subject/1959195/', 'https://movie.douban.com/subject/25895901/',
        #  'https://movie.douban.com/subject/1293181/', 'https://movie.douban.com/subject/24750126/',
        #  'https://movie.douban.com/subject/25773932/', 'https://movie.douban.com/subject/1297518/',
        #  'https://movie.douban.com/subject/2209573/', 'https://movie.douban.com/subject/1292401/',
        #  'https://movie.douban.com/subject/1292328/', 'https://movie.douban.com/subject/1300374/',
        #  'https://movie.douban.com/subject/27622447/', 'https://movie.douban.com/subject/10808442/',
        #  'https://movie.douban.com/subject/6534248/', 'https://movie.douban.com/subject/1978709/',
        #  'https://movie.douban.com/subject/1291578/', 'https://movie.douban.com/subject/4848115/',
        #  'https://movie.douban.com/subject/1862151/', 'https://movie.douban.com/subject/1293318/',
        #  'https://movie.douban.com/subject/1291870/', 'https://movie.douban.com/subject/1828115/',
        #  'https://movie.douban.com/subject/1293460/', 'https://movie.douban.com/subject/3011051/',
        #  'https://movie.douban.com/subject/1309163/', 'https://movie.douban.com/subject/1307811/',
        #  'https://movie.douban.com/subject/1292226/', 'https://movie.douban.com/subject/1293908/',
        #  'https://movie.douban.com/subject/1308857/', 'https://movie.douban.com/subject/26430107/',
        #  'https://movie.douban.com/subject/1296909/', 'https://movie.douban.com/subject/1302827/',
        #  'https://movie.douban.com/subject/4739952/', 'https://movie.douban.com/subject/25980443/',
        #  'https://movie.douban.com/subject/26787574/', 'https://movie.douban.com/subject/1867345/',
        #  'https://movie.douban.com/subject/27059130/', 'https://movie.douban.com/subject/1291879/',
        #  'https://movie.douban.com/subject/1291844/', 'https://movie.douban.com/subject/1292329/',
        #  'https://movie.douban.com/subject/25724855/', 'https://movie.douban.com/subject/1303394/',
        #  'https://movie.douban.com/subject/3075287/', 'https://movie.douban.com/subject/1307106/',
        #  'https://movie.douban.com/subject/1292287/', 'https://movie.douban.com/subject/1310177/',
        #  'https://movie.douban.com/subject/3592854/', 'https://movie.douban.com/subject/1293964/',
        #  'https://movie.douban.com/subject/5300054/', 'https://movie.douban.com/subject/1438652/',
        #  'https://movie.douban.com/subject/2222996/', 'https://movie.douban.com/subject/1428175/',
        #  'https://movie.douban.com/subject/25807345/', 'https://movie.douban.com/subject/1295865/',
        #  'https://movie.douban.com/subject/1419936/', 'https://movie.douban.com/subject/1461403/',
        #  'https://movie.douban.com/subject/1300117/', 'https://movie.douban.com/subject/1308767/',
        #  'https://movie.douban.com/subject/1304141/', 'https://movie.douban.com/subject/3443389/',
        #  'https://movie.douban.com/subject/1959877/', 'https://movie.douban.com/subject/1305690/',
        #  'https://movie.douban.com/subject/1937946/', 'https://movie.douban.com/subject/1307856/',
        #  'https://movie.douban.com/subject/1304102/', 'https://movie.douban.com/subject/2363506/',
        #  'https://movie.douban.com/subject/1760622/', 'https://movie.douban.com/subject/26614893/',
        #  'https://movie.douban.com/subject/6874403/', 'https://movie.douban.com/subject/27119724/',
        #  'https://movie.douban.com/subject/5908478/', 'https://movie.douban.com/subject/2213597/',
        #  'https://movie.douban.com/subject/25934014/', 'https://movie.douban.com/subject/25921812/',
        #  'https://movie.douban.com/subject/25954475/', 'https://movie.douban.com/subject/25864085/',
        #  'https://movie.douban.com/subject/26393561/', 'https://movie.douban.com/subject/2297265/',
        #  'https://movie.douban.com/subject/1292528/', 'https://movie.douban.com/subject/1307394/']
        #
        print('电影url爬取完毕!开始爬取数据~')
        print(movie_urls)
        print(len(movie_urls))
        # get_proxy()
        # 多线程爬取详细信息
        sleep(3)
        self.work_0 = WorkThread(movie_urls[0])
        self.work_0.start()
        self.work_1 = WorkThread(movie_urls[1])
        self.work_1.start()
        self.work_2 = WorkThread(movie_urls[2])
        self.work_2.start()
        self.work_3 = WorkThread(movie_urls[3])
        self.work_3.start()
        self.work_4 = WorkThread(movie_urls[4])
        self.work_4.start()
        # sleep(1)
        self.work_5 = WorkThread(movie_urls[5])
        self.work_5.start()
        self.work_6 = WorkThread(movie_urls[6])
        self.work_6.start()
        self.work_7 = WorkThread(movie_urls[7])
        self.work_7.start()
        self.work_8 = WorkThread(movie_urls[8])
        self.work_8.start()
        self.work_9 = WorkThread(movie_urls[9])
        self.work_9.start()
        # sleep(1)
        self.work_10 = WorkThread(movie_urls[10])
        self.work_10.start()
        self.work_11 = WorkThread(movie_urls[11])
        self.work_11.start()
        self.work_12 = WorkThread(movie_urls[12])
        self.work_12.start()
        self.work_13 = WorkThread(movie_urls[13])
        self.work_13.start()
        self.work_14 = WorkThread(movie_urls[14])
        self.work_14.start()
        # sleep(1)
        self.work_15 = WorkThread(movie_urls[15])
        self.work_15.start()
        self.work_16 = WorkThread(movie_urls[16])
        self.work_16.start()
        self.work_17 = WorkThread(movie_urls[17])
        self.work_17.start()
        self.work_18 = WorkThread(movie_urls[18])
        self.work_18.start()
        self.work_19 = WorkThread(movie_urls[19])
        self.work_19.start()
        # sleep(1)
        self.work_20 = WorkThread(movie_urls[20])
        self.work_20.start()
        self.work_21 = WorkThread(movie_urls[21])
        self.work_21.start()
        self.work_22 = WorkThread(movie_urls[22])
        self.work_22.start()
        self.work_23 = WorkThread(movie_urls[23])
        self.work_23.start()
        self.work_24 = WorkThread(movie_urls[24])
        self.work_24.start()
        # sleep(1)
        self.work_25 = WorkThread(movie_urls[25])
        self.work_25.start()
        self.work_26 = WorkThread(movie_urls[26])
        self.work_26.start()
        self.work_27 = WorkThread(movie_urls[27])
        self.work_27.start()
        self.work_28 = WorkThread(movie_urls[28])
        self.work_28.start()
        self.work_29 = WorkThread(movie_urls[29])
        self.work_29.start()
        # sleep(1)
        self.work_30 = WorkThread(movie_urls[30])
        self.work_30.start()
        self.work_31 = WorkThread(movie_urls[31])
        self.work_31.start()
        self.work_32 = WorkThread(movie_urls[32])
        self.work_32.start()
        self.work_33 = WorkThread(movie_urls[33])
        self.work_33.start()
        self.work_34 = WorkThread(movie_urls[34])
        self.work_34.start()
        # sleep(1)
        self.work_35 = WorkThread(movie_urls[35])
        self.work_35.start()
        self.work_36 = WorkThread(movie_urls[36])
        self.work_36.start()
        self.work_37 = WorkThread(movie_urls[37])
        self.work_37.start()
        self.work_38 = WorkThread(movie_urls[38])
        self.work_38.start()
        self.work_39 = WorkThread(movie_urls[39])
        self.work_39.start()
        # sleep(1)
        self.work_40 = WorkThread(movie_urls[40])
        self.work_40.start()
        self.work_41 = WorkThread(movie_urls[41])
        self.work_41.start()
        self.work_42 = WorkThread(movie_urls[42])
        self.work_42.start()
        self.work_43 = WorkThread(movie_urls[43])
        self.work_43.start()
        self.work_44 = WorkThread(movie_urls[44])
        self.work_44.start()
        # sleep(1)
        self.work_45 = WorkThread(movie_urls[45])
        self.work_45.start()
        self.work_46 = WorkThread(movie_urls[46])
        self.work_46.start()
        self.work_47 = WorkThread(movie_urls[47])
        self.work_47.start()
        self.work_48 = WorkThread(movie_urls[48])
        self.work_48.start()
        self.work_49 = WorkThread(movie_urls[49])
        self.work_49.start()
        # sleep(1)
        self.work_50 = WorkThread(movie_urls[50])
        self.work_50.start()
        self.work_51 = WorkThread(movie_urls[51])
        self.work_51.start()
        self.work_52 = WorkThread(movie_urls[52])
        self.work_52.start()
        self.work_53 = WorkThread(movie_urls[53])
        self.work_53.start()
        self.work_54 = WorkThread(movie_urls[54])
        self.work_54.start()
        # sleep(1)
        self.work_55 = WorkThread(movie_urls[55])
        self.work_55.start()
        self.work_56 = WorkThread(movie_urls[56])
        self.work_56.start()
        self.work_57 = WorkThread(movie_urls[57])
        self.work_57.start()
        self.work_58 = WorkThread(movie_urls[58])
        self.work_58.start()
        self.work_59 = WorkThread(movie_urls[59])
        self.work_59.start()
        # sleep(1)
        self.work_60 = WorkThread(movie_urls[60])
        self.work_60.start()
        self.work_61 = WorkThread(movie_urls[61])
        self.work_61.start()
        self.work_62 = WorkThread(movie_urls[62])
        self.work_62.start()
        self.work_63 = WorkThread(movie_urls[63])
        self.work_63.start()
        self.work_64 = WorkThread(movie_urls[64])
        self.work_64.start()
        # sleep(1)
        self.work_65 = WorkThread(movie_urls[65])
        self.work_65.start()
        self.work_66 = WorkThread(movie_urls[66])
        self.work_66.start()
        self.work_67 = WorkThread(movie_urls[67])
        self.work_67.start()
        self.work_68 = WorkThread(movie_urls[68])
        self.work_68.start()
        self.work_69 = WorkThread(movie_urls[69])
        self.work_69.start()
        # sleep(1)
        self.work_70 = WorkThread(movie_urls[70])
        self.work_70.start()
        self.work_71 = WorkThread(movie_urls[71])
        self.work_71.start()
        self.work_72 = WorkThread(movie_urls[72])
        self.work_72.start()
        self.work_73 = WorkThread(movie_urls[73])
        self.work_73.start()
        self.work_74 = WorkThread(movie_urls[74])
        self.work_74.start()
        # sleep(1)
        self.work_75 = WorkThread(movie_urls[75])
        self.work_75.start()
        self.work_76 = WorkThread(movie_urls[76])
        self.work_76.start()
        self.work_77 = WorkThread(movie_urls[77])
        self.work_77.start()
        self.work_78 = WorkThread(movie_urls[78])
        self.work_78.start()
        self.work_79 = WorkThread(movie_urls[79])
        self.work_79.start()
        # sleep(1)
        self.work_80 = WorkThread(movie_urls[80])
        self.work_80.start()
        self.work_81 = WorkThread(movie_urls[81])
        self.work_81.start()
        self.work_82 = WorkThread(movie_urls[82])
        self.work_82.start()
        self.work_83 = WorkThread(movie_urls[83])
        self.work_83.start()
        self.work_84 = WorkThread(movie_urls[84])
        self.work_84.start()
        # sleep(1)
        self.work_85 = WorkThread(movie_urls[85])
        self.work_85.start()
        self.work_86 = WorkThread(movie_urls[86])
        self.work_86.start()
        self.work_87 = WorkThread(movie_urls[87])
        self.work_87.start()
        self.work_88 = WorkThread(movie_urls[88])
        self.work_88.start()
        self.work_89 = WorkThread(movie_urls[89])
        self.work_89.start()
        # sleep(1)
        self.work_90 = WorkThread(movie_urls[90])
        self.work_90.start()
        self.work_91 = WorkThread(movie_urls[91])
        self.work_91.start()
        self.work_92 = WorkThread(movie_urls[92])
        self.work_92.start()
        self.work_93 = WorkThread(movie_urls[93])
        self.work_93.start()
        self.work_94 = WorkThread(movie_urls[94])
        self.work_94.start()
        # sleep(1)
        self.work_95 = WorkThread(movie_urls[95])
        self.work_95.start()
        self.work_96 = WorkThread(movie_urls[96])
        self.work_96.start()
        self.work_97 = WorkThread(movie_urls[97])
        self.work_97.start()
        self.work_98 = WorkThread(movie_urls[98])
        self.work_98.start()
        self.work_99 = WorkThread(movie_urls[99])
        self.work_99.start()
        # sleep(1)
        self.work_100 = WorkThread(movie_urls[100])
        self.work_100.start()
        self.work_101 = WorkThread(movie_urls[101])
        self.work_101.start()
        self.work_102 = WorkThread(movie_urls[102])
        self.work_102.start()
        self.work_103 = WorkThread(movie_urls[103])
        self.work_103.start()
        self.work_104 = WorkThread(movie_urls[104])
        self.work_104.start()
        # sleep(1)
        self.work_105 = WorkThread(movie_urls[105])
        self.work_105.start()
        self.work_106 = WorkThread(movie_urls[106])
        self.work_106.start()
        self.work_107 = WorkThread(movie_urls[107])
        self.work_107.start()
        self.work_108 = WorkThread(movie_urls[108])
        self.work_108.start()
        self.work_109 = WorkThread(movie_urls[109])
        self.work_109.start()
        # sleep(1)
        self.work_110 = WorkThread(movie_urls[110])
        self.work_110.start()
        self.work_111 = WorkThread(movie_urls[111])
        self.work_111.start()
        self.work_112 = WorkThread(movie_urls[112])
        self.work_112.start()
        self.work_113 = WorkThread(movie_urls[113])
        self.work_113.start()
        self.work_114 = WorkThread(movie_urls[114])
        self.work_114.start()
        # sleep(1)
        self.work_115 = WorkThread(movie_urls[115])
        self.work_115.start()
        self.work_116 = WorkThread(movie_urls[116])
        self.work_116.start()
        self.work_117 = WorkThread(movie_urls[117])
        self.work_117.start()
        self.work_118 = WorkThread(movie_urls[118])
        self.work_118.start()
        self.work_119 = WorkThread(movie_urls[119])
        self.work_119.start()
        # sleep(1)
        self.work_120 = WorkThread(movie_urls[120])
        self.work_120.start()
        self.work_121 = WorkThread(movie_urls[121])
        self.work_121.start()
        self.work_122 = WorkThread(movie_urls[122])
        self.work_122.start()
        self.work_123 = WorkThread(movie_urls[123])
        self.work_123.start()
        self.work_124 = WorkThread(movie_urls[124])
        self.work_124.start()
        # sleep(1)
        self.work_125 = WorkThread(movie_urls[125])
        self.work_125.start()
        self.work_126 = WorkThread(movie_urls[126])
        self.work_126.start()
        self.work_127 = WorkThread(movie_urls[127])
        self.work_127.start()
        self.work_128 = WorkThread(movie_urls[128])
        self.work_128.start()
        self.work_129 = WorkThread(movie_urls[129])
        self.work_129.start()
        # sleep(1)
        self.work_130 = WorkThread(movie_urls[130])
        self.work_130.start()
        self.work_131 = WorkThread(movie_urls[131])
        self.work_131.start()
        self.work_132 = WorkThread(movie_urls[132])
        self.work_132.start()
        self.work_133 = WorkThread(movie_urls[133])
        self.work_133.start()
        self.work_134 = WorkThread(movie_urls[134])
        self.work_134.start()
        # sleep(1)
        self.work_135 = WorkThread(movie_urls[135])
        self.work_135.start()
        self.work_136 = WorkThread(movie_urls[136])
        self.work_136.start()
        self.work_137 = WorkThread(movie_urls[137])
        self.work_137.start()
        self.work_138 = WorkThread(movie_urls[138])
        self.work_138.start()
        self.work_139 = WorkThread(movie_urls[139])
        self.work_139.start()
        # sleep(1)
        self.work_140 = WorkThread(movie_urls[140])
        self.work_140.start()
        self.work_141 = WorkThread(movie_urls[141])
        self.work_141.start()
        self.work_142 = WorkThread(movie_urls[142])
        self.work_142.start()
        self.work_143 = WorkThread(movie_urls[143])
        self.work_143.start()
        self.work_144 = WorkThread(movie_urls[144])
        self.work_144.start()
        # sleep(1)
        self.work_145 = WorkThread(movie_urls[145])
        self.work_145.start()
        self.work_146 = WorkThread(movie_urls[146])
        self.work_146.start()
        self.work_147 = WorkThread(movie_urls[147])
        self.work_147.start()
        self.work_148 = WorkThread(movie_urls[148])
        self.work_148.start()
        self.work_149 = WorkThread(movie_urls[149])
        self.work_149.start()
        # sleep(1)
        self.work_150 = WorkThread(movie_urls[150])
        self.work_150.start()
        self.work_151 = WorkThread(movie_urls[151])
        self.work_151.start()
        self.work_152 = WorkThread(movie_urls[152])
        self.work_152.start()
        self.work_153 = WorkThread(movie_urls[153])
        self.work_153.start()
        self.work_154 = WorkThread(movie_urls[154])
        self.work_154.start()
        # sleep(1)
        self.work_155 = WorkThread(movie_urls[155])
        self.work_155.start()
        self.work_156 = WorkThread(movie_urls[156])
        self.work_156.start()
        self.work_157 = WorkThread(movie_urls[157])
        self.work_157.start()
        self.work_158 = WorkThread(movie_urls[158])
        self.work_158.start()
        self.work_159 = WorkThread(movie_urls[159])
        self.work_159.start()
        # sleep(1)
        self.work_160 = WorkThread(movie_urls[160])
        self.work_160.start()
        self.work_161 = WorkThread(movie_urls[161])
        self.work_161.start()
        self.work_162 = WorkThread(movie_urls[162])
        self.work_162.start()
        self.work_163 = WorkThread(movie_urls[163])
        self.work_163.start()
        self.work_164 = WorkThread(movie_urls[164])
        self.work_164.start()
        # sleep(1)
        self.work_165 = WorkThread(movie_urls[165])
        self.work_165.start()
        self.work_166 = WorkThread(movie_urls[166])
        self.work_166.start()
        self.work_167 = WorkThread(movie_urls[167])
        self.work_167.start()
        self.work_168 = WorkThread(movie_urls[168])
        self.work_168.start()
        self.work_169 = WorkThread(movie_urls[169])
        self.work_169.start()
        # sleep(1)
        self.work_170 = WorkThread(movie_urls[170])
        self.work_170.start()
        self.work_171 = WorkThread(movie_urls[171])
        self.work_171.start()
        self.work_172 = WorkThread(movie_urls[172])
        self.work_172.start()
        self.work_173 = WorkThread(movie_urls[173])
        self.work_173.start()
        self.work_174 = WorkThread(movie_urls[174])
        self.work_174.start()
        # sleep(1)
        self.work_175 = WorkThread(movie_urls[175])
        self.work_175.start()
        self.work_176 = WorkThread(movie_urls[176])
        self.work_176.start()
        self.work_177 = WorkThread(movie_urls[177])
        self.work_177.start()
        self.work_178 = WorkThread(movie_urls[178])
        self.work_178.start()
        self.work_179 = WorkThread(movie_urls[179])
        self.work_179.start()
        # sleep(1)
        self.work_180 = WorkThread(movie_urls[180])
        self.work_180.start()
        self.work_181 = WorkThread(movie_urls[181])
        self.work_181.start()
        self.work_182 = WorkThread(movie_urls[182])
        self.work_182.start()
        self.work_183 = WorkThread(movie_urls[183])
        self.work_183.start()
        self.work_184 = WorkThread(movie_urls[184])
        self.work_184.start()
        # sleep(1)
        self.work_185 = WorkThread(movie_urls[185])
        self.work_185.start()
        self.work_186 = WorkThread(movie_urls[186])
        self.work_186.start()
        self.work_187 = WorkThread(movie_urls[187])
        self.work_187.start()
        self.work_188 = WorkThread(movie_urls[188])
        self.work_188.start()
        self.work_189 = WorkThread(movie_urls[189])
        self.work_189.start()
        # sleep(1)
        self.work_190 = WorkThread(movie_urls[190])
        self.work_190.start()
        self.work_191 = WorkThread(movie_urls[191])
        self.work_191.start()
        self.work_192 = WorkThread(movie_urls[192])
        self.work_192.start()
        self.work_193 = WorkThread(movie_urls[193])
        self.work_193.start()
        self.work_194 = WorkThread(movie_urls[194])
        self.work_194.start()
        # sleep(1)
        self.work_195 = WorkThread(movie_urls[195])
        self.work_195.start()
        self.work_196 = WorkThread(movie_urls[196])
        self.work_196.start()
        self.work_197 = WorkThread(movie_urls[197])
        self.work_197.start()
        self.work_198 = WorkThread(movie_urls[198])
        self.work_198.start()
        self.work_199 = WorkThread(movie_urls[199])
        self.work_199.start()
        # sleep(1)
        self.work_200 = WorkThread(movie_urls[200])
        self.work_200.start()
        self.work_201 = WorkThread(movie_urls[201])
        self.work_201.start()
        self.work_202 = WorkThread(movie_urls[202])
        self.work_202.start()
        self.work_203 = WorkThread(movie_urls[203])
        self.work_203.start()
        self.work_204 = WorkThread(movie_urls[204])
        self.work_204.start()
        # sleep(1)
        self.work_205 = WorkThread(movie_urls[205])
        self.work_205.start()
        self.work_206 = WorkThread(movie_urls[206])
        self.work_206.start()
        self.work_207 = WorkThread(movie_urls[207])
        self.work_207.start()
        self.work_208 = WorkThread(movie_urls[208])
        self.work_208.start()
        self.work_209 = WorkThread(movie_urls[209])
        self.work_209.start()
        # sleep(1)
        self.work_210 = WorkThread(movie_urls[210])
        self.work_210.start()
        self.work_211 = WorkThread(movie_urls[211])
        self.work_211.start()
        self.work_212 = WorkThread(movie_urls[212])
        self.work_212.start()
        self.work_213 = WorkThread(movie_urls[213])
        self.work_213.start()
        self.work_214 = WorkThread(movie_urls[214])
        self.work_214.start()
        # sleep(1)
        self.work_215 = WorkThread(movie_urls[215])
        self.work_215.start()
        self.work_216 = WorkThread(movie_urls[216])
        self.work_216.start()
        self.work_217 = WorkThread(movie_urls[217])
        self.work_217.start()
        self.work_218 = WorkThread(movie_urls[218])
        self.work_218.start()
        self.work_219 = WorkThread(movie_urls[219])
        self.work_219.start()
        # sleep(1)
        self.work_220 = WorkThread(movie_urls[220])
        self.work_220.start()
        self.work_221 = WorkThread(movie_urls[221])
        self.work_221.start()
        self.work_222 = WorkThread(movie_urls[222])
        self.work_222.start()
        self.work_223 = WorkThread(movie_urls[223])
        self.work_223.start()
        self.work_224 = WorkThread(movie_urls[224])
        self.work_224.start()
        # sleep(1)
        self.work_225 = WorkThread(movie_urls[225])
        self.work_225.start()
        self.work_226 = WorkThread(movie_urls[226])
        self.work_226.start()
        self.work_227 = WorkThread(movie_urls[227])
        self.work_227.start()
        self.work_228 = WorkThread(movie_urls[228])
        self.work_228.start()
        self.work_229 = WorkThread(movie_urls[229])
        self.work_229.start()
        # sleep(1)
        self.work_230 = WorkThread(movie_urls[230])
        self.work_230.start()
        self.work_231 = WorkThread(movie_urls[231])
        self.work_231.start()
        self.work_232 = WorkThread(movie_urls[232])
        self.work_232.start()
        self.work_233 = WorkThread(movie_urls[233])
        self.work_233.start()
        self.work_234 = WorkThread(movie_urls[234])
        self.work_234.start()
        # sleep(1)
        self.work_235 = WorkThread(movie_urls[235])
        self.work_235.start()
        self.work_236 = WorkThread(movie_urls[236])
        self.work_236.start()
        self.work_237 = WorkThread(movie_urls[237])
        self.work_237.start()
        self.work_238 = WorkThread(movie_urls[238])
        self.work_238.start()
        self.work_239 = WorkThread(movie_urls[239])
        self.work_239.start()
        # sleep(1)
        self.work_240 = WorkThread(movie_urls[240])
        self.work_240.start()
        self.work_241 = WorkThread(movie_urls[241])
        self.work_241.start()
        self.work_242 = WorkThread(movie_urls[242])
        self.work_242.start()
        self.work_243 = WorkThread(movie_urls[243])
        self.work_243.start()
        self.work_244 = WorkThread(movie_urls[244])
        self.work_244.start()
        # sleep(1)
        self.work_245 = WorkThread(movie_urls[245])
        self.work_245.start()
        self.work_246 = WorkThread(movie_urls[246])
        self.work_246.start()
        self.work_247 = WorkThread(movie_urls[247])
        self.work_247.start()
        self.work_248 = WorkThread(movie_urls[248])
        self.work_248.start()
        self.work_249 = WorkThread(movie_urls[249])
        self.work_249.start()








    def get_excel_map(self):
        print('正在导出数据')
        to_excel()
        print('导出完成！正在构建知识图谱...')
        # 构建知识图谱
        sleep(2)
        data_xls = pd.read_excel('movie_data.xls', index_col=0)
        data_xls.to_csv('movie_data.csv', encoding='utf-8')
        sleep(1)
        # 清空数据库 match (n) detach delete n
        CreateGraph()
        print('知识图谱构建完成！')




    def get_word_freq(self):
        self.wordfreq_page = WordFreq()
        self.wordfreq_page.show()


    def get_motion(self):
        self.motion_page = Motion()
        self.motion_page.show()

    def get_back(self):
        self.close()
        window.show()


# GUI界面 获取词频统计界面窗口
class WordFreq(QWidget):
    def __init__(self):
        super(WordFreq, self).__init__()
        self.setWindowTitle('词频统计')
        self.setWindowIcon(QIcon("./img/shouye_.ico"))
        # self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setFixedSize(300, 300)
        self.window_pale = QPalette()
        self.window_pale.setBrush(self.backgroundRole(), QBrush(QPixmap("./img/preview2.jpg")))
        self.setPalette(self.window_pale)
        self.label_0 = QLabel('词频统计模块')
        self.label_0.setAlignment(Qt.AlignCenter)
        self.label_0.setFont(QFont('宋体', 12, QFont.Bold))
        self.frq1_button = QPushButton('年份词频统计')
        self.frq1_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq2_button = QPushButton('评分词频统计')
        self.frq2_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq3_button = QPushButton('时长词频统计')
        self.frq3_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq4_button = QPushButton('电影类型词云图')
        self.frq4_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq5_button = QPushButton('国家地区词云图')
        self.frq5_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq6_button = QPushButton('退出词频统计')
        self.frq6_button.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.frq1_button.clicked.connect(self.frq1)
        self.frq2_button.clicked.connect(self.frq2)
        self.frq3_button.clicked.connect(self.frq3)
        self.frq4_button.clicked.connect(self.frq4)
        self.frq5_button.clicked.connect(self.frq5)
        self.frq6_button.clicked.connect(self.frq6)

        # 布局
        self.v_layout = QVBoxLayout()
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.label_0)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq1_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq2_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq3_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq4_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq5_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.frq6_button)
        self.v_layout.addSpacing(10)
        self.v_layout.addStretch(1)

        self.setLayout(self.v_layout)

    def frq1(self):
        # 读取年份数据
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        year = sheet1.col_values(3)[1:]
        # 词频统计
        word_counts = dict(collections.Counter(year))
        keys = sorted(word_counts.keys())
        values = []
        for key in keys:
            values.append(word_counts.get(key))
        # 作图
        plt.figure(figsize=(20, 8), dpi=80)
        matplotlib.rc("font", family='MicroSoft YaHei', weight="bold")
        plt.bar(keys, values)
        plt.xticks(rotation=90)
        plt.xlabel('年份')
        plt.ylabel('频次')
        plt.title('年份分布统计')
        plt.grid(alpha=0.5)
        plt.show()


    def frq2(self):
        # 读取评分数据
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        score = sheet1.col_values(4)[1:]
        # 词频统计
        word_counts = dict(collections.Counter(score))
        keys = sorted(word_counts.keys())
        values = []
        for key in keys:
            values.append(word_counts.get(key))
        # 作图
        plt.figure(figsize=(20, 8), dpi=80)
        matplotlib.rc("font", family='MicroSoft YaHei', weight="bold")
        plt.bar(keys, values, color='green')
        plt.xticks(rotation=90)
        plt.xlabel('豆瓣评分')
        plt.ylabel('频次')
        plt.title('豆瓣评分分布统计')
        plt.grid(alpha=0.5)
        plt.show()

    def frq3(self):
        # 读取时长数据
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        times = sheet1.col_values(10)[1:]
        time = []
        for i in times:
            i = ''.join(i)
            i = i.split('分钟')[0]
            time.append(int(i))
        # 词频统计
        word_counts = dict(collections.Counter(time))
        keys = sorted(word_counts.keys())
        values = []
        for key in keys:
            values.append(word_counts.get(key))
        # 作图
        plt.figure(figsize=(20, 8), dpi=80)
        matplotlib.rc("font", family='MicroSoft YaHei', weight="bold")
        plt.bar(keys, values, color='pink')
        plt.xticks(rotation=90)
        plt.xlabel('电影时长/min')
        plt.ylabel('频次')
        plt.title('电影时长统计')
        plt.grid(alpha=0.5)
        plt.show()

    def frq4(self):
        # 获取电影类型字符串
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        types = sheet1.col_values(7)[1:]
        string_data = ''
        for i in types:
            string_data += i
        # 调用词云图函数
        MyCloud(string_data)

    def frq5(self):
        # 获取电影国家地区字符串
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        countries = sheet1.col_values(8)[1:]
        string_data = ''
        for i in countries:
            string_data += i
        # 调用词云图函数
        MyCloud(string_data)

    def frq6(self):
        self.close()


# GUI界面 获取情感分析界面窗口
class Motion(QWidget):
    def __init__(self):
        super(Motion, self).__init__()
        self.setWindowTitle('情感分析')
        self.setWindowIcon(QIcon("./img/shouye_.ico"))
        self.setFixedSize(400, 400)
        self.window_pale = QPalette()
        self.window_pale.setBrush(self.backgroundRole(), QBrush(QPixmap("./img/preview3.jpg")))
        self.setPalette(self.window_pale)
        self.label_0 = QLabel('电影情感分析模块')
        self.label_0.setAlignment(Qt.AlignCenter)
        self.label_0.setFont(QFont('宋体', 16, QFont.Bold))
        # 输入框
        self.shuru = QLineEdit("")
        self.shuru.setPlaceholderText('请输入需要情感分析的电影中文名称')
        self.shuru.returnPressed.connect(self.correct)
        self.shuru.setStyleSheet(
            '''QLineEdit{font-size:14px;border-radius:5px;}''')
        # 查询按钮
        self.button_1 = QPushButton(icon('fa.search', color='black'), "")
        self.button_1.clicked.connect(self.correct)
        self.button_1.setStyleSheet(
            '''QPushButton{background:white;font-size:14;border-radius:5px;}QPushButton:hover{background:#3684C8;}'''
        )
        # 退出按钮
        self.button_2 = QPushButton('退出情感分析')
        self.button_2.clicked.connect(self.close)
        self.button_2.setStyleSheet(
            '''QPushButton{font-family:'楷体';background:white;font-size:18px;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 搜索结果文本
        self.txt = QTextBrowser()

        # 水平布局
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.shuru)
        self.h_layout.addWidget(self.button_1)
        # 垂直布局
        self.v_layout = QVBoxLayout()
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.label_0)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.txt)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.button_2)
        self.v_layout.addStretch(1)

        self.setLayout(self.v_layout)

    # 搜索确认
    def correct(self):

        # 获取输入的电影名称
        shuru = self.shuru.text()
        # 在excel中获取该电影信息
        global movie_urls
        # 根据该电影排名从movie_urls中获取url，爬取热门评论10条
        # 获取输入电影名称的url并爬虫
        workbook = xlrd.open_workbook('./movie_data.xls')
        sheet1 = workbook.sheet_by_index(0)
        titles = sheet1.col_values(0)[1:]
        index = titles.index(shuru)  # 电影名称对应的索引（乱序，非排名）
        ranks = sheet1.col_values(2)[1:]
        rank_tmp = ranks[index]
        rank_index = int(rank_tmp.split('.')[1])  # 电影排名序号
        url = movie_urls[rank_index-1] + 'comments'
        # 爬取热门评论
        global proxies
        get_proxy()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
        }
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        new_comments = []
        if resp.status_code == 200:
            tree = fromstring(resp.text)
            try:
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[1]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[2]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[3]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[4]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[5]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[6]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[7]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[8]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[9]/div[2]/p/span/text()')))
                new_comments.append(''.join(tree.xpath('//*[@id="comments"]/div[10]/div[2]/p/span/text()')))
            except:
                new_comments.append('comment_error')
        else:
            print('评论爬取失败')
        # 将电影信息与评论打印输出再文本框中，并输出情感分析评分
        motion_score = []
        for i in new_comments:
            a1 = SnowNLP(i)
            # print(a1.words)  # 分词
            # print(a1.tags)  # 词性标注
            # print(a1.sentences)  # 断句
            a2 = a1.sentiments  # 获取得分
            motion_score.append(a2)
        # 作出十条评分的情感得分图
        # 作图
        plt.figure(figsize=(20, 8), dpi=80)
        matplotlib.rc("font", family='MicroSoft YaHei', weight="bold")
        x = [i for i in range(1, 11)]
        plt.plot(x, motion_score, color='green')
        plt.xlabel('评论用户')
        plt.ylabel('情感程度')
        plt.title(f'{shuru} 电影热门评论情感分析')
        plt.grid(alpha=0.5)
        plt.show()

        self.txt.setText('             --***** ' + shuru + '热门评论 *****--' + '\n①' + new_comments[0] + f'\n --****情感程度:{motion_score[0]} ****--\n②' + new_comments[1] + f'\n --****情感程度:{motion_score[1]} ****--\n③' + new_comments[2] + f'\n --****情感程度:{motion_score[2]} ****--\n④' + new_comments[3] + f'\n --****情感程度:{motion_score[3]} ****--\n⑤' + new_comments[4] + f'\n --****情感程度:{motion_score[4]} ****--\n⑥' + new_comments[5] + f'\n --****情感程度:{motion_score[5]} ****--\n⑦' + new_comments[6] + f'\n --****情感程度:{motion_score[6]} ****--\n⑧' + new_comments[7] + f'\n --****情感程度:{motion_score[7]} ****--\n⑨' + new_comments[8] + f'\n --****情感程度:{motion_score[8]} ****--\n⑩' + new_comments[9] + f'\n --****情感程度:{motion_score[9]} ****--' )

# 词频统计及词云图，需传入待处理文本字符串
def MyCloud(string_data):
    # 文本预处理
    pattern = re.compile('/|\t| |n')  # 正则匹配
    string_data = re.sub(pattern, '', string_data)  # 将符合模式的字符去除
    # 文本分词
    seg_list = jieba.cut(string_data, cut_all=False)
    # 词频统计
    word_counts = collections.Counter(seg_list)  # 对分词做词频统计
    # 绘制词云图
    mask = np.array(Image.open('./img/python_logo.jpg'))
    wc = wordcloud.WordCloud(
        font_path='C:\Windows\Fonts\STXINGKA.TTF',  # 设置字体
        mask=mask,  # 设置背景图片
        max_words=200,  # 最多显示字数
        max_font_size=250  # 字体最大值
    )
    wc.generate_from_frequencies(word_counts)  # 从字典生成词云图
    image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
    wc.recolor(color_func=image_colors)  # 将词云图颜色设置为背景图方案
    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭坐标轴
    plt.show()


# 将缓存列表里的详细数据movies导出excel，需在点击爬取数据完成后进行
def to_excel():
    try:
        global movies
        wb = xlwt.Workbook(encoding='utf-8')
        sh = wb.add_sheet("豆瓣电影top250", cell_overwrite_ok=True)
        col = ('电影名称（中文）', '电影名称（英文）', '排名', '年份', '评分', '导演', '主要演员', '类型', '国家/地区', '语言', '时长', '热门评论')
        for i in range(12):
            sh.write(0, i, col[i])
        try:
            for i in range(250):
                for j in range(12):
                    sh.write(i+1, j, movies[i][j])
        except:
            print('写入异常...')
        # save_file = 'G:\_2021秋软件课程设计\src\movie_data.xls'
        save_file = './movie_data.xls'
        wb.save(save_file)
        print('写入完成...')

    except:
        print('保存xls失败...')


# 芝麻代理获取
def get_proxy():
    global proxies
    print('开始获取代理IP地址...')
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
    zhima_url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=3&pro=&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    proxy_ip = requests.get(url=zhima_url, headers=headers)
    tmp = proxy_ip.text.replace('\r', '').replace('\n', '')
    proxies = {'https': 'http://' + tmp}

    print('代理IP地址：{}'.format(proxies))


# 启动
if __name__ == '__main__':
    page = QApplication(sys.argv)
    # 实例登录界面
    window = LoginPage()
    if not window.auto_login.isChecked():
        window.show()
    sys.exit(page.exec())
    # get_proxy()

