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
import threading
from datafile import DataFile

class ReceiveData(Base):
    """
    接工单类,负责从send_sucs.txt文件里读取工单号，登录后查询到工单点击查看>关闭工单，循环下个工单号，
    如果有工单在查询中出错，将放弃该工单号，重启浏览器查询下一个工单号，接单成功的单号保存到receive_sucs.txt文件
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/receive_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password,need_upload=False)

    
    """
    处理工单,que是个队列，从其他线程处理结果中读取工单号
    """
    def run(self,que=None):
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
            text = ""
            if(que is None):
                text = self.in_file.readline()
            elif que.qsize()>0:
                text = que.get()
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
                #判断是否是当前工单号的工单
                check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                if(check.text == text):
                    #处理工单
                    self.browser.find_element_by_class_name("tableDropdown").click()
                    #接单之前选项有{1-查看，2-任务处理},这里选择 查看 就完成接单
                    time.sleep(1)
                    self.browser.find_element_by_xpath('//*[@class="el-dropdown-menu__item" and text()="查看"]').click()
                    time.sleep(10)
                    tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                    tabListDiv = tabList.find_elements_by_tag_name('div')[1]
                    if(tabListDiv is None):
                        print("工单接单出错："+ text)
                    else:
                        #关闭工单信息窗口，如果工单信息正常打开，关闭按钮不会出错
                        self.browser.find_element_by_id("taskManagement_closeHandleTask").click()
                        print("完成工单： "+text)
                        self.out_file.write(text+'\n')
                        self.out_file.flush()
                        time.sleep(3)
            except Exception as e:
                print("处理工单出错,接着处理工单!" + str(e))
                self.refresh()


def recv_stack(in_path="",out_path=""):
    start = ReceiveData(in_path=in_path,out_path=out_path)
    start.run()

if(__name__ == "__main__"):
    """
    start = ReceiveData()
    start.run()
    """
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=recv_stack,args=('./data/data'+str(i)+".txt","./data/Recv_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(3)
    

    while True:
        pass
