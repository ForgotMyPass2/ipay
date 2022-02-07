#iPay Code

from tkinter import *
from tkinter import ttk
import mysql.connector
import random
import os
import csv
import wx
import wx.grid as grid
 

con=mysql.connector.connect(user="ipay", password="test", auth_plugin="mysql_native_password", host="0.tcp.in.ngrok.io", port="12912", database="ipay")
mc=con.cursor()
#"mc" is cursor variable.
#Globals used: Login

#==================================
#       backend functions
#==================================


def closewindow(name):
    name.destroy()
    root.destroy()

def signup_get(title, window, getname, getusername, getemail, getphone, getpass, getcardno, getcard_month, getcard_year, getcvv):
    accno_generated=accno_gen()
    mc.execute(f"select accno, card_no, phone, username from userinfo")
    acc_check=mc.fetchall()
    trueusername=0
    truecard=0
    truephone=0
    if len(getname)<25:
                if len(getemail)<50:
                    if getphone.isdigit() and len(getphone)==10:
                        for i in acc_check:
                            if int(getphone)==i[2]:
                                truephone=1
                        if truephone==0: 
                            if getcardno.isdigit() and len(getcardno)==16:
                                for i in acc_check:
                                    if int(getcardno)==i[1]:
                                        truecard=1
                                if truecard==0:
                                    if getcvv.isdigit() and len(getcvv)==3:
                                        if len(getpass)<=24 and len(getpass)>=8:
                                            for i in acc_check:
                                                if getusername==i[3]:
                                                    trueusername=1
                                            if trueusername==0:
                                                if len(getusername)<=30:
                                                    date=str(getcard_month+"_"+getcard_year)
                                                    x="insert into userinfo (accno,name,email,phone,card_no,card_expiry,cvv,password,balance,username) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                                    y=[(accno_generated),(getname.strip(" ")),((getemail.strip()).replace(" ","_")),(int(getphone)),(int(getcardno)),(date),(int(getcvv)),(getpass.rstrip(" ")),(0), (getusername)]
                                                    mc.execute(x,y)
                                                    con.commit()
                                                    success("Success!", "Your account has been created, now head to the login page", window)
                                                else:
                                                    title.configure(text="Username too long, limit is 30", fg="red")
                                            else:
                                                title.configure(text="Username already in use", fg="red")
                                        else:
                                            title.configure(text="Password length must be b/w 8 & 24", fg="red")
                                    else:
                                        title.configure(text="CVV is Long/Short/Not Numeric", fg="red")
                                else:
                                    title.configure(text="Card Number already in use", fg="red")
                            else:
                                title.configure(text="Card No. is Long/Short/Not Numeric", fg="red")
                        else:
                            title.configure(text="Phone Number already in use", fg="red")
                    else:
                        title.configure(text="Invalid Phone No.", fg="red")
                else:
                    title.configure(text="Email too long (how even)", fg="red")
    else:
        title.configure(text="Name is too long(get a new one)", fg="red")

def accno_gen():
    x=random.randint(100000, 999999)
    mc.execute("select username from userinfo")
    userinfo=mc.fetchall()
    if x in userinfo:
        accno_gen()
    else:
        return x

def getlogin(user, passw, passfield):          #auth() func to authenthicate saved login
    mc.execute(f"select username,password,accno from userinfo")
    unames = mc.fetchall()
    result="0"
    for i in unames:
        if i[0]==user:
            result="1"
            if i[1] == passw:
                homepage(i[2])
            else:
                errorLogin=Label(Login, text="Incorrect Password", fg="red").grid(row=1, column=0, columnspan=3)
                passfield.delete(0, END)
    if result=="0":
        errorLogin=Label(Login, text="Incorrect Username", fg="red").grid(row=1, column=0, columnspan=3)
        passfield.delete(0, END)

def success(heading, message, optional=0):
    if optional!=0:
        optional.destroy()
    popup=Toplevel()
    popup.resizable(width=False, height=False)
    popup.title(heading)
    body=Label(popup, text=message)
    okbutton=Button(popup, text="Ok", command=popup.destroy)
    body.grid(row=0, column=0, padx=10, pady=5)
    okbutton.grid(row=1, column=0, pady=10)

