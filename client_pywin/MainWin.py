#!/usr/bin/env python3

from tkinter        import *


#==============================================================================

#geometry('657x674+514+185')
GEOMETRY = '657x674+514+185'

#------------------------------------------------------------------------------

class Console():
        def __init__(self, master=None):
                self.var_use_group2 = IntVar()

                _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
                _fgcolor = '#000000'  # X11 color: 'black'
                _compcolor = '#d9d9d9' # X11 color: 'gray85'
                _ana1color = '#d9d9d9' # X11 color: 'gray85' 
                _ana2color = '#d9d9d9' # X11 color: 'gray85' 
                master.configure(background=_bgcolor)
                master.configure(highlightbackground="#d9d9d9")
                master.configure(highlightcolor="black")


                self.Frame1 = Frame (master)
                self.Frame1.place(relx=0.05,rely=0.04,relheight=0.2,relwidth=0.91)
                self.Frame1.configure(relief=GROOVE)
                self.Frame1.configure(borderwidth="2")
                self.Frame1.configure(relief=GROOVE)
                self.Frame1.configure(background=_bgcolor)
                self.Frame1.configure(highlightbackground="#d9d9d9")
                self.Frame1.configure(highlightcolor="black")
                self.Frame1.configure(width=595)

                self.Frame6 = Frame (self.Frame1)
                self.Frame6.place(relx=0.39,rely=0.15,relheight=0.7,relwidth=0.58)
                self.Frame6.configure(relief=GROOVE)
                self.Frame6.configure(borderwidth="2")
                self.Frame6.configure(relief=GROOVE)
                self.Frame6.configure(background=_bgcolor)
                self.Frame6.configure(highlightbackground="#d9d9d9")
                self.Frame6.configure(highlightcolor="black")
                self.Frame6.configure(width=345)

                self.input_bidno = Entry (self.Frame6)
                self.input_bidno.place(relx=0.32,rely=0.11,relheight=0.28,relwidth=0.3)
                self.input_bidno.configure(background="white")
                self.input_bidno.configure(disabledforeground="#a3a3a3")
                self.input_bidno.configure(font="TkFixedFont")
                self.input_bidno.configure(foreground="#000000")
                self.input_bidno.configure(highlightbackground="#d9d9d9")
                self.input_bidno.configure(highlightcolor="black")
                self.input_bidno.configure(insertbackground="black")
                self.input_bidno.configure(justify=RIGHT)
                self.input_bidno.configure(selectbackground="#c4c4c4")
                self.input_bidno.configure(selectforeground="black")

                self.input_passwd = Entry (self.Frame6)
                self.input_passwd.place(relx=0.32,rely=0.53,relheight=0.28,relwidth=0.3)
                self.input_passwd.configure(background="white")
                self.input_passwd.configure(disabledforeground="#a3a3a3")
                self.input_passwd.configure(font="TkFixedFont")
                self.input_passwd.configure(foreground="#000000")
                self.input_passwd.configure(highlightbackground="#d9d9d9")
                self.input_passwd.configure(highlightcolor="black")
                self.input_passwd.configure(insertbackground="black")
                self.input_passwd.configure(justify=RIGHT)
                self.input_passwd.configure(selectbackground="#c4c4c4")
                self.input_passwd.configure(selectforeground="black")

                self.button_login = Button (self.Frame6)
                self.button_login.place(relx=0.72,rely=0.53,height=28,width=75)
                self.button_login.configure(activebackground="#d9d9d9")
                self.button_login.configure(activeforeground="#000000")
                self.button_login.configure(background=_bgcolor)
                self.button_login.configure(disabledforeground="#a3a3a3")
                self.button_login.configure(foreground="#000000")
                self.button_login.configure(highlightbackground="#d9d9d9")
                self.button_login.configure(highlightcolor="black")
                self.button_login.configure(pady="0")
                self.button_login.configure(text='''登录''')
                self.button_login.bind('<Button-1>',self.proc_login)

                self.Label7 = Label (self.Frame6)
                self.Label7.place(relx=0.12,rely=0.11,height=23,width=30)
                self.Label7.configure(activebackground="#f9f9f9")
                self.Label7.configure(activeforeground="black")
                self.Label7.configure(background=_bgcolor)
                self.Label7.configure(disabledforeground="#a3a3a3")
                self.Label7.configure(foreground="#000000")
                self.Label7.configure(highlightbackground="#d9d9d9")
                self.Label7.configure(highlightcolor="black")
                self.Label7.configure(text='''账号''')

                self.Label8 = Label (self.Frame6)
                self.Label8.place(relx=0.12,rely=0.53,height=23,width=30)
                self.Label8.configure(activebackground="#f9f9f9")
                self.Label8.configure(activeforeground="black")
                self.Label8.configure(background=_bgcolor)
                self.Label8.configure(disabledforeground="#a3a3a3")
                self.Label8.configure(foreground="#000000")
                self.Label8.configure(highlightbackground="#d9d9d9")
                self.Label8.configure(highlightcolor="black")
                self.Label8.configure(text='''密码''')

                self.check_use_group2 = Checkbutton (self.Frame6)
                self.check_use_group2.place(relx=0.72,rely=0.11,relheight=0.28,relwidth=0.21)
                self.check_use_group2.configure(activebackground="#d9d9d9")
                self.check_use_group2.configure(activeforeground="#000000")
                self.check_use_group2.configure(background=_bgcolor)
                self.check_use_group2.configure(disabledforeground="#a3a3a3")
                self.check_use_group2.configure(foreground="#000000")
                self.check_use_group2.configure(highlightbackground="#d9d9d9")
                self.check_use_group2.configure(highlightcolor="black")
                self.check_use_group2.configure(text='''使用组2''')
                self.check_use_group2.configure(variable=self.var_use_group2)

                self.Frame7 = Frame (self.Frame1)
                self.Frame7.place(relx=0.03,rely=0.15,relheight=0.7,relwidth=0.31)
                self.Frame7.configure(relief=GROOVE)
                self.Frame7.configure(borderwidth="2")
                self.Frame7.configure(relief=GROOVE)
                self.Frame7.configure(background=_bgcolor)
                self.Frame7.configure(highlightbackground="#d9d9d9")
                self.Frame7.configure(highlightcolor="black")
                self.Frame7.configure(width=185)

                self.Frame10 = Frame (self.Frame7)
                self.Frame10.place(relx=0.27,rely=0.21,relheight=0.58,relwidth=0.46)
                self.Frame10.configure(relief=GROOVE)
                self.Frame10.configure(borderwidth="2")
                self.Frame10.configure(relief=GROOVE)
                self.Frame10.configure(background=_bgcolor)
                self.Frame10.configure(highlightbackground="#d9d9d9")
                self.Frame10.configure(highlightcolor="black")
                self.Frame10.configure(width=85)

                self.ouput_login_status = Message (self.Frame10)
                self.ouput_login_status.place(relx=0.12,rely=0.18,relheight=0.64,relwidth=0.79)
                self.ouput_login_status.configure(background=_bgcolor)
                self.ouput_login_status.configure(foreground="#000000")
                self.ouput_login_status.configure(highlightbackground="#d9d9d9")
                self.ouput_login_status.configure(highlightcolor="black")
                self.ouput_login_status.configure(text='''未登录''')
                self.ouput_login_status.configure(width=67)

                self.Frame3 = Frame (master)
                self.Frame3.place(relx=0.05,rely=0.27,relheight=0.32,relwidth=0.91)
                self.Frame3.configure(relief=GROOVE)
                self.Frame3.configure(borderwidth="2")
                self.Frame3.configure(relief=GROOVE)
                self.Frame3.configure(background=_bgcolor)
                self.Frame3.configure(highlightbackground="#d9d9d9")
                self.Frame3.configure(highlightcolor="black")
                self.Frame3.configure(width=595)

                self.Frame4 = Frame (self.Frame3)
                self.Frame4.place(relx=0.57,rely=0.09,relheight=0.81,relwidth=0.39)
                self.Frame4.configure(relief=GROOVE)
                self.Frame4.configure(borderwidth="2")
                self.Frame4.configure(relief=GROOVE)
                self.Frame4.configure(background=_bgcolor)
                self.Frame4.configure(highlightbackground="#d9d9d9")
                self.Frame4.configure(highlightcolor="black")
                self.Frame4.configure(width=235)

                self.input_ajust_channel = Entry (self.Frame4)
                self.input_ajust_channel.place(relx=0.13,rely=0.69,relheight=0.15,relwidth=0.4)
                self.input_ajust_channel.configure(background="white")
                self.input_ajust_channel.configure(disabledforeground="#a3a3a3")
                self.input_ajust_channel.configure(font="TkFixedFont")
                self.input_ajust_channel.configure(foreground="#000000")
                self.input_ajust_channel.configure(highlightbackground="#d9d9d9")
                self.input_ajust_channel.configure(highlightcolor="black")
                self.input_ajust_channel.configure(insertbackground="black")
                self.input_ajust_channel.configure(justify=CENTER)
                self.input_ajust_channel.configure(selectbackground="#c4c4c4")
                self.input_ajust_channel.configure(selectforeground="black")

                self.button_channel = Button (self.Frame4)
                self.button_channel.place(relx=0.6,rely=0.69,height=28,width=79)
                self.button_channel.configure(activebackground="#d9d9d9")
                self.button_channel.configure(activeforeground="#000000")
                self.button_channel.configure(background=_bgcolor)
                self.button_channel.configure(disabledforeground="#a3a3a3")
                self.button_channel.configure(foreground="#000000")
                self.button_channel.configure(highlightbackground="#d9d9d9")
                self.button_channel.configure(highlightcolor="black")
                self.button_channel.configure(pady="0")
                self.button_channel.configure(text='''调整通道数''')
                self.button_channel.bind('<Button-1>',self.proc_channel)

                self.Label5 = Label (self.Frame4)
                self.Label5.place(relx=0.64,rely=0.17,height=23,width=66)
                self.Label5.configure(activebackground="#f9f9f9")
                self.Label5.configure(activeforeground="black")
                self.Label5.configure(background=_bgcolor)
                self.Label5.configure(disabledforeground="#a3a3a3")
                self.Label5.configure(foreground="#000000")
                self.Label5.configure(highlightbackground="#d9d9d9")
                self.Label5.configure(highlightcolor="black")
                self.Label5.configure(text='''计划通道数''')

                self.Label6 = Label (self.Frame4)
                self.Label6.place(relx=0.13,rely=0.34,height=23,width=6)
                self.Label6.configure(activebackground="#f9f9f9")
                self.Label6.configure(activeforeground="black")
                self.Label6.configure(background=_bgcolor)
                self.Label6.configure(disabledforeground="#a3a3a3")
                self.Label6.configure(foreground="#000000")
                self.Label6.configure(highlightbackground="#d9d9d9")
                self.Label6.configure(highlightcolor="black")

                self.Frame14 = Frame (self.Frame4)
                self.Frame14.place(relx=0.13,rely=0.11,relheight=0.2,relwidth=0.4)
                self.Frame14.configure(relief=GROOVE)
                self.Frame14.configure(borderwidth="2")
                self.Frame14.configure(relief=GROOVE)
                self.Frame14.configure(background=_bgcolor)
                self.Frame14.configure(highlightbackground="#d9d9d9")
                self.Frame14.configure(highlightcolor="black")
                self.Frame14.configure(width=95)

                self.output_goal_channel = Message (self.Frame14)
                self.output_goal_channel.place(relx=0.21,rely=0.29,relheight=0.43,relwidth=0.6)
                self.output_goal_channel.configure(background=_bgcolor)
                self.output_goal_channel.configure(foreground="#000000")
                self.output_goal_channel.configure(highlightbackground="#d9d9d9")
                self.output_goal_channel.configure(highlightcolor="black")
                self.output_goal_channel.configure(text='''0''')
                self.output_goal_channel.configure(width=57)

                self.Frame18 = Frame (self.Frame4)
                self.Frame18.place(relx=0.13,rely=0.4,relheight=0.2,relwidth=0.4)
                self.Frame18.configure(relief=GROOVE)
                self.Frame18.configure(borderwidth="2")
                self.Frame18.configure(relief=GROOVE)
                self.Frame18.configure(background=_bgcolor)
                self.Frame18.configure(highlightbackground="#d9d9d9")
                self.Frame18.configure(highlightcolor="black")
                self.Frame18.configure(width=95)

                self.output_current_channel = Message (self.Frame18)
                self.output_current_channel.place(relx=0.21,rely=0.29,relheight=0.43,relwidth=0.6)
                self.output_current_channel.configure(background=_bgcolor)
                self.output_current_channel.configure(foreground="#000000")
                self.output_current_channel.configure(highlightbackground="#d9d9d9")
                self.output_current_channel.configure(highlightcolor="black")
                self.output_current_channel.configure(text='''0''')
                self.output_current_channel.configure(width=57)

                self.Label14 = Label (self.Frame4)
                self.Label14.place(relx=0.64,rely=0.46,height=23,width=66)
                self.Label14.configure(activebackground="#f9f9f9")
                self.Label14.configure(activeforeground="black")
                self.Label14.configure(background=_bgcolor)
                self.Label14.configure(disabledforeground="#a3a3a3")
                self.Label14.configure(foreground="#000000")
                self.Label14.configure(highlightbackground="#d9d9d9")
                self.Label14.configure(highlightcolor="black")
                self.Label14.configure(text='''可用通道数''')

                self.Frame8 = Frame (self.Frame3)
                self.Frame8.place(relx=0.03,rely=0.09,relheight=0.81,relwidth=0.5)
                self.Frame8.configure(relief=GROOVE)
                self.Frame8.configure(borderwidth="2")
                self.Frame8.configure(relief=GROOVE)
                self.Frame8.configure(background=_bgcolor)
                self.Frame8.configure(highlightbackground="#d9d9d9")
                self.Frame8.configure(highlightcolor="black")
                self.Frame8.configure(width=295)

                self.Label2 = Label (self.Frame8)
                self.Label2.place(relx=0.14,rely=0.17,height=23,width=54)
                self.Label2.configure(activebackground="#f9f9f9")
                self.Label2.configure(activeforeground="black")
                self.Label2.configure(background=_bgcolor)
                self.Label2.configure(disabledforeground="#a3a3a3")
                self.Label2.configure(foreground="#000000")
                self.Label2.configure(highlightbackground="#d9d9d9")
                self.Label2.configure(highlightcolor="black")
                self.Label2.configure(text='''变价时间''')

                self.Label3 = Label (self.Frame8)
                self.Label3.place(relx=0.14,rely=0.46,height=23,width=54)
                self.Label3.configure(activebackground="#f9f9f9")
                self.Label3.configure(activeforeground="black")
                self.Label3.configure(background=_bgcolor)
                self.Label3.configure(disabledforeground="#a3a3a3")
                self.Label3.configure(foreground="#000000")
                self.Label3.configure(highlightbackground="#d9d9d9")
                self.Label3.configure(highlightcolor="black")
                self.Label3.configure(text='''系统时间''')

                self.Label4 = Label (self.Frame8)
                self.Label4.place(relx=0.14,rely=0.74,height=23,width=54)
                self.Label4.configure(activebackground="#f9f9f9")
                self.Label4.configure(activeforeground="black")
                self.Label4.configure(background=_bgcolor)
                self.Label4.configure(disabledforeground="#a3a3a3")
                self.Label4.configure(foreground="#000000")
                self.Label4.configure(highlightbackground="#d9d9d9")
                self.Label4.configure(highlightcolor="black")
                self.Label4.configure(text='''当前价格''')

                self.Frame11 = Frame (self.Frame8)
                self.Frame11.place(relx=0.44,rely=0.11,relheight=0.2,relwidth=0.42)
                self.Frame11.configure(relief=GROOVE)
                self.Frame11.configure(borderwidth="2")
                self.Frame11.configure(relief=GROOVE)
                self.Frame11.configure(background=_bgcolor)
                self.Frame11.configure(highlightbackground="#d9d9d9")
                self.Frame11.configure(highlightcolor="black")
                self.Frame11.configure(width=125)

                self.output_change_time = Message (self.Frame11)
                self.output_change_time.place(relx=0.24,rely=0.29,relheight=0.43,relwidth=0.54)
                self.output_change_time.configure(background=_bgcolor)
                self.output_change_time.configure(foreground="#000000")
                self.output_change_time.configure(highlightbackground="#d9d9d9")
                self.output_change_time.configure(highlightcolor="black")
                self.output_change_time.configure(text='''00:00:00''')
                self.output_change_time.configure(width=67)

                self.Frame12 = Frame (self.Frame8)
                self.Frame12.place(relx=0.44,rely=0.4,relheight=0.2,relwidth=0.42)
                self.Frame12.configure(relief=GROOVE)
                self.Frame12.configure(borderwidth="2")
                self.Frame12.configure(relief=GROOVE)
                self.Frame12.configure(background=_bgcolor)
                self.Frame12.configure(highlightbackground="#d9d9d9")
                self.Frame12.configure(highlightcolor="black")
                self.Frame12.configure(width=125)

                self.output_system_time = Message (self.Frame12)
                self.output_system_time.place(relx=0.24,rely=0.29,relheight=0.43,relwidth=0.54)
                self.output_system_time.configure(background=_bgcolor)
                self.output_system_time.configure(foreground="#000000")
                self.output_system_time.configure(highlightbackground="#d9d9d9")
                self.output_system_time.configure(highlightcolor="black")
                self.output_system_time.configure(text='''00:00:00''')
                self.output_system_time.configure(width=67)

                self.Frame13 = Frame (self.Frame8)
                self.Frame13.place(relx=0.44,rely=0.69,relheight=0.2,relwidth=0.42)
                self.Frame13.configure(relief=GROOVE)
                self.Frame13.configure(borderwidth="2")
                self.Frame13.configure(relief=GROOVE)
                self.Frame13.configure(background=_bgcolor)
                self.Frame13.configure(highlightbackground="#d9d9d9")
                self.Frame13.configure(highlightcolor="black")
                self.Frame13.configure(width=125)

                self.output_current_price = Message (self.Frame13)
                self.output_current_price.place(relx=0.24,rely=0.29,relheight=0.43,relwidth=0.54)
                self.output_current_price.configure(background=_bgcolor)
                self.output_current_price.configure(foreground="#000000")
                self.output_current_price.configure(highlightbackground="#d9d9d9")
                self.output_current_price.configure(highlightcolor="black")
                self.output_current_price.configure(text='''0''')
                self.output_current_price.configure(width=67)

                self.Frame5 = Frame (master)
                self.Frame5.place(relx=0.05,rely=0.61,relheight=0.35,relwidth=0.91)
                self.Frame5.configure(relief=GROOVE)
                self.Frame5.configure(borderwidth="2")
                self.Frame5.configure(relief=GROOVE)
                self.Frame5.configure(background=_bgcolor)
                self.Frame5.configure(highlightbackground="#d9d9d9")
                self.Frame5.configure(highlightcolor="black")
                self.Frame5.configure(width=595)

                self.Frame2 = Frame (self.Frame5)
                self.Frame2.place(relx=0.39,rely=0.09,relheight=0.83,relwidth=0.58)
                self.Frame2.configure(relief=GROOVE)
                self.Frame2.configure(borderwidth="2")
                self.Frame2.configure(relief=GROOVE)
                self.Frame2.configure(background=_bgcolor)
                self.Frame2.configure(highlightbackground="#d9d9d9")
                self.Frame2.configure(highlightcolor="black")
                self.Frame2.configure(width=345)

                self.Label12 = Label (self.Frame2)
                self.Label12.place(relx=0.17,rely=0.26,height=23,width=30)
                self.Label12.configure(activebackground="#f9f9f9")
                self.Label12.configure(activeforeground="black")
                self.Label12.configure(background=_bgcolor)
                self.Label12.configure(disabledforeground="#a3a3a3")
                self.Label12.configure(foreground="#000000")
                self.Label12.configure(highlightbackground="#d9d9d9")
                self.Label12.configure(highlightcolor="black")
                self.Label12.configure(text='''价格''')

                self.input_image_price = Entry (self.Frame2)
                self.input_image_price.place(relx=0.41,rely=0.26,relheight=0.14,relwidth=0.27)
                self.input_image_price.configure(background="white")
                self.input_image_price.configure(disabledforeground="#a3a3a3")
                self.input_image_price.configure(font="TkFixedFont")
                self.input_image_price.configure(foreground="#000000")
                self.input_image_price.configure(highlightbackground="#d9d9d9")
                self.input_image_price.configure(highlightcolor="black")
                self.input_image_price.configure(insertbackground="black")
                self.input_image_price.configure(justify=RIGHT)
                self.input_image_price.configure(selectbackground="#c4c4c4")
                self.input_image_price.configure(selectforeground="black")

                self.input_image_decode = Entry (self.Frame2)
                self.input_image_decode.place(relx=0.41,rely=0.62,relheight=0.14,relwidth=0.27)
                self.input_image_decode.configure(background="white")
                self.input_image_decode.configure(disabledforeground="#a3a3a3")
                self.input_image_decode.configure(font="TkFixedFont")
                self.input_image_decode.configure(foreground="#000000")
                self.input_image_decode.configure(highlightbackground="#d9d9d9")
                self.input_image_decode.configure(highlightcolor="black")
                self.input_image_decode.configure(insertbackground="black")
                self.input_image_decode.configure(justify=RIGHT)
                self.input_image_decode.configure(selectbackground="#c4c4c4")
                self.input_image_decode.configure(selectforeground="black")

                self.button_image_price = Button (self.Frame2)
                self.button_image_price.place(relx=0.72,rely=0.26,height=28,width=81)
                self.button_image_price.configure(activebackground="#d9d9d9")
                self.button_image_price.configure(activeforeground="#000000")
                self.button_image_price.configure(background=_bgcolor)
                self.button_image_price.configure(disabledforeground="#a3a3a3")
                self.button_image_price.configure(foreground="#000000")
                self.button_image_price.configure(highlightbackground="#d9d9d9")
                self.button_image_price.configure(highlightcolor="black")
                self.button_image_price.configure(pady="0")
                self.button_image_price.configure(text='''请求图形码''')
                self.button_image_price.bind('<Button-1>',self.proc_image_price)

                self.button_image_decode = Button (self.Frame2)
                self.button_image_decode.place(relx=0.72,rely=0.62,height=28,width=81)
                self.button_image_decode.configure(activebackground="#d9d9d9")
                self.button_image_decode.configure(activeforeground="#000000")
                self.button_image_decode.configure(background=_bgcolor)
                self.button_image_decode.configure(disabledforeground="#a3a3a3")
                self.button_image_decode.configure(foreground="#000000")
                self.button_image_decode.configure(highlightbackground="#d9d9d9")
                self.button_image_decode.configure(highlightcolor="black")
                self.button_image_decode.configure(pady="0")
                self.button_image_decode.configure(text='''打码并出价''')
                self.button_image_decode.bind('<Button-1>',self.proc_image_decode)

                self.label_picture = Label (self.Frame2)
                self.label_picture.place(relx=0.03,rely=0.51,height=73,width=127)
                self.label_picture.configure(activebackground="#f9f9f9")
                self.label_picture.configure(activeforeground="black")
                self.label_picture.configure(background=_bgcolor)
                self.label_picture.configure(disabledforeground="#a3a3a3")
                self.label_picture.configure(foreground="#000000")
                self.label_picture.configure(highlightbackground="#d9d9d9")
                self.label_picture.configure(highlightcolor="black")
                self.label_picture.configure(text='''图片''')

                self.Frame9 = Frame (self.Frame5)
                self.Frame9.place(relx=0.03,rely=0.09,relheight=0.83,relwidth=0.31)
                self.Frame9.configure(relief=GROOVE)
                self.Frame9.configure(borderwidth="2")
                self.Frame9.configure(relief=GROOVE)
                self.Frame9.configure(background=_bgcolor)
                self.Frame9.configure(highlightbackground="#d9d9d9")
                self.Frame9.configure(highlightcolor="black")
                self.Frame9.configure(width=185)

                self.Label9 = Label (self.Frame9)
                self.Label9.place(relx=0.05,rely=0.15,height=23,width=42)
                self.Label9.configure(activebackground="#f9f9f9")
                self.Label9.configure(activeforeground="black")
                self.Label9.configure(background=_bgcolor)
                self.Label9.configure(disabledforeground="#a3a3a3")
                self.Label9.configure(foreground="#000000")
                self.Label9.configure(highlightbackground="#d9d9d9")
                self.Label9.configure(highlightcolor="black")
                self.Label9.configure(text='''第一次''')

                self.Label10 = Label (self.Frame9)
                self.Label10.place(relx=0.05,rely=0.46,height=23,width=42)
                self.Label10.configure(activebackground="#f9f9f9")
                self.Label10.configure(activeforeground="black")
                self.Label10.configure(background=_bgcolor)
                self.Label10.configure(disabledforeground="#a3a3a3")
                self.Label10.configure(foreground="#000000")
                self.Label10.configure(highlightbackground="#d9d9d9")
                self.Label10.configure(highlightcolor="black")
                self.Label10.configure(text='''第二次''')

                self.Label11 = Label (self.Frame9)
                self.Label11.place(relx=0.05,rely=0.77,height=23,width=42)
                self.Label11.configure(activebackground="#f9f9f9")
                self.Label11.configure(activeforeground="black")
                self.Label11.configure(background=_bgcolor)
                self.Label11.configure(disabledforeground="#a3a3a3")
                self.Label11.configure(foreground="#000000")
                self.Label11.configure(highlightbackground="#d9d9d9")
                self.Label11.configure(highlightcolor="black")
                self.Label11.configure(text='''第三次''')

                self.Frame15 = Frame (self.Frame9)
                self.Frame15.place(relx=0.38,rely=0.1,relheight=0.18,relwidth=0.51)
                self.Frame15.configure(relief=GROOVE)
                self.Frame15.configure(borderwidth="2")
                self.Frame15.configure(relief=GROOVE)
                self.Frame15.configure(background=_bgcolor)
                self.Frame15.configure(highlightbackground="#d9d9d9")
                self.Frame15.configure(highlightcolor="black")
                self.Frame15.configure(width=95)

                self.output_first_price = Message (self.Frame15)
                self.output_first_price.place(relx=0.21,rely=0.29,relheight=0.43,relwidth=0.6)
                self.output_first_price.configure(background=_bgcolor)
                self.output_first_price.configure(foreground="#000000")
                self.output_first_price.configure(highlightbackground="#d9d9d9")
                self.output_first_price.configure(highlightcolor="black")
                self.output_first_price.configure(text='''0''')
                self.output_first_price.configure(width=57)

                self.Frame16 = Frame (self.Frame9)
                self.Frame16.place(relx=0.38,rely=0.41,relheight=0.18,relwidth=0.51)
                self.Frame16.configure(relief=GROOVE)
                self.Frame16.configure(borderwidth="2")
                self.Frame16.configure(relief=GROOVE)
                self.Frame16.configure(background=_bgcolor)
                self.Frame16.configure(highlightbackground="#d9d9d9")
                self.Frame16.configure(highlightcolor="black")
                self.Frame16.configure(width=95)

                self.output_second_price = Message (self.Frame16)
                self.output_second_price.place(relx=0.21,rely=0.29,relheight=0.43,relwidth=0.6)
                self.output_second_price.configure(background=_bgcolor)
                self.output_second_price.configure(foreground="#000000")
                self.output_second_price.configure(highlightbackground="#d9d9d9")
                self.output_second_price.configure(highlightcolor="black")
                self.output_second_price.configure(text='''0''')
                self.output_second_price.configure(width=57)

                self.Frame17 = Frame (self.Frame9)
                self.Frame17.place(relx=0.38,rely=0.72,relheight=0.18,relwidth=0.51)
                self.Frame17.configure(relief=GROOVE)
                self.Frame17.configure(borderwidth="2")
                self.Frame17.configure(relief=GROOVE)
                self.Frame17.configure(background=_bgcolor)
                self.Frame17.configure(highlightbackground="#d9d9d9")
                self.Frame17.configure(highlightcolor="black")
                self.Frame17.configure(width=95)

                self.output_third_price = Message (self.Frame17)
                self.output_third_price.place(relx=0.21,rely=0.29,relheight=0.43,relwidth=0.6)
                self.output_third_price.configure(background=_bgcolor)
                self.output_third_price.configure(foreground="#000000")
                self.output_third_price.configure(highlightbackground="#d9d9d9")
                self.output_third_price.configure(highlightcolor="black")
                self.output_third_price.configure(text='''0''')
                self.output_third_price.configure(width=57)



        def proc_login(self,p1):
                print ('self.proc_login')
                sys.stdout.flush()

        def proc_channel(self,p1):
                print ('self.proc_channel')
                sys.stdout.flush()

        def proc_image_price(self,p1):
                print ('self.proc_image_price')
                sys.stdout.flush()

        def proc_image_decode(self,p1):
                print ('self.proc_image_decode')
                sys.stdout.flush()


#=============================================================================


if __name__ == '__main__':
        root = Tk()
        root.title('Console')
        root.geometry(GEOMETRY)
        Console (root)
        root.mainloop()

