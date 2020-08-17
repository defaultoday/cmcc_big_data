#coding:utf-8

from base import Base
from userdata import UserData
import time
import os 
import win32api
import win32con
import win32gui
import threading
from datafile import DataFile



class Hangup(Base):
    """
    挂起类，选择挂起，上传附件，点击挂起
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/submit_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password,need_upload=True)

    """
    处理上传附件功能，file_path就附件的绝对路径
    """
    def upload(self, file_path):
        hld = 0
        #循环识别打开对话框，找到对话框的父句柄与初始化浏览器时获取的句柄一致时，才算是获取到正确的对话框
        while True:
            #dialog = win32gui.FindWindow('#32770', u'打开')
            dialog = win32gui.FindWindowEx(0,hld,'#32770', u'打开')
            hld = dialog
            if(win32gui.GetParent(dialog) == self.handle):
                break
        time.sleep(1)
        ComboBoxEx32 = win32gui.FindWindowEx(hld, 0, 'ComboBoxEx32', None) 
        ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
        Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
        button = win32gui.FindWindowEx(dialog, 0, 'Button', None)
        win32gui.SendMessage(Edit, win32con.WM_SETTEXT, None, file_path)
        time.sleep(1)
        win32gui.SendMessage(hld, win32con.WM_COMMAND, 1, button)  # 按button

    def run(self):
        while True:
            if(self.login() and self.close_notice_window()):
                self.select_to_default()
                break
            else:
                self.destroy()
        time.sleep(5)
        while True:
            try:
                #输入工单号
                input_text = self.browser.find_element_by_id('public_inputCompinent__inputMainorderCode')
                input_text.clear()
                text = self.in_file.readline()
                input_text.send_keys(text)
                print("正在处理工单："+text)
                text=text.rstrip("\n")
                if(text == ""):
                    self.out_file.write(text+'\n')
                    self.out_file.flush()
                    print("处理完成："+text)
                    break
                #查询工单
                time.sleep(5)
                self.browser.find_element_by_id("task_management_mat").click()
                time.sleep(5)
                #点击到驳回里
                self.browser.find_element_by_xpath('//div[@class="navContent"]/p[text()="驳回"]').click()
                time.sleep(5)
                #判断是否是当前工单号的工单
                check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                if(check.text == text):
                    #处理工单
                    try:
                        self.browser.find_element_by_class_name("tableDropdown").click()
                    except:
                        print('没有工单号：'+text)
                        continue
                    #接单之前选项有{1-查看，2-任务处理},这里选择 查看 就完成接单
                    time.sleep(1)
                    self.browser.find_element_by_xpath('//*[@class="el-dropdown-menu__item" and text()="任务处理"]').click()
                    time.sleep(3)
                    tabList = self.browser.find_element_by_class_name('el-tabs__nav-scroll')
                    tabListDiv = tabList.find_elements_by_tag_name('div')
                    tabListDiv = tabListDiv[0].find_elements_by_tag_name('div')
                    #选择地市处理
                    tabListDiv[2].click()
                    time.sleep(3)
                    #支路选择--挂起
                    self.browser.find_element_by_xpath('//input[@id="form_component_control_switch"]').click()
                    #选择挂起
                    time.sleep(1)
                    check_list = self.browser.find_elements_by_xpath('//span[text()="挂起"]')
                    check_list[0].click()
                    time.sleep(3)
                    #选择附件
                    #file_input = self.browser.find_element_by_xpath('//*[@id="online_task_upload_area"]/div[1]/input')
                    #file_input.send_keys('/home/long/Codes/cmcc_data/data/质检-附件.xlsx')
                    #self.browser.execute_script("var setDate=document.getElementById(\"formComponent_isEdit__select优化分类\");setDate.removeAttribute('readonly');")
                    self.browser.find_element_by_xpath('//button[@class="el-button el-button--primary el-button--small"]/span[contains(text(),"地市处理附件上传")]').click()
                    time.sleep(5)
                    #上传文件
                    path = os.getcwd() + '\\data\\挂起报告.docx'
                    self.upload(path)
                    time.sleep(3)
                    #挂起按钮
                    self.browser.find_element_by_xpath('//button[@class="el-button el-button--primary el-button--mini"]/span[contains(text(),"挂起")]').click()
                    time.sleep(3)
                    print("处理完成："+text)
                    self.out_file.write(text+'\n')
                    self.out_file.flush()
            except Exception as e:
                self.refresh()
                print("处理出错:"+str(e))
        self.destroy()

def hangup_stack(in_path="",out_path=""):
    start = Hangup(in_path=in_path,out_path=out_path)
    start.run()

if __name__ == "__main__":
    """
    hangup_task = Hangup()
    hangup_task.run()
    """
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=hangup_stack,args=('./data/data'+str(i)+".txt","./data/Hangup_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(10)
    
    while True:
        pass
