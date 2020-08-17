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
from datetime import datetime
import threading
from datafile import DataFile

class SendData(Base):
    """
    派工单类,负责从data.txt文件里读取工单号，登录后查询到工单,点击任务处理，选择预处理意见，设置处理时限，转派
    循环下个工单号，如果有工单在查询中出错，将放弃该工单号，重启浏览器查询下一个工单号，接单成功的单号保存到send_sucs.txt文件
    data.txt格式：
    工单单号    处理时限   #文本内容不包含表头
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/send_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password)

    """
    处理转派
    """
    def trans(self,time_limit=''):
        try:
            #接单之前选项有{查看，任务处理}，派单前选项有{查看，删除，任务处理},派单后{1-查看，2-任务处理}
            self.browser.find_element_by_xpath('//*[@class="el-dropdown-menu__item" and text()="任务处理"]').click()
            time.sleep(5)
            #获取工单详情上表头

            tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
            tabListDiv = tabList.find_elements_by_tag_name('div')
            tabListDiv = tabListDiv[0].find_elements_by_tag_name('div')
            tabListDiv[1].click()

            time.sleep(1)
            #设置工单处理时限，从文件里读取
            input_limit = self.browser.find_element_by_id("form_component_resolved_duration")
            input_limit.clear()
            input_limit.send_keys(time_limit)
            #转派
            self.browser.find_element_by_xpath('//button[@class="el-button el-button--primary el-button--mini"]/span[contains(text(),"转派")]').click()
        except Exception as e:
            print("转派出错:"+str(e))
    """
    处理工单,que是个队列，在多线程的时候，如果给一个队列，会把处理好的工单号也保存到队列里，给其他线程
    直接从队列里读取工单号
    """
    def run(self,que=None):
        input_text = None
        while True:
            if(self.login() and self.close_notice_window()):
                self.select_to_default()
                break
            else:
                self.destroy()

        while True:
            text = self.in_file.readline()
            try:
                #有些工单找不到，需要设置日期为往前一年
                time.sleep(5)
                try:
                    now = datetime.now()
                    self.browser.execute_script("var setDate=document.getElementById(\"date_picker__task_previous\");setDate.removeAttribute('readonly');")
                    self.browser.find_element_by_xpath('//input[@id="date_picker__task_previous"]').send_keys("%d-%02d-%02d"%(now.year-1,now.month,1))
                    #输入工单号
                    input_text = self.browser.find_element_by_id('public_inputCompinent__inputMainorderCode')
                except Exception as e:
                    print("加载页面到输入框出错:" + str(e))

                text=text.rstrip("\n")
                #text='ZDYH-KM-CG064-20200612-01986395'
                if(text == ""):
                    self.destroy()
                    print("所有工单处理完成")
                    break
                #保存当前工单用于异常后接着处理
                self.text = text
                input_text.clear()
                text_list = text.split('\t')
                input_text.send_keys(text_list[0])
                print("正在处理工单："+text_list[0])
                #查询工单
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #处理工单--选择工单处理菜单
                self.browser.find_element_by_class_name("tableDropdown").click()
                #处理工单--转派
                time.sleep(3)
                self.trans(text_list[1])
                if(que != None):
                    que.put(text_list[0])
                self.out_file.write(text_list[0]+'\n')
                self.out_file.flush()
                print("完成工单： "+text_list[0])
            except Exception as e:
                print("处理工单出错,接着处理工单!"+str(e))
                self.refresh()
        self.destroy()


def sendtrans_stack(in_path="",out_path=""):
    start = SendData(in_path=in_path,out_path=out_path)
    start.run()


if(__name__ == "__main__"):
    """
    start = SendData()
    start.run()
    """
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=sendtrans_stack,args=('./data/data'+str(i)+".txt","./data/Sendtrans_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(10)

    while True:
        pass