def addbalance(payment, passwd, cvv, user, window, addmessage): #addmoney function
    if payment>10000 or payment<0:
        addmessage.configure(text="Invalid (amount between 1-10000)",fg = "red")
    else:
        mc.execute(f"select password,cvv from userinfo where accno = {user}")
        getcvvpass=mc.fetchone()
        if passwd == getcvvpass[0]:
            if cvv.isdigit():
                cvv=int(cvv)
                if cvv == getcvvpass[1]:
                    mc.execute(f"update userinfo set balance=balance+{int(payment)} where accno = {user}")
                    transactionappend("Self", "Credit", user)
                    success("Success!", "₹"+str(payment)+" has been added to your account", window)
                    activebalance(user)
                
                else:
                    addmessage.configure(text="Invalid CVV!",fg = "red")
                
            else:
                addmessage.configure(text="CVV is not numeric!",fg = "red")
        else:
            addmessage.configure(text="Invalid password!",fg = "red")
        con.commit()


def activebalance(user):
    x=mc.execute(f"select balance from userinfo where accno = {user}")
    bal=mc.fetchone()
    homebalance.configure(text="Your Balance is ₹"+str(bal[0]))


def transactionappend(to, credit_debit, usernow):
    x=mc.execute(f"select balance from userinfo where accno = {usernow}")
    bal=mc.fetchone()
    mc.execute(f"insert into transaction_history (acc_no, date_of_transaction, debit_credit, recipient, balance, Time) values ({usernow}, CURDATE(), '{credit_debit}', '{to}', {bal[0]}, CURTIME())")
    con.commit()



def sendlogic(user, window, sendmessage, payment, passwd, cvv, recieve):
    mc.execute(f"select balance,password,cvv from userinfo where accno = {user}")
    getinfo=mc.fetchone()
    if getinfo[0]<payment:
        sendmessage.configure(text="Too poor to pay",fg = "red")
    else:
        if passwd == getinfo[1]:
            if cvv.isdigit():
                cvv=int(cvv)
                if cvv == getinfo[2]:
                    mc.execute("select username, accno from userinfo")
                    username=mc.fetchall()
                    true=0
                    for i in username:
                        if i[0]==recieve:
                            recieve_accno=i[1]
                            true=1
                    if true==1:
                        mc.execute(f"update userinfo set balance=balance-{int(payment)} where accno = {user}")
                        mc.execute(f"update userinfo set balance=balance+{int(payment)} where accno = {recieve_accno}")
                        activebalance(user)
                        mc.execute(f"select accno from userinfo where username = \"{recieve}\"")
                        y=(mc.fetchone())[0]
                        transactionappend(str(recieve), "Debit", user)
                        transactionappend(str(user), "Credit", y)
                        success("Success!",str(recieve)+" has been sent ₹"+str(payment)+".", window)
                    else:
                        sendmessage.configure(text="Invalid username",fg = "red")
                else:
                    sendmessage.configure(text="Invalid CVV!",fg = "red")                    
            else:
                sendmessage.configure(text="CVV is not numeric!",fg = "red")
        else:
            sendmessage.configure(text="Invalid password!",fg = "red")
    con.commit()



def calculate_elec(title, payment, passwd, cvv, board, user, window):
    #calculates and deducts electricity bill which has been input by user
    mc.execute(f"select balance,password,cvv from userinfo where accno = {user}")
    getinfo=mc.fetchone()
    if board!="":
        if getinfo[0]>(payment+100):
            if passwd == getinfo[1]:
                if cvv.isdigit():
                    cvv=int(cvv)
                    if cvv == getinfo[2]:
                        mc.execute(f"update userinfo set balance=balance-{int(payment)} where accno = {user}")
                        success("Success!", "₹"+str(payment)+" has been paid to "+str(board)+".", window)
                        transactionappend(board, "Debit", user)
                        activebalance(user)
                    else:
                        title.configure(text="Invalid CVV!",fg = "red")
                else:
                    title.configure(text="CVV is not numeric!",fg = "red")
            else:
                title.configure(text="Invalid password!",fg = "red")
        else:
            title.configure(text="Insufficient funds",fg = "red")
    else:
        title.configure(text="Choose Board!",fg = "red")
    con.commit()



