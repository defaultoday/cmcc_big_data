#coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
#from selenium.webdriver.support import WebDriverWait
import selenium.webdriver.support.wait as W
from selenium.webdriver.support import expected_conditions as E
from selenium.webdriver.common.by import By
#from selenium.webdriver.support import expected_conditions
from base import Base
from userdata import UserData

class ReceiveData(Base):
    """
    接工单类,负责从send_sucs.txt文件里读取工单号，登录后查询到工单点击查看>关闭工单，循环下个工单号，
    如果有工单在查询中出错，将放弃该工单号，重启浏览器查询下一个工单号，接单成功的单号保存到receive_sucs.txt文件
    """
    def __init__(self,driver_path="./driver/receive",in_path="./data/send_sucs.txt",out_path="./data/receive_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password)
   
    """
    处理工单
    """
    def run(self):
        while True:
            if(self.login() and self.close_notice_window()):
                self.select_to_default()
                break
            else:
                self.destroy()
        while True:
            #输入工单号
            input_text = self.browser.find_element_by_id('public_inputCompinent__inputMainorderCode')
            input_text.clear()
            text = self.in_file.readline()
            try:
                if(text == ""):
                    self.destroy()
                    print("所有工单处理完成")
                    break
                #保存当前工单用于异常后接着处理
                text=text.rstrip("\n")
                self.text = text
                input_text.clear()
                input_text.send_keys(self.text)
                print("正在处理工单："+text)
                #查询工单
                time.sleep(5)
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #处理工单
                self.browser.find_element_by_class_name("tableDropdown").click()
                #接单之前选项有{1-查看，2-任务处理},这里选择 查看 就完成接单
                time.sleep(1)
                self.browser.find_element_by_xpath("/html/body/ul/div[1]/li/i").click()
                time.sleep(10)
                """"
                读取工单信息一部分内容，确保工单接单已完成
                工单信息中没有工单单号，这里读取工单表头用来确定接单是否成功，可能会出现误判：
                输入一个工单号，点击搜索后，10秒内还没有搜索出来的话，搜索结果里的工单还是上一条工单，点击tableDropdown弹出菜单，
                再点击查看item,读取到的就上一个工单的信息，因此，这个单号就会误判为接单成功，
                """
                tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                tabListDiv = tabList.find_elements_by_tag_name('div')[1]
                if(tabListDiv is None):
                    print("工单接单出错："+ text)
                else:
                    #关闭工单信息窗口，如果工单信息正常打开，关闭按钮不会出错
                    self.browser.find_element_by_id("taskManagement_closeHandleTask").click()
                    print("完成工单： "+text)
                    self.out_file.write(text)
                    self.out_file.flush()
                    time.sleep(3)
            except:
                self.refresh()
                print("处理工单出错,接着处理工单!")



if(__name__ == "__main__"):
    start = ReceiveData()
    start.run()
