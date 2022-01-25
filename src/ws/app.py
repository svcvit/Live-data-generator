"""
ws tool for excel and pdf
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import datetime
import time
import pandas as pd

from .tool import tools

def get_localtime():
    now = datetime.datetime.now()
    # offset = datetime.timedelta(hours=2)
    start = now.strftime('%Y-%m-%d')+" 15:00:00"
    end = now.strftime('%Y-%m-%d')+" 18:00:00"
    return [start,end]



class WS(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.get_location()

        self.tool = tools(self.resources)

        main_box = toga.Box(style=Pack(padding=10))
        container = toga.OptionContainer()

        
        container_box1 = self.container_box1()


        #添加container
        container.add('观看数据生成器', container_box1)

        main_box.add(container)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


    def get_location(self):
        self.resources = self.factory.paths.app / self.factory.paths.Path("resources/")
        
    def generate_table(self):
        pass


    def container_box1(self):

        label_style = Pack(flex=1)
        style_row = Pack(direction=ROW, flex=1,padding=10)
        style_column = Pack(direction=COLUMN)
        style_flex = Pack(flex=1, 
        # font_family='monospace', font_size=14,height=20
        )
        self.now = get_localtime()
        province_list = self.tool.get_province()

        self.start_datetime = toga.MultilineTextInput(style=style_flex,initial=self.now[0])
        self.end_datetime = toga.MultilineTextInput(style=style_flex,initial=self.now[1])
        self.export_number = toga.NumberInput(style=style_flex, min_value=0, default=300)
        self.city = toga.Selection(items=province_list,style = Pack(flex=1))

        
        
        row1 = toga.Box(
            style=style_row,
            children=[
                toga.Label("输入开始时间", style=label_style),
                self.start_datetime]
        )

        row2 = toga.Box(
            style=style_row,
            children=[
                toga.Label("输入结束时间", style=label_style),
                self.end_datetime]
        )

        row3 = toga.Box(
            style=style_row,
            children=[
                toga.Label("姓名隐私保护", style=label_style),
                toga.Selection(items=["姓名加**","昵称"],style = Pack(flex=1))
            ]
        )

        row4 = toga.Box(
            style=style_row,
            children=[
                toga.Label("观看直播主要城市", style=label_style),
                self.city
            ]
        )

        row5 = toga.Box(
            style=style_row,
            children=[
                toga.Label("大概生成数量", style=label_style),
                self.export_number]
        )

        row6 = toga.Box(
            style=style_row,
            children=[
                toga.Button('生成表格',style=style_flex,on_press=self.button_click_01),  
            ]
        )


        box = toga.Box(
            style=style_column,
            children=[row1, row2,row4,row5,row6]
        )

        return box



       # 按钮功能
    #集采任务分配表
    def button_click_01(self, widget):

        province =self.city.value
        start = str(self.start_datetime.value)
        end = str(self.end_datetime.value)
        count = int(self.export_number.value)


        #获取输入数据
        date_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) 
        fname = f'直播观看数据-{date_time}.xlsx'

        output = self.tool.generate_dataset(province=province,count=count,rate=2/10,start=start,end=end)

        try:
            save_path = self.main_window.save_file_dialog(
                "保存文件",
                suggested_filename=fname)
            if save_path is not None:
                file_name_out = save_path

                with pd.ExcelWriter(file_name_out, engine='xlsxwriter') as writer:
                    output.to_excel(writer, sheet_name='Sheet1',index=False)
                    formatObj = writer.book.add_format({'num_format': 'hh:mm:ss'})
                    writer.book.sheetnames['Sheet1'].set_column('A:A',14, formatObj)
                    writer.book.sheetnames['Sheet1'].set_column('B:D',20, formatObj)
                    writer.book.sheetnames['Sheet1'].set_column('E:E',12, formatObj)
                    writer.book.sheetnames['Sheet1'].set_column('G:H',20, formatObj)
                        
                self.main_window.info_dialog('提示', '数据导出成功')
            else:
                self.main_window.info_dialog('提示', '取消数据导出')
                
        except ValueError:
            self.main_window.info_dialog('提示', '取消数据导出')


    



def main():
    return WS()