def transactionlist(user):
    x=mc.execute(f"select date_of_transaction, Time, debit_credit, recipient, balance from transaction_history where acc_no = {user}")
    listall=mc.fetchall()
    y=mc.execute(f"select name from userinfo where accno = {user}")
    name=mc.fetchone()        
    f=open(f"Transaction_history_of_{name[0]}.csv", "w", newline="")
    write=csv.writer(f)
    field=("Date of Transaction", "Time", "Debit/Credit", "Recipient", "Balance")
    write.writerow(field)
    for i in listall:
          write.writerow(i)
    f.close()
    trans_hist(f"Transaction_history_of_{name[0]}.csv") 



#==================================
#       frontend functions
#==================================



def loginwindow():   #first window that opens after running the program.
    global Login
    Login = Toplevel()
    Login.resizable(width=False, height=False)
    Login.title("iPay: Login")

                #Login Page Elements
    title = Label(Login, text="Welcome! Log in or Sign up" )
    user = Label(Login, text="Username:")
    e_user = Entry(Login)
    Pass = Label(Login, text="Password:")
    e_Pass = Entry(Login, show="*")
    LoginButton = Button(Login, text="Login", command=lambda: getlogin(e_user.get(), e_Pass.get(), e_Pass), padx=77)      #getlogin() func to authenthicate user
    SignupButton = Button(Login, text="Sign Up", command=signuppage, padx=77)       #signuppage() func. to add account to system
    exitButton = Button(Login, text="Exit", command=lambda: closewindow(Login))
    

                #Login Page Grid
    title.grid(row=0, column=0, pady=5, padx=50, columnspan=3)
    user.grid(row=2, column=0, pady=25, padx=0)
    e_user.grid(row=2, column=2, pady=0, padx=0)
    Pass.grid(row=3, column=0, pady=25)
    e_Pass.grid(row=3, column=2, pady=0, padx=0)
    LoginButton.grid(row=5, column=0, pady=0, padx=0)
    SignupButton.grid(row=5, column=2, pady=0, padx=0)
    exitButton.grid(row=6, column=0, pady=0, padx=0, columnspan=3, sticky=E+W)



def signuppage():   #signup page accessible via login page
    signup = Toplevel()
    signup.resizable(width=False, height=False)
    signup.title("Sign up!")

    title=Label(signup, text="Enter Details below")
    name=Label(signup, text="Name(no spaces) :")
    username=Label(signup, text="Username:")
    email=Label(signup, text="Email:")
    phone=Label(signup, text="Phone Number:")
    passw=Label(signup, text="Password:")
    cardno=Label(signup, text="Card Number:")
    cardexpiry=Label(signup, text="Card Expiry:")
    cvv=Label(signup, text="CVV:")
    SignupButton=Button(signup, text="Sign up", padx=80, command=lambda: signup_get(title, signup, e_name.get(), e_username.get(), e_email.get (), e_phone.get(), e_passw.get(), e_cardno.get(), str(e_card_month.get()), str(e_card_year.get()), e_cvv.get()))
    BackButton=Button(signup, text="Back", command=lambda: closewindow(signup), padx=90)
    e_name=Entry(signup)
    e_username=Entry(signup)
    e_email=Entry(signup)
    e_phone=Entry(signup)
    e_passw=Entry(signup, show="*")
    e_cardno=Entry(signup)
    e_card_month=Spinbox(signup, from_=1, to=12, width=8, state = "readonly")
    e_card_year=Spinbox(signup, from_=2023, to=2028, width=8, state = "readonly")
    e_cvv=Entry(signup, show="*")

                    #placement of window elements
    title.grid(row=0, column=0, columnspan=3)
    name.grid(row=1, column=0)
    username.grid(row=2, column=0)
    email.grid(row=3, column=0)
    phone.grid(row=4, column=0)
    passw.grid(row=5, column=0)
    cardno.grid(row=6, column=0)
    cardexpiry.grid(row=7, column=0)
    cvv.grid(row=8, column=0)
    SignupButton.grid(row=9, column=0, padx=5)
    BackButton.grid(row=9, column=1, columnspan=2)
    e_name.grid(row=1, column=1, pady=10, padx=5, columnspan=2)
    e_username.grid(row=2, column=1, pady=5, columnspan=2)
    e_email.grid(row=3, column=1, pady=5, columnspan=2)
    e_phone.grid(row=4, column=1, pady=5, columnspan=2)
    e_passw.grid(row=5, column=1, pady=5, columnspan=2)
    e_cardno.grid(row=6, column=1, pady=5, columnspan=2)
    e_card_month.grid(row=7, column=1)
    e_card_year.grid(row=7, column=2)
    e_cvv.grid(row=8, column=1, pady=5, columnspan=2)


