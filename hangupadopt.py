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



class Hangupadopt(Base):
    """
    挂起通过，工单号-〉任务处理-挂起通过
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/submit_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password,need_upload=False)

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
                #判断是否是当前工单号的工单
                check = self.browser.find_element_by_xpath('//*[@id="complex_table__task_out-table"]/div[3]/table/tbody/tr[1]/td[3]/div')
                if(check.text == text):
                    #处理工单
                    try:
                        self.browser.find_element_by_class_name("tableDropdown").click()
                    except:
                        print('没有工单号：'+text)
                        continue
                    #接单之前选项有{1-查看，2-任务处理},这里选择 任务处理
                    time.sleep(1)
                    self.browser.find_element_by_xpath('//*[@class="el-dropdown-menu__item" and text()="任务处理"]').click()
                    time.sleep(5)
                    
                    #挂起通过
                    #self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[7]/button[1]/span').click()
                    self.browser.find_element_by_xpath('//button[@class="el-button el-button--primary el-button--mini"]/span[contains(text(),"挂起通过")]').click()
                    time.sleep(3)
                    print("处理完成："+text)
                    self.out_file.write(text+'\n')
                    self.out_file.flush()
            except Exception as e:
                self.refresh()
                print("处理出错:"+str(e))
        self.destroy()

def hangupadopt_stack(in_path="",out_path=""):
    start = Hangupadopt(in_path=in_path,out_path=out_path)
    start.run()

if __name__ == "__main__":
    """
    hangup_task = Hangupadopt()
    hangup_task.run()
    """
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,4):
        send_thread = threading.Thread(target=hangupadopt_stack,args=('./data/data'+str(i)+".txt","./data/Hangupadopt_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        time.sleep(10)
    
    while True:
        pass
