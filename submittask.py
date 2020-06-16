#coding:utf-8

from base import Base
from userdata import UserData
import time
import os 



class SubmitTask(Base):
    """
    回工单类
    """
    def __init__(self,driver_path="./driver/chromedriver.exe",in_path="./data/data.txt",out_path="./data/submit_sucs.txt"):
        user_data = UserData()
        username,password = user_data.get_user_data(0)
        super().__init__(driver_path,in_path,out_path,username,password)

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
                    self.browser.find_element_by_class_name("tableDropdown").click()
                    #接单之前选项有{1-查看，2-任务处理},这里选择 查看 就完成接单
                    time.sleep(1)
                    self.browser.find_element_by_xpath("/html/body/ul/div[2]/li/i").click()
                    time.sleep(3)
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
                    #选择附件
                    #file_input = self.browser.find_element_by_xpath('//*[@id="online_task_upload_area"]/div[1]/input')
                    #file_input.send_keys('/home/long/Codes/cmcc_data/data/质检-附件.xlsx')
                    #self.browser.execute_script("var setDate=document.getElementById(\"formComponent_isEdit__select优化分类\");setDate.removeAttribute('readonly');")
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[7]/div[2]/div[1]/button').click()
                    time.sleep(3)
                    #上传文件
                    os.system('c:/cmcc_data/lib/upload.exe')
                    #质检按钮
                    self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[7]/button[2]/span').click()
                    time.sleep(3)
            except Exception as e:
                self.refresh()
                print("处理出错:"+str(e))
        self.destroy()

if __name__ == "__main__":
    submit_task = SubmitTask()
    submit_task.run()