def homepage(user):
                #Homepage
    global homebalance
    Login.destroy()
    home = Toplevel()
    home.resizable(width=False, height=False)
    home.title("iPay Home")
    mc.execute(f"select name,balance from userinfo where accno = {user}")
    getinfo = mc.fetchone()

    
                #HomePage Elements
    title = Label(home, text=f"Welcome back {getinfo[0]}")
    homebalance = Label(home, text="Your balance is ₹"+str(getinfo[1]))
    exitbutton = Button(home, text="Exit", command=lambda: closewindow(home), width=25)
    paybutton = Button(home, text="""Pay
electricity
bill""", command=lambda: payelectric(user), padx=20)
    addbutton=Button(home, text="Add Money", command=lambda: addmoneywindow(user, str(getinfo[1])), pady=26, padx=14)
    transacthistorybutton=Button(home, text="""Transaction
history""", padx=11, pady=14, command=lambda: transactionlist(user))
    sendbutton=Button(home, text="Send money", pady=25, padx=10, command=lambda: sendmoneywindow(user))
    
                #HomePage Grid
    title.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
    homebalance.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
    exitbutton.grid(row=6, column=0, columnspan=3)
    paybutton.grid(row=2, column=2)
    addbutton.grid(row=2, column=0)
    transacthistorybutton.grid(row=3, column=0)
    sendbutton.grid(row=3, column=2)


def addmoneywindow(user, currentbal):
    try:
        global addmoney
        addmoney.destroy()
        return
    except:
        print()
    finally:
        addmoney = Toplevel()
        addmoney.title("Add Money")
        addmoney.resizable(width=False, height=False)

        addmessage = Label(addmoney, text="Enter Details below")
        pay = Label(addmoney, text="Amount to be added:")
        passw = Label(addmoney, text="Enter Password:")
        cvv = Label(addmoney, text="Enter CVV:")
        e_pay = Entry(addmoney, width=15)
        e_pass = Entry(addmoney, show="*", width=15)
        e_cvv = Entry(addmoney, width=15, show="*")
        pay_but = Button(addmoney, text="ADD", padx=50, pady=10, fg="green", activeforeground="green", command=lambda: addbalance(int(e_pay.get()), e_pass.get(), e_cvv.get(), user, addmoney, addmessage))
        exit_but = Button(addmoney, text="Back", command=addmoney.destroy, padx=50, pady=10, fg="red", activeforeground="red")


        pay.grid(row=2, column=0, pady=5, padx=3)
        passw.grid(row=3, column=0, pady=5)
        cvv.grid(row=4, column=0, pady=5)
        e_pay.grid(row=2, column=2, padx=3)
        e_pass.grid(row=3, column=2)
        e_cvv.grid(row=4, column=2)
        pay_but.grid(row=5, column=0)
        exit_but.grid(row=5, column=2)
        addmessage.grid(row=1, column=0, columnspan=3)



def sendmoneywindow(user):
    try:
        global sendmoney
        sendmoney.destroy()
        return
    except:
        print()
    finally:
        sendmoney=Toplevel()
        sendmoney.title("Send Money")
        sendmoney.resizable(width=False, height=False)

        sendmessage=Label(sendmoney, text="Send Money to another account")
        recipientuser=Label(sendmoney, text="Reciever's username")
        payment=Label(sendmoney, text="Enter Amount:")
        passw=Label(sendmoney, text="Enter Password:")
        cvv=Label(sendmoney, text="Enter CVV:")
        e_recipientuser=Entry(sendmoney, width=15)
        e_payment=Entry(sendmoney, width=15)
        e_passw=Entry(sendmoney, show="*", width=15)
        e_cvv=Entry(sendmoney, show="*", width=15)
        paybutton=Button(sendmoney, text="Pay!", fg="green", padx=50, pady=10, command=lambda: sendlogic(user, sendmoney, sendmessage, int(e_payment.get()), e_passw.get(), e_cvv.get(), e_recipientuser.get()))
        backbutton=Button(sendmoney, command=sendmoney.destroy, text="Back", fg="red", padx=50, pady=10)


        sendmessage.grid(row=0, column=0, columnspan=3, pady=5)
        recipientuser.grid(row=2, column=0, pady=5, padx=5)
        e_recipientuser.grid(row=2, column=2, pady=5, padx=5)
        passw.grid(row=4, column=0, pady=5)
        e_passw.grid(row=4, column=2, pady=5)
        cvv.grid(row=5, column=0, pady=5)
        e_cvv.grid(row=5, column=2, pady=5)
        payment.grid(row=3, column=0, pady=5)
        e_payment.grid(row=3, column=2, pady=5)
        paybutton.grid(row=6, column=0)
        backbutton.grid(row=6, column=2)

