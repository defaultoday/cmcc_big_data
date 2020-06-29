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
from datetime import datetime

class Archive(Base):
    """
    归档类，输入工单号，设置更新时间往前一年，查询工单-〉任务处理-〉归档
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/archive_sucs.txt"):
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
        time.sleep(5)
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
                #设置时间往前一年
                now = datetime.now()
                self.browser.execute_script("var setDate=document.getElementById(\"date_picker__task_previous\");setDate.removeAttribute('readonly');")
                self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[3]/div/div[1]/ul/div/div[2]/li/div/div[1]/input').send_keys("%d-%02d-%02d"%(now.year-1,now.month,1))
                #查询工单
                time.sleep(5)
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #判断是否是当前工单号的工单
                check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                if(check.text == text):
                    #处理工单
                    self.browser.find_element_by_class_name("tableDropdown").click()
                    #接单之前选项有{1-查看，2-任务处理},这里选择 任务处理
                    time.sleep(1)
                    self.browser.find_element_by_xpath("/html/body/ul/div[2]/li/i").click()
                    time.sleep(5)
                    #归档按钮
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[8]/button[2]/span').click()
                    self.out_file.write(text+'\n')
                    self.out_file.flush()
                    time.sleep(3)
                        
            except:
                print("处理工单出错,接着处理工单!")
                self.refresh()


def archive_stack(in_path="",out_path=""):
    start = Archive(in_path=in_path,out_path=out_path)
    start.run()

if(__name__ == "__main__"):
    
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=archive_stack,args=('./data/data'+str(i)+".txt","./data/Archive_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(3)
    """
    start = Archive(in_path='./data/data.txt',out_path='./data/Archive_Thread.txt')
    start.run()
    """
    while True:
        pass
