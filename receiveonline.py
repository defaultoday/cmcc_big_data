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

class ReceiveOnline(Base):
    """
    接工单类,负责在想一直刷新中端优化市场第三方页面，如果接单时间为空就点击查看，在线监控接单，由快线程一直接工单页面第一页的工单
    慢线程每隔半小时启动检查2-4页工单
    """
    def __init__(self,driver_path="./driver/chromedriver"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path=driver_path,in_path="",out_path="",username=username,password=password)
    """
    循环接一个页面没有接单日期的工单
    """
    def recv_check(self):
        #判断是否是当前工单号的工单
        check = self.browser.find_elements_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr')
        if(check.__len__() > 0):
            for i in range(0,check.__len__()):
                ActionChains(self.browser).move_to_element(check[i]).perform()
                item = check[i].find_elements_by_tag_name('td')
                #如果item接单时间为空，就点击工单上的菜单按钮，弹出菜单
                if(item[4].text == ""):
                    ActionChains(self.browser).move_to_element(item[1]).perform()
                    #item[1].click()
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div[1]/div/div[3]/table/tbody/tr['+str(i+1)+']/td[2]/div/div/div/div/span').click()
                    #接单之前选项有{1-查看，2-任务处理},这里选择 查看 就完成接单
                    time.sleep(1)
                    self.browser.find_element_by_xpath("/html/body/ul/div[1]/li/i").click()
                    """
                    if(i==0):
                        self.browser.find_element_by_xpath("/html/body/ul/div[1]/li/i").click()
                    else:
                        self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div[1]/div/div[3]/table/tbody/tr['+ str(i+1) +']/td[2]/div/div/div/div/ul/div[1]/li/i').click()
                    """
                    time.sleep(5)
                    tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                    tabListDiv = tabList.find_elements_by_tag_name('div')[1]
                    if(tabListDiv != None):
                        #关闭工单信息窗口，如果工单信息正常打开，关闭按钮不会出错
                        self.browser.find_element_by_id("taskManagement_closeHandleTask").click()
                        time.sleep(3) 
    """
    在线程中，一个监控工单页面第一页，出现没有接单日期的工单，立马接单
    """
    def recv_fast(self):
        while True:
            try:
                self.browser.find_element_by_id('process_select__task').click()
                time.sleep(3)
                self.browser.find_element_by_xpath('//*[@id="mid_optimizing_city_outsourcing"]/span').click()
                time.sleep(1)
                #查询工单
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(10)
                self.recv_check()
            except Exception as e:
                self.refresh()
                print("处理工单出错,接着处理工单!"+str(e))
    
    """
        慢速接单，在线程中用来半小时启动一次，检查2-4页工单是否有遗漏没有接单
    """
    def recv_slow(self):
        try:
            self.browser.find_element_by_id('process_select__task').click()
            time.sleep(3)
            self.browser.find_element_by_xpath('//*[@id="mid_optimizing_city_outsourcing"]/span').click()
            time.sleep(1)
            #查询工单
            self.browser.find_element_by_id("task_management_mat").click()
            time.sleep(10)
            items = self.browser.find_elements_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/div[2]/div/div/ul/li')
            #检查1-4页
            for page in range(1,5):
                items[page].click()
                time.sleep(10)
                self.recv_check()
        except:
            print("处理工单出错，接着处理工单！")


    """
    处理工单,从其他线程处理结果中读取工单号,is_fast默认就快线程，快线程只有一个，一直在线刷新工单第一页，
    没有接单时间的立马接单
    如果is_fast=False，是慢线程，每隔半个小时启动一次检查，检查2-4页，如果快线程有接单误判，就又慢线程来检查遗漏，如果
    半小时没有检查完，也不会启动新的慢线程，保证一个时间内只有一个快线程和最多一个慢线程
    """
    def run(self,is_fast=True):
        while True:
            if(self.login() and self.close_notice_window()):
                self.select_to_default()
                break
            else:
                self.destroy()
        
        if(is_fast):
            self.recv_fast()
        else:
            self.recv_slow()

        self.destroy()



if(__name__ == "__main__"):
    start = ReceiveOnline()
    start.run()
