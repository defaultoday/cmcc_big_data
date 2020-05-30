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
        user_data = UserData('')
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password)
   
    """
    处理工单
    """
    def run(self):
        while True:
            if(self.Finished):
                break
            self.Finished = False
            if(self.login() and self.close_notice_window()):
                try:
                    #选择在线协作
                    self.browser.find_element_by_xpath('//*[@id="node_ZXXZ"]/i').click()
                    time.sleep(10)
                    iframe = self.browser.find_element_by_xpath('//*[@id="main_frame_01"]/iframe')
                    self.browser.switch_to_frame(iframe)
                    logo = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div')
                    ActionChains(self.browser).move_to_element(logo).click()
                    #输入工单号
                    input_text = self.browser.find_element_by_id('public_inputCompinent__inputMainorderCode')
                    while True:
                        text = self.file.readline()
                        if(text == ""):
                            self.destroy()
                            self.Finished = True
                            print("所有工单处理完成")
                            break
                        #从异常后恢复到对应的单号的下一个单号后接着处理
                        if(self.text != "" and text == self.text and self.error):
                            self.error = False
                            continue
                        if(self.text != "" and text != self.text and self.error):
                            continue
                        #保存当前工单用于异常后接着处理
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
                        #读取工单信息一部分内容，确保工单接单已完成
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
                    print("处理接单出错！")
                    self.destroy()
                    print("重新开始处理工单")
                    self.error = True



if(__name__ == "__main__"):
    start = ReceiveData()
    start.run()
