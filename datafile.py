#coding:utf-8

class DataFile:
    """
    把工单文件分割成多thread_count个文件，提供给线程使用，总文件data_path
    """
    def __init__(self,data_path='./data/data.txt',thread_count=4):
        self.data_path = data_path
        self.thread_count = thread_count

    def run(self):
        try:
            file = open(self.data_path,encoding='utf-8')
            datas = file.readlines()
            file.close()
            file = None
            data_len = len(datas)
            count = int(data_len/self.thread_count)
            print('正在分割数据')
            for i in range(0,self.thread_count):
                thread_file = open(self.data_path[0:-4]+str(i)+".txt","w+")
                if(i == self.thread_count-1):
                    for n in range(i*count,data_len):
                        thread_file.write(datas[n])
                else:
                    for n in range(i*count,(i+1)*count):
                        thread_file.write(datas[n])
                thread_file.flush()
                thread_file.close()
                thread_file = None
            print('数据分割完成')
        except Exception as e:
            print("处理文件出错:"+str(e))


if __name__ == "__main__":
    data = DataFile('./data/data.txt',4)
    data.run()