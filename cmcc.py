#coding:utf-8

import time
import threading
from receive import ReceiveData
from send import SendData
from datafile import DataFile
class Cmcc:
    """
    主线程
    """
    def __init__(self):
        pass

    """
    派单任务
    """
    def send_task(self,in_path="",out_path=""):
        send = SendData(in_path=in_path,out_path=out_path)
        send.run()
    
    """
    接单任务
    """
    def recv_task(self):
        recv = ReceiveData()
        recv.run()

if( __name__ == "__main__"):
    start_time = time.time()
    send_thread_list = []
    cmcc = Cmcc()
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,thread_count):
        send_thread = threading.Thread(target=cmcc.send_task,args=(path_pre+str(i)+".txt","./data/Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        send_thread_list.append(send_thread)
        time.sleep(3)

    while True:
        """
        派单模块派单后需要相应的接单模块来处理，单个接单线程可能无法满足多个派单模块的需求,暂时不确定实现方式
        """
        
        #delta = int(time.time() - start_time)
        pass

        