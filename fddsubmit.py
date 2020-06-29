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

class FDDSubmit(Base):
    """
    fdd质检类，输入工单，直接搜索，搜索结果可能出现在待办或是驳回里，找到工单后，执行任务处理
    选择支路为“质检”，填写原因归类、产生原因和处理描述，最后点击质检按钮
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/fddsubmit_sucs.txt"):
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
                data_arr = text.split('\t')
                self.text = data_arr[0]
                input_text.clear()
                input_text.send_keys(self.text)
                print("正在处理工单："+self.text)
                #查询工单
                time.sleep(5)
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #检查是待办还是驳回
                opt = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[2]/ul/div[1]/li/div/div/i')
                if(opt.text != '0'):
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[2]/ul/div[1]/li/div/p').click()
                else:
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[2]/ul/div[3]/li/div/p').click()
                time.sleep(5)
                #判断是否是当前工单号的工单
                check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                if(check.text == self.text):
                    #处理工单
                    self.browser.find_element_by_class_name("tableDropdown").click()
                    #接单之前选项有{1-查看，2-任务处理},这里选择 任务处理
                    time.sleep(1)
                    self.browser.find_element_by_xpath("/html/body/ul/div[2]/li/i").click()
                    time.sleep(5)
                    tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                    tabListDiv = tabList.find_elements_by_tag_name('div')
                    tabListDiv = tabListDiv[0].find_elements_by_tag_name('div')
                    #选择地市处理
                    tabListDiv[2].click()
                    time.sleep(3)
                    #支路选择
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[3]/div[2]/div/div/form/div[1]/div/div/div[1]/input').click()
                    #选择质检
                    time.sleep(1)
                    check_list = self.browser.find_elements_by_xpath('//span[text()="质检"]')
                    check_list[0].click()
                    time.sleep(3)
                    #再次点击地市处理，为了确保选择质检之后留下一个没有内容的选择框
                    tabListDiv[2].click()
                    #填写工单信息
                    #原因归类
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[3]/div[2]/div/div/form/div[2]/div/div/div/input').click()
                    if(data_arr[1] == '覆盖类'):
                        self.browser.find_element_by_xpath('//span[text()="覆盖类"]').click()
                    elif(data_arr[1] == '故障类'):
                        self.browser.find_element_by_xpath('//span[text()="故障类"]').click()
                    elif(data_arr[1] == '干扰类'):
                        self.browser.find_element_by_xpath('//span[text()="干扰类"]').click()
                    elif(data_arr[1] == '参数类'):
                        self.browser.find_element_by_xpath('//span[text()="参数类"]').click()
                    elif(data_arr[1] == '邻区类'):
                        self.browser.find_element_by_xpath('//span[text()="邻区类"]').click()
                    elif(data_arr[1] == '终端类'):
                        self.browser.find_element_by_xpath('//span[text()="终端类"]').click()
                    elif(data_arr[1] == '核心网类'):
                        self.browser.find_element_by_xpath('//span[text()="核心网类"]').click()
                    elif(data_arr[1] == '其他'):
                        self.browser.find_element_by_xpath('//span[text()="其他"]').click()
                    elif(data_arr[1] == '资源类'):
                        self.browser.find_element_by_xpath('//span[text()="资源类"]').click()
                    elif(data_arr[1] == '容量类'):
                        self.browser.find_element_by_xpath('//span[text()="容量类"]').click()
                    #填写产生原因
                    input_case = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[3]/div[2]/div/div/form/div[3]/div/div/input')
                    input_case.clear()
                    input_case.send_keys(data_arr[2])
                    #填写处理描述
                    input_case = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[3]/div[2]/div/div/form/div[4]/div/div/input')
                    input_case.clear()
                    input_case.send_keys(data_arr[2])

                    #质检按钮
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[6]/button[3]/span').click()
                    self.out_file.write(text+'\n')
                    self.out_file.flush()
                    time.sleep(3)
                        
            except:
                print("处理工单出错,接着处理工单!")
                self.refresh()


def fddsubmit_stack(in_path="",out_path=""):
    start = FDDSubmit(in_path=in_path,out_path=out_path)
    start.run()

if(__name__ == "__main__"):
    
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=fddsubmit_stack,args=('./data/data'+str(i)+".txt","./data/FDDSubmit_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(3)
    """
    start = FDDSubmit(in_path='./data/data.txt',out_path='./data/FDDSubmit_Thread.txt')
    start.run()
    """
    while True:
        pass
