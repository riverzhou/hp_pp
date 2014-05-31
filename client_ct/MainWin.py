#!/usr/bin/env python3

from tkinter        import *

#geometry('591x592+650+150')

GEOMETRY = '591x592+650+150'


class Console:
    def __init__(self, master=None):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 
        font12 = "-family 微软雅黑 -size 12 -weight normal -slant roman  " + \
            "-underline 0 -overstrike 0"
        master.configure(background=_bgcolor)
        master.configure(highlightbackground="#d9d9d9")
        master.configure(highlightcolor="black")


        self.frame_bid = Frame (master)
        self.frame_bid.place(relx=0.07,rely=0.52,relheight=0.41,relwidth=0.85)
        self.frame_bid.configure(relief=GROOVE)
        self.frame_bid.configure(borderwidth="2")
        self.frame_bid.configure(relief=GROOVE)
        self.frame_bid.configure(background=_bgcolor)
        self.frame_bid.configure(highlightbackground="#d9d9d9")
        self.frame_bid.configure(highlightcolor="black")
        self.frame_bid.configure(width=505)

        self.button_image_warmup = Button (self.frame_bid)
        self.button_image_warmup.place(relx=0.24,rely=0.08,height=35,width=79)
        self.button_image_warmup.configure(activebackground="#d9d9d9")
        self.button_image_warmup.configure(activeforeground="#000000")
        self.button_image_warmup.configure(background=_bgcolor)
        self.button_image_warmup.configure(disabledforeground="#a3a3a3")
        self.button_image_warmup.configure(font=font12)
        self.button_image_warmup.configure(foreground="#000000")
        self.button_image_warmup.configure(highlightbackground="#d9d9d9")
        self.button_image_warmup.configure(highlightcolor="black")
        self.button_image_warmup.configure(pady="0")
        self.button_image_warmup.configure(text='''图片预热''')
        self.button_image_warmup.bind('<Button-1>',self.button_image_warmup_clicked)

        self.button_price_warmup = Button (self.frame_bid)
        self.button_price_warmup.place(relx=0.55,rely=0.08,height=35,width=79)
        self.button_price_warmup.configure(activebackground="#d9d9d9")
        self.button_price_warmup.configure(activeforeground="#000000")
        self.button_price_warmup.configure(background=_bgcolor)
        self.button_price_warmup.configure(disabledforeground="#a3a3a3")
        self.button_price_warmup.configure(font=font12)
        self.button_price_warmup.configure(foreground="#000000")
        self.button_price_warmup.configure(highlightbackground="#d9d9d9")
        self.button_price_warmup.configure(highlightcolor="black")
        self.button_price_warmup.configure(pady="0")
        self.button_price_warmup.configure(text='''价格预热''')
        self.button_price_warmup.bind('<Button-1>',self.button_price_warmup_clicked)

        self.input_image_price = Entry (self.frame_bid)
        self.input_image_price.place(relx=0.3,rely=0.37,relheight=0.1
                ,relwidth=0.36)
        self.input_image_price.configure(background="white")
        self.input_image_price.configure(disabledforeground="#a3a3a3")
        self.input_image_price.configure(font=font12)
        self.input_image_price.configure(foreground="#000000")
        self.input_image_price.configure(highlightbackground="#d9d9d9")
        self.input_image_price.configure(highlightcolor="black")
        self.input_image_price.configure(insertbackground="black")
        self.input_image_price.configure(selectbackground="#c4c4c4")
        self.input_image_price.configure(selectforeground="black")

        self.input_image_number = Entry (self.frame_bid)
        self.input_image_number.place(relx=0.3,rely=0.65,relheight=0.1
                ,relwidth=0.36)
        self.input_image_number.configure(background="white")
        self.input_image_number.configure(disabledforeground="#a3a3a3")
        self.input_image_number.configure(font=font12)
        self.input_image_number.configure(foreground="#000000")
        self.input_image_number.configure(highlightbackground="#d9d9d9")
        self.input_image_number.configure(highlightcolor="black")
        self.input_image_number.configure(insertbackground="black")
        self.input_image_number.configure(selectbackground="#c4c4c4")
        self.input_image_number.configure(selectforeground="black")

        self.button_image_price = Button (self.frame_bid)
        self.button_image_price.place(relx=0.75,rely=0.37,height=35,width=95)
        self.button_image_price.configure(activebackground="#d9d9d9")
        self.button_image_price.configure(activeforeground="#000000")
        self.button_image_price.configure(background=_bgcolor)
        self.button_image_price.configure(disabledforeground="#a3a3a3")
        self.button_image_price.configure(font=font12)
        self.button_image_price.configure(foreground="#000000")
        self.button_image_price.configure(highlightbackground="#d9d9d9")
        self.button_image_price.configure(highlightcolor="black")
        self.button_image_price.configure(pady="0")
        self.button_image_price.configure(text='''请求图形码''')
        self.button_image_price.bind('<Button-1>',self.button_image_price_clicked)

        self.button_image_number = Button (self.frame_bid)
        self.button_image_number.place(relx=0.75,rely=0.65,height=35,width=95)
        self.button_image_number.configure(activebackground="#d9d9d9")
        self.button_image_number.configure(activeforeground="#000000")
        self.button_image_number.configure(background=_bgcolor)
        self.button_image_number.configure(disabledforeground="#a3a3a3")
        self.button_image_number.configure(font=font12)
        self.button_image_number.configure(foreground="#000000")
        self.button_image_number.configure(highlightbackground="#d9d9d9")
        self.button_image_number.configure(highlightcolor="black")
        self.button_image_number.configure(pady="0")
        self.button_image_number.configure(text='''打码并出价''')
        self.button_image_number.bind('<Button-1>',self.button_image_number_clicked)

        self.Label5 = Label (self.frame_bid)
        self.Label5.place(relx=0.14,rely=0.37,height=23,width=30)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(background=_bgcolor)
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''价格''')

        self.Label7 = Label (self.frame_bid)
        self.Label7.place(relx=0.14,rely=0.65,height=23,width=30)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(activeforeground="black")
        self.Label7.configure(background=_bgcolor)
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(highlightbackground="#d9d9d9")
        self.Label7.configure(highlightcolor="black")
        self.Label7.configure(text='''图片''')

        self.frame_server = Frame (master)
        self.frame_server.place(relx=0.07,rely=0.05,relheight=0.41
                ,relwidth=0.85)
        self.frame_server.configure(relief=GROOVE)
        self.frame_server.configure(borderwidth="2")
        self.frame_server.configure(relief=GROOVE)
        self.frame_server.configure(background=_bgcolor)
        self.frame_server.configure(highlightbackground="#d9d9d9")
        self.frame_server.configure(highlightcolor="black")
        self.frame_server.configure(width=505)

        self.input_ip = Entry (self.frame_server)
        self.input_ip.place(relx=0.22,rely=0.12,relheight=0.1,relwidth=0.36)
        self.input_ip.configure(background="white")
        self.input_ip.configure(disabledforeground="#a3a3a3")
        self.input_ip.configure(font=font12)
        self.input_ip.configure(foreground="#000000")
        self.input_ip.configure(highlightbackground="#d9d9d9")
        self.input_ip.configure(highlightcolor="black")
        self.input_ip.configure(insertbackground="black")
        self.input_ip.configure(selectbackground="#c4c4c4")
        self.input_ip.configure(selectforeground="black")

        self.input_port = Entry (self.frame_server)
        self.input_port.place(relx=0.22,rely=0.33,relheight=0.1,relwidth=0.36)
        self.input_port.configure(background="white")
        self.input_port.configure(disabledforeground="#a3a3a3")
        self.input_port.configure(font=font12)
        self.input_port.configure(foreground="#000000")
        self.input_port.configure(highlightbackground="#d9d9d9")
        self.input_port.configure(highlightcolor="black")
        self.input_port.configure(insertbackground="black")
        self.input_port.configure(selectbackground="#c4c4c4")
        self.input_port.configure(selectforeground="black")

        self.input_bidno = Entry (self.frame_server)
        self.input_bidno.place(relx=0.22,rely=0.53,relheight=0.1,relwidth=0.36)
        self.input_bidno.configure(background="white")
        self.input_bidno.configure(disabledforeground="#a3a3a3")
        self.input_bidno.configure(font=font12)
        self.input_bidno.configure(foreground="#000000")
        self.input_bidno.configure(highlightbackground="#d9d9d9")
        self.input_bidno.configure(highlightcolor="black")
        self.input_bidno.configure(insertbackground="black")
        self.input_bidno.configure(selectbackground="#c4c4c4")
        self.input_bidno.configure(selectforeground="black")

        self.input_passwd = Entry (self.frame_server)
        self.input_passwd.place(relx=0.22,rely=0.73,relheight=0.1,relwidth=0.36)

        self.input_passwd.configure(background="white")
        self.input_passwd.configure(disabledforeground="#a3a3a3")
        self.input_passwd.configure(font=font12)
        self.input_passwd.configure(foreground="#000000")
        self.input_passwd.configure(highlightbackground="#d9d9d9")
        self.input_passwd.configure(highlightcolor="black")
        self.input_passwd.configure(insertbackground="black")
        self.input_passwd.configure(selectbackground="#c4c4c4")
        self.input_passwd.configure(selectforeground="black")

        self.Label1 = Label (self.frame_server)
        self.Label1.place(relx=0.06,rely=0.12,height=23,width=53)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background=_bgcolor)
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''服务器IP''')

        self.Label2 = Label (self.frame_server)
        self.Label2.place(relx=0.06,rely=0.33,height=23,width=66)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background=_bgcolor)
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''服务器Port''')

        self.Label3 = Label (self.frame_server)
        self.Label3.place(relx=0.06,rely=0.53,height=23,width=54)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background=_bgcolor)
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''用户账号''')

        self.Label4 = Label (self.frame_server)
        self.Label4.place(relx=0.06,rely=0.73,height=23,width=54)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(background=_bgcolor)
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''用户密码''')

        self.Label8 = Label (self.frame_server)
        self.Label8.place(relx=0.63,rely=0.12,height=83,width=167)
        self.Label8.configure(activebackground="#f9f9f9")
        self.Label8.configure(activeforeground="black")
        self.Label8.configure(background=_bgcolor)
        self.Label8.configure(borderwidth="5")
        self.Label8.configure(disabledforeground="#a3a3a3")
        self.Label8.configure(font=font12)
        self.Label8.configure(foreground="#000000")
        self.Label8.configure(highlightbackground="#d9d9d9")
        self.Label8.configure(highlightcolor="black")
        self.Label8.configure(text='''最新信息''')

        self.button_connect = Button (self.frame_server)
        self.button_connect.place(relx=0.71,rely=0.61,height=35,width=95)
        self.button_connect.configure(activebackground="#d9d9d9")
        self.button_connect.configure(activeforeground="#000000")
        self.button_connect.configure(background=_bgcolor)
        self.button_connect.configure(disabledforeground="#a3a3a3")
        self.button_connect.configure(font=font12)
        self.button_connect.configure(foreground="#000000")
        self.button_connect.configure(highlightbackground="#d9d9d9")
        self.button_connect.configure(highlightcolor="black")
        self.button_connect.configure(pady="0")
        self.button_connect.configure(text='''连接服务器''')
        self.button_connect.bind('<Button-1>',self.button_connect_clicked)


    def button_connect_clicked(self,p1):
            print ('self.button_connect_clicked')
            sys.stdout.flush()

    def button_image_number_clicked(self,p1):
            print ('self.button_image_number_clicked')
            sys.stdout.flush()

    def button_image_price_clicked(self,p1):
            print ('self.button_image_price_clicked')
            sys.stdout.flush()

    def button_image_warmup_clicked(self,p1):
            print ('self.button_image_warmup_clicked')
            sys.stdout.flush()

    def button_price_warmup_clicked(self,p1):
            print ('self.button_price_warmup_clicked')
            sys.stdout.flush()




if __name__ == '__main__':
        root = Tk()
        root.title('Console')
        root.geometry(GEOMETRY)
        Console (root)
        root.mainloop()

