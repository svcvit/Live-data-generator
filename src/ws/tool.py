import pandas as pd

from faker import Faker
import random
import os
import numpy as np
import datetime
import arrow


class tools():
    def __init__(self,path):
        self.path = str(path)

    def get_province(self):
        ip_data = pd.read_feather(self.path+'/ip_data.feather')
        return list(ip_data['province'].unique())


    def get_datetime(self,input_datetime = '2022-01-19 15:00:00',count=300):
        
        mid_datetime = arrow.get(input_datetime).naive
        s = list(np.random.randint(-10*60,10*60,size=count))
        
        datatime_list = []
        for item in s:
            offset = datetime.timedelta(seconds=int(item))
            time = mid_datetime + offset
            datatime_list.append(time)
        return datatime_list


    def createRandomString(self,len):

        result = []
        for i in range (len):

            raw = ""
            range1 = range(58, 65) # between 0~9 and A~Z
            range2 = range(91, 97) # between A~Z and a~z

            i = 0
            while i < 12:
                seed = random.randint(48, 122)
                if ((seed in range1) or (seed in range2)):
                    continue
                raw += chr(seed)
                i += 1
            result.append(raw)
        return result

    def long2ip(self,long):
        floor_list=[]
        yushu=long
        for i in reversed(range(4)):   #3,2,1,0
            res=divmod(yushu,256**i)
            floor_list.append(str(res[0]))
            yushu=res[1]
        return '.'.join(floor_list)


    def get_fakename(self,number=300):
        result =[]
        fake = Faker(['zh_CN'])
        for _ in range(number):
            result.append(fake.name())
        return result

    def get_nickname(self,number=300):
        table = pd.read_excel(self.path+'/nickname.xlsx')
        result = random.sample(list(table['nickname']), number)
        return result

    def get_ramdon_ip(self,ip=16777472):
        offset = random.randint(1,254)
        ip_address = ip+offset
        return self.long2ip(ip_address)

    def generate_dataset(self,province="上海市",count=300,rate=2/10,start='2022-01-19 15:00:00',end='2022-01-19 18:00:00'):
        ip_data = pd.read_feather(self.path+'/ip_data.feather')
        selected_ip = ip_data[ip_data['province']==province]
        out_selected_ip = ip_data[ip_data['province']!=province]

        if len(selected_ip) >= count:
            #随机抽样
            order = np.random.randint(0,len(selected_ip),size=count)
            #通过随机抽样抽取DataFrame中的行
            newDf = selected_ip.take(order)
        else:
            loop = int(count/len(selected_ip))
            newDf = selected_ip
            for i in range(loop):
                newDf = pd.concat([newDf,selected_ip],sort=False)
        
        out_numbner = int(count*rate)
        order_out = np.random.randint(0,len(out_selected_ip),size=out_numbner)
        newDf_out = out_selected_ip.take(order_out)

        newDf = pd.concat([newDf,newDf_out],sort=False)
        newDf['ip'] = newDf['ip_start_num'].apply(self.get_ramdon_ip)
        result = newDf[['province','city','location','ip']]

        ramdom_result = result.take(np.random.permutation(len(result))).reset_index(drop=True)
        
        nickname = self.get_nickname(len(ramdom_result))
        enter_time = self.get_datetime(start,len(ramdom_result))
        out_time = self.get_datetime(end,len(ramdom_result))

        id = self.createRandomString(len(ramdom_result))

        df_nickname = pd.DataFrame({'id':id,'nickname':nickname,'enter_time':enter_time,'out_time':out_time}).reset_index(drop=True)
        new = pd.concat([ramdom_result,df_nickname],axis=1, sort=False)
        new['during_time'] = new['out_time']-new['enter_time']

        new['during_time'] = new['during_time'].dt.seconds/(24*60*60)
        

        new['enter_time'] = new['enter_time'].dt.tz_localize(None)
        new['out_time'] = new['out_time'].dt.tz_localize(None)
        
        output =new.rename(columns={"id":"ID", "nickname":"昵称", "enter_time":"进入时间", 
        "out_time":"退出时间","during_time":"在线时长","province":"省份","city":"城市","ip":"IP地址"
        })

        output=output[['ID','昵称','进入时间','退出时间','在线时长','省份','城市','IP地址']]
            
        return  output

    

