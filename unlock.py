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

class UnlockCheck(Base):
    """
    实现解挂流程
    """
    def __init__(self,driver_path="./driver/chromedriver",in_path="./data/data.txt",out_path="./data/unload_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password)

    def select_to_default(self):
        try:
            self.browser.find_element_by_xpath('//*[@id="node_ZXXZ"]/i').click()
            time.sleep(5)
            iframe = self.browser.find_element_by_xpath('//*[@id="main_frame_01"]/iframe')
            self.browser.switch_to_frame(iframe)
            logo = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div')
            ActionChains(self.browser).move_to_element(logo).click()
            self.browser.find_element_by_xpath('//input[@id="defaultSelect_balackParamsorder_type__task"]').click()
            time.sleep(3)
            self.browser.find_element_by_xpath('//span[text()="中端优化"]').click()
            time.sleep(20)
            return True
        except Exception as e:
            print('跳转到默认窗口出错：'+str(e))
            return False

    def refresh(self):
        self.browser.refresh()
        time.sleep(3)
        self.close_notice_window()
        time.sleep(3)
        self.select_to_default()


    """
    处理工单,que是个队列，从其他线程处理结果中读取工单号
    """
    def run(self,que=None):
        while True:
            if(self.login() and self.close_notice_window()):
                if(self.select_to_default() == True):
                    break
            else:
                self.destroy()
        while True:
            #解挂标签
            #self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[2]/ul/div[3]/li/div/p').click()
            #time.sleep(5)
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
                print("正在处理工单："+self.text)
                now = datetime.now()
                self.browser.execute_script("var setDate=document.getElementById(\"date_picker__task_previous\");setDate.removeAttribute('readonly');")
                date_input = self.browser.find_element_by_xpath('//input[@id="date_picker__task_previous"]')
                date_input.clear()
                date_input.send_keys("%d-%02d-%02d"%(now.year-1,now.month,1))
                #查询工单
                time.sleep(5)
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #挂起标签
                self.browser.find_element_by_xpath('//p[text()="挂起"]').click()
                time.sleep(5)
                #判断是否是当前工单号的工单
                #check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                #弹出菜单
                try:
                    self.browser.find_element_by_class_name("tableDropdown").click()
                except:
                    print('没有工单：'+self.text+'\n')
                    continue
                time.sleep(1)
                
                #接单之前选项有{查看，任务处理}，派单前选项有{查看，删除，任务处理},派单后{1-查看，2-任务处理}
                self.browser.find_element_by_xpath('//li[@class="el-dropdown-menu__item" and text()="任务处理"]').click()
                time.sleep(5)
                #获取工单详情上表头 选择地市处理

                tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                tabListDiv = tabList.find_elements_by_tag_name('div')
                tabListDiv = tabListDiv[0].find_elements_by_tag_name('div')
                tabListDiv[2].click()

                time.sleep(1)
                #设置工单处理时限，从文件里读取
                #设置工单信息
                input_txt = self.browser.find_element_by_xpath('//textarea[@id="form_component_on_site_ack"]')
                input_txt.clear()
                input_txt.send_keys('1')
                input_txt = self.browser.find_element_by_xpath('//textarea[@id="form_component_measures_to_implement"]')
                input_txt.clear()
                input_txt.send_keys('1')
                input_txt = self.browser.find_element_by_xpath('//textarea[@id="form_component_effect_ack"]')
                input_txt.clear()
                input_txt.send_keys('1')
                #设置工单类型
                self.browser.find_element_by_xpath('//span[@class="el-radio__label" and contains(text(),"覆盖类")]').click()
                
                time.sleep(1)
                #解挂按钮
                self.browser.find_element_by_xpath('//button[@class="el-button el-button--primary el-button--mini"]/span[contains(text(),"解挂")]').click()
            
                self.out_file.write(self.text+'\n')
                self.out_file.flush()
                print('处理完成：'+self.text+'\n')
                

            except Exception as e:
                print("处理工单出错,接着处理工单!" + str(e))
                self.refresh()
        self.destroy()    


def unlockcheck_stack(in_path="",out_path=""):
    start = UnlockCheck(in_path=in_path,out_path=out_path)
    start.run()

if(__name__ == "__main__"):
    
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()

    for i in range(0,thread_count):
        send_thread = threading.Thread(target=unlockcheck_stack,args=(path_pre+str(i)+".txt","./data/Unlock_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(3)
    
    #start = UnlockCheck(in_path='./data/data.txt',out_path='./data/unlockcheck_sucs.txt')
    #start.run()
    while True:
        pass
