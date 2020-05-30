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

class SendData(Base):
    """
    派工单类,负责从data.txt文件里读取工单号，登录后查询到工单点击任务处理，设置优化分类，提交
    再点击当前工单，点击任务处理，选择预处理意见，设置处理时限，转派
    循环下个工单号，如果有工单在查询中出错，将放弃该工单号，重启浏览器查询下一个工单号，接单成功的单号保存到send_sucs.txt文件
    data.txt格式：
    工单单号    处理时限   #文本内容不包含表头
    """
    def __init__(self,driver_path="./driver/send",in_path="./data/data.txt",out_path="./data/send_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(1)
        super().__init__(driver_path,in_path,out_path,username,password)

    """
    处理工单
    """
    def run(self):
        while True:
            if(self.Finished):
                break
            if(self.login() and self.close_notice_window()):
                self.Finished = False
                try:
                    #选择在线协作
                    self.browser.find_element_by_xpath('//*[@id="node_ZXXZ"]/i').click()
                    time.sleep(5)
                    iframe = self.browser.find_element_by_xpath('//*[@id="main_frame_01"]/iframe')
                    self.browser.switch_to_frame(iframe)
                    logo = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div')
                    ActionChains(self.browser).move_to_element(logo).click()
                    #有些工单找不到，需要设置日期为往前一年
                    now = datetime.now()
                    self.browser.execute_script("var setDate=document.getElementById(\"date_picker__task_previous\");setDate.removeAttribute('readonly');")
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[3]/div/div[1]/ul/div/div[2]/li/div/div[1]/input').send_keys("%d-%02d-%02d"%(now.year-1,now.month,1))
                    #输入工单号
                    input_text = self.browser.find_element_by_id('public_inputCompinent__inputMainorderCode')
                    while True:
                        text = self.file.readline()
                        text=text.rstrip("\n")
                        if(text == ""):
                            self.Finished = True
                            self.destroy()
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
                        text_list = text.split('\t')
                        input_text.send_keys(text_list[0])
                        print("正在处理工单："+text_list[0])
                        #查询工单
                        self.browser.find_element_by_id("task_management_mat").click()
                        time.sleep(5)
                        #处理工单--优化分类
                        self.browser.find_element_by_class_name("tableDropdown").click()
                        #接单之前选项有{查看，任务处理}，派单前选项有{1-查看，2-删除，3-任务处理},派单后{查看，任务处理}
                        time.sleep(1)
                        self.browser.find_element_by_xpath("/html/body/ul/div[3]/li/i").click()
                        time.sleep(5)
                        #读取工单优化分类，从文件里读取
                        dataTypeSelect = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[1]/div[2]/div/form/div[29]/div/div/div/input')
                        #如果优化分类已经有选择，就用默认选择的内容，如果没有选择就从下拉列表里选择 #1-省公司优化派单
                        if(dataTypeSelect.text == ""):
                            dataTypeSelect.click()
                            #憨定位非select下拉列表
                            dataTypeList = self.browser.find_elements_by_xpath('/html/body/div')[1]
                            dataTypeListdiv = dataTypeList.find_element_by_tag_name("div")
                            dataTypeListdiv1 = dataTypeListdiv.find_element_by_tag_name("div")
                            dataTypeListUl = dataTypeListdiv1.find_element_by_tag_name("ul")
                            dataTypeListLi = dataTypeListUl.find_elements_by_tag_name("li")
                            #优化分类共6种，取值0-5
                            #0-省公司自动触发 默认值 为空
                            #1-省公司优化派单
                            #2-地市自派-测试类
                            #3-地市自派-投诉类
                            #4-地市自派-干扰类
                            #5-地市自派-其他类
                            """
                            if(text_list[1]=="省公司自动触发"):
                                dataTypeListLi[0].click()
                            """
                            if(text_list[1]=="省公司优化派单"):
                                dataTypeListLi[1].click()
                            """
                            if(text_list[1]=="地市自派-测试类"):
                                dataTypeListLi[2].click()
                            if(text_list[1]=="地市自派-投诉类"):
                                dataTypeListLi[3].click()
                            if(text_list[1]=="地市自派-干扰类"):
                                dataTypeListLi[4].click()
                            if(text_list[1]=="地市自派-其他类"):
                                dataTypeListLi[5].click()
                            """ 
                        #提交工单
                        self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[6]/button').click()
                        #关闭工单详情
                        #self.browser.find_element_by_xpath('//*[@id="taskManagement_closeHandleTask"]').click()
                        time.sleep(1)
                        #处理工单--转派
                        #再次点击工单
                        self.browser.find_element_by_class_name("tableDropdown").click()
                        time.sleep(1)
                        #接单之前选项有{查看，任务处理}，派单前选项有{查看，删除，任务处理},派单后{1-查看，2-任务处理}
                        self.browser.find_element_by_xpath("/html/body/ul/div[2]/li/i").click()
                        #获取工单详情上表头
                        tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                        tabListDiv = tabList.find_elements_by_tag_name('div')[2]
                        tabListDiv.click()
                        time.sleep(1)
                        #设置工单处理时限，从文件里读取
                        input_limit = self.browser.find_element_by_id("formComponent_isEdit__resolved_duration")
                        input_limit.clear()
                        input_limit.send_keys(text_list[1])
                        #转派
                        self.browser.find_element_by_xpath('//*[@id="online_task_handle_area"]/button').click()
                        #关闭工单详情
                        #self.browser.find_element_by_xpath('//*[@id="taskManagement_closeHandleTask"]').click()
                        self.out_file.write(text_list[0])
                        self.out_file.flush()
                        time.sleep(1)
                        print("完成工单： "+text_list[0])

                except:
                    print("处理工单出错,重新开始处理工单!")
                    self.destroy()
                    self.error = True




if(__name__ == "__main__"):
    start = SendData()
    start.run()
