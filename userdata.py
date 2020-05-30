class UserData:
    """
    从../password.txt文件读取用户账号和密码
    文件格式：
    ID  USERNAME    PASSWORD

    ID取值[0,n]
    """
    def __init__(self,data_path="../password.txt"):
        self.data_path = data_path
    
    """
    通过ID获取账号和密码
    """
    def get_user_data(self,id=-1):
        username = ""
        password = ""
        file = None
        try:
            file = open(self.data_path)
            while True:
                text = file.readline()
                text = text.rstrip("\n")
                data = text.split('\t')
                if(data[0] == str(id)):
                    username = data[1]
                    password = data[2]
                    break
        except:
            print("获取账号和密码失败")
        if(file != None):
            file.close()
            file = None
        return username,password