#coding:utf-8

import time
import threading
from receive import ReceiveData
from send import SendData
from datafile import DataFile
import queue
from receiveonline import ReceiveOnline

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
    def recv_task(self,out_path=""):
        recv = ReceiveData(out_path=out_path)
        recv.run()
    
    """
    处理在线接单任务
    """
    def recv_task_online(self,is_fast=True):
        recv = ReceiveOnline()
        recv.run(is_fast)

if( __name__ == "__main__"):
    start_time = time.time()
    que = queue.Queue()
    send_thread_list = []
    #receive_thread_list = []
    cmcc = Cmcc()
    data_path = './data/data.txt'
    path_pre = data_path[0:-4]
    thread_count = 4
    data = DataFile(data_path,thread_count)
    data.run()
    for i in range(0,thread_count):
        send_thread = threading.Thread(target=cmcc.send_task,args=(path_pre+str(i)+".txt","./data/Send_Thread"+str(i)+".txt"))
        send_thread.setDaemon(True)
        send_thread.start()
        send_thread_list.append(send_thread)
        time.sleep(3)
    #睡120秒再启动快线程
    """
    time.sleep(120)
    thread = threading.Thread(target=cmcc.recv_task_online,args=(True,))
    thread.setDaemon(True)
    thread.start()
    thread_slow = None
    """
    while True:
        pass
        """
        派单模块派单后需要相应的接单模块来处理
        """
        """
        if(receive_thread_list.count()<thread_count):
            if(que.qsize() > 10 and receive_thread_list.count() == que.qsize()//50):
                receive_thread = threading.Thread(target=cmcc.recv_task,args=("./data/receive_Thread"+str(i)+".txt"))
                receive_thread_list.append(receive_thread)
        """
        """
        可能快线程意外终止，随时检查
        """
        """
        if(not thread.is_alive()):
            thread.start()
        """
        """
        每隔半小时启动一次慢接单线程，如果该线程还没运行完就不启动，保证只有一个快接单线程和一个慢接单线程
        """
        """
        delta = (time.time() - start_time)//(30*60)
        if(delta == 1):
            start_time = time.time()
            if(thread_slow == None):
                thread_slow = threading.Thread(target=cmcc.recv_task_online,args=(False,))
                thread_slow.setDaemon(True)
                thread_slow.start()
            else:
                if(not thread_slow.is_alive()):
                    thread_slow.start()
        """



