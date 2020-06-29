#coding:utf-8

"""
df = pd.read_excel('./test.xlsx')
df2 = pd.read_excel('./2.xlsx')
df3 = df.set_index(['名字'])[~df.set_index(['名字']).isin(df2.set_index(['名字'])).all(1)].reset_index()

for i in range(0,df.shape[0]):
    print(df.values[i][0])

print(df3.iloc[0,0])

#df.to_excel('2.xlsx')

"""
from base import Base
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import win32api
import win32con
import win32gui
import os


print(os.getcwd() + '\\data\\质检-附件.xlsx')

browser = webdriver.Chrome('./driver/chromedriver.exe')
browser.get('C:/Users/long/Desktop/cmcc/cmcc_data/test.html')
win = win32gui.FindWindow('Chrome_WidgetWin_1',None)

handle_list = []
win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), handle_list)
for handle in handle_list:
    handle_class = win32gui.GetClassName(handle)
    if(handle_class =='Chrome_WidgetWin_1'):
        print("%#x"%handle+" "+handle_class)
    else:
        handle_list.remove(handle)
browser.refresh()
print(handle_list)

browser.title = 'yyy'
print(browser.title)
parent_id = browser.current_window_handle
#upload_button = browser.find_element_by_id('uploadfile')
#upload_button.click
all_windows = browser.window_handles
print(all_windows+parent_id)