def payelectric(user):
    #Try and except so that previous instance is closed before another is opened
    try:
        global bill1
        bill1.destroy()
        return
    except:
        print()
    finally:
        x=mc.execute(f"select balance from userinfo where accno = {user}")
        bal=mc.fetchone()
        bill1 = Toplevel()
        bill1.resizable(width=False, height=False)
        bill1.title("Pay Bills")
        n=StringVar()

        
        #Bill Page Elements
        title = Label(bill1 ,text="Pay Electricity bill")
        billamount = Label(bill1, text="Enter Amount:", padx=5)
        Accpasswd = Label(bill1, text="Enter Password:", padx=5)
        AccCVV = Label(bill1, text="Enter CVV:", padx=5)
        elecboard = Label(bill1, text="Select Board:")
        select_elecboard=ttk.Combobox(bill1, textvariable=n, width=15, state = "readonly")
        closebutton = Button(bill1, text="Close", command=bill1.destroy, fg="red", padx=50, pady=10)
        e_billamount = Entry(bill1,width=16)
        e_Accpasswd = Entry(bill1,width=16, show="*")
        e_AccCVV = Entry(bill1,width=16, show="*")
        paybutton = Button(bill1, text="Pay!", padx=50, pady=10,command=lambda: calculate_elec(title, int(e_billamount.get()), e_Accpasswd.get(), e_AccCVV.get(), select_elecboard.get(), user, bill1), fg="green")
        select_elecboard['values'] = ('BESCOM','CESC Mysore','GESCOM','HESCOM','MESCOM')
        select_elecboard.current(0)


        #Bill page Grid
        title.grid(row=0, column=0, columnspan=3, pady=5)
        elecboard.grid(row=4, column=0, pady=5, padx=5)
        select_elecboard.grid(row=4, column=2)
        closebutton.grid(row=10, column=2, pady=5, padx=6)
        paybutton.grid(row=10, column=0, pady=5, padx=19)
        Accpasswd.grid(row=5, column=0, pady=5, padx=5)
        AccCVV.grid(row=6, column=0, pady=5, padx=5)
        e_Accpasswd.grid(row=5, column=2, pady=5, padx=5)
        e_AccCVV.grid(row=6, column=2, pady=5, padx=5)
        billamount.grid(row=3, column=0, pady=5, padx=5)
        e_billamount.grid(row=3, column=2, pady=5, padx=5)


def trans_hist(filename):
    print(filename)
    open_file=open(filename,"r")
    file=csv.reader(open_file)
    tablerows=0
    data=[]
    for i in file:
        tablerows+=1
        data.append(i)      
   
    class MyFrame(wx.Frame):
        def __init__(self, parent, title):
            super(MyFrame, self).__init__(parent, title =title, size = (480,600))
            self.panel = MyPanel(self)
     
     
    class MyPanel(wx.Panel):
        def __init__(self, parent):
            super(MyPanel, self).__init__(parent)   

            mygrid = grid.Grid(self)
            mygrid.CreateGrid(tablerows,5)

            for x in range(tablerows):
                for y in range(5):
                    cellvalue=data[x][y]
                    mygrid.SetCellValue(x,y,str(cellvalue))
                    mygrid.SetReadOnly(x,y,True)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(mygrid, 1, wx.EXPAND)
            self.SetSizer(sizer)

    class MyApp(wx.App):
        def OnInit(self):
            self.frame = MyFrame(parent=None, title=filename)
            self.frame.Show()
            return True

    app = MyApp()
    app.MainLoop()

#=============================================
#       start of program execution
#=============================================
root=Tk()
root.withdraw()
loginwindow() 
    
