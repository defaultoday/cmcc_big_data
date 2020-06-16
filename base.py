#coding:utf-8

from abc import abstractmethod,ABC
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

class Base(ABC):
    """
    处理工单基类，run函数为为处理流程函数，需要在子类中实现
    """
    url = "http://10.174.240.17:8081/portal/pure/Frame.action"

    def __init__(self,driver_path="",in_path="",out_path="",username="",password=""):
        self.username = username
        self.password = password
        #驱动路径，默认值为：chromedriver
        self.driver_path = driver_path
        self.browser = None
        #工单文件路径，文本文件，默认一行一个工单号
        self.in_path = in_path
        self.in_file = None
        #接单成功保存单号到该文件
        self.out_path = out_path
        self.out_file = None
        #保存当前读取到的工单号
        self.text = ""
    """
    初始化工单文件
    """
    def init_data(self):
        print("初始化文件：IN："+self.in_path+" OUT:"+self.out_path)
        #需要处理没有输入和输出文件的情况
        if(self.in_path != ""): 
            if(self.in_file == None):
                try:
                    self.in_file = open(self.in_path)
                except:
                    print("加载工单文件出错！")
                    return False
        if(self.out_path != ''):
            if(self.out_file == None):
                try:
                    self.out_file = open(self.out_path,"w+")
                except:
                    print("加载输出文件错误")
                    return False
        return True
    """
    获取浏览器，同一上下文只允许一个浏览器
    """
    def init_browser(self):
        if(self.init_data() == False):
            return False
        if(self.browser == None):
            try:
                if(self.driver_path == ""):
                    self.browser = webdriver.Chrome()
                else:
                    self.browser = webdriver.Chrome(self.driver_path)
            except Exception as e:
                print("初始化浏览器失败！请关闭已打开的浏览器！"+ str(e))
        if(self.browser != None):
            self.browser.implicitly_wait(15)
        return self.browser
    """
    登录操作
    """
    def login(self):
        if(self.init_browser()):
            try:
                self.browser.get(self.url)
                self.browser.find_element_by_id("username").send_keys(self.username)
                self.browser.find_element_by_id("password").send_keys(self.password)
                self.browser.find_element_by_class_name("btn-submit").click()
            except:
                print("登录出错")
                return False
        return True
    """
    登录或刷新完成需要关闭提示窗口，现在除了登录用到之外，可能暂时不怎么用到，可能以后刷新用到
    """
    def close_notice_window(self):
        if(self.browser != None):
            time.sleep(3)
            try:
                self.browser.find_element_by_class_name("sys-window-btn-close").click()
            except:
                print("关闭提示窗口失败")
                return False
        return True

    """
    异常后关闭文件和浏览器
    """
    def destroy(self):
        print("关闭浏览器和文件: IN:"+self.in_path+" OUT:"+self.out_path)
        if(self.browser != None):
            try:
                self.browser.quit()
            except:
                print("关闭浏览器出错！")
            
        self.browser = None
        if(self.in_file != None):
            try:
                self.in_file.close()
            except:
                print("关闭文件出错！")
            
        self.file = None
        if(self.out_file != None):
            try:
                self.out_file.close()
            except:
                print("关闭输出文件错误")
        self.out_file = None
    
    """
    刷新环境，处理出错后刷新重新处理
    """
    def refresh(self):
        self.browser.refresh()
        time.sleep(3)
        self.close_notice_window()
        time.sleep(3)
        self.select_to_default()

    """
    刷新后需要选择到默认界面
    """
    def select_to_default(self):
        try:
            #选择在线协作
            self.browser.find_element_by_xpath('//*[@id="node_ZXXZ"]/i').click()
            time.sleep(5)
            iframe = self.browser.find_element_by_xpath('//*[@id="main_frame_01"]/iframe')
            self.browser.switch_to_frame(iframe)
            logo = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div')
            ActionChains(self.browser).move_to_element(logo).click()
        except:
            print("选择默认界面失败")

    """
    处理任务函数,每个模块需要有单独的自己实现
    """
    @abstractmethod
    def run(self):
        pass
