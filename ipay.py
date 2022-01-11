#iPay Program


from tkinter import *
from tkinter import ttk
import mysql.connector
import csv
import os
import datetime
import random

#port=int(input("Enter Port (0 for default): "))
#if port==0:
#    port="3306"
#port=str(port)
#host=input("Enter host (0 for localhost): ")
#if host=="0":
#    host="0.tcp.in.ngrok.io"
con=mysql.connector.connect(user="ipay", password="test", auth_plugin="mysql_native_password", host="localhost", database="ipay")
#con=mysql.connector.connect(user="root", password="test", auth_plugin="mysql_native_password", host="localhost", database="projectpay")
mc=con.cursor()

#if 1, program "stops"
close=0

#Functions will appear here
def getlogin(user, passw):#auth() func to authenthicate saved login
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
                LoginPass.delete(0, END)
    if result=="0":
        errorLogin=Label(Login, text="Incorrect Username", fg="red").grid(row=1, column=0, columnspan=3)
        LoginPass.delete(0, END)


def closehome():
    #Closes otp and root
    global close
    global home
    close = 1
    home.destroy()
    return
def closelogin():
    #Closes login and root
    global close
    global Login
    close = 1
    Login.destroy()
    return

def calculate_elec(payment, passwd, cvv, board, billno, user):
    #calculates and deducts electricity bill which has been input by user
    mc.execute(f"select balance,password,cvv from userinfo where accno = {user}")
    getinfo=mc.fetchone()
    if board!="":
        if getinfo[0]<payment:
            billTitle.configure(text="Too poor to pay",fg = "red")
        else:
            if passwd == getinfo[1]:
                if cvv.isdigit():
                    cvv=int(cvv)
                    if cvv == getinfo[2]:
                        mc.execute(f"update userinfo set balance=balance-{int(payment)} where accno = {user}")
                        billTitle.configure(text="Transaction Successful",fg = "green")
                        activebalance(billbalance, user)
                        transactionappend(board, "Debit", user)  
                    
                    else:
                        billTitle.configure(text="Invalid CVV!",fg = "red")
                    
                else:
                    billTitle.configure(text="CVV is not numeric!",fg = "red")
            else:
                billTitle.configure(text="Invalid password!",fg = "red")
             
    else:
        billTitle.configure(text="Choose Board!",fg = "red")
        

    
    con.commit()


def accno_gen():
    x=random.randint(100000, 999999)
    mc.execute("select username from userinfo")
    userinfo=mc.fetchall()
    if x in userinfo:
        accno_gen()
    else:
        return x
    
    
def signup_get(getname, getusername, getemail, getphone, getpass, getcardno, getcard_month, getcard_year, getcvv):
    accno_generated=accno_gen()
    mc.execute(f"select accno, card_no, phone from userinfo")
    acc_check=mc.fetchall()
    trueacc=0
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
                                            date=str(getcard_month+"_"+getcard_year)
                                            x="insert into userinfo (accno,name,email,phone,card_no,card_expiry,cvv,password,balance,username) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                            y=[(accno_generated),(getname.strip(" ")),((getemail.strip()).replace(" ","_")),(int(getphone)),(int(getcardno)),(date),(int(getcvv)),(getpass.rstrip(" ")),(0), (getusername)]
                                            mc.execute(x,y)
                                            con.commit()
                                            sign_title.configure(text="Success, now head to the Login Page!", fg="Green")
                                        else:
                                            sign_title.configure(text="Password length must be b/w 8 & 24", fg="red")

                                    else:
                                        sign_title.configure(text="CVV is Long/Short/Not Numeric", fg="red")
                                else:
                                    sign_title.configure(text="Card Number already in use", fg="red")
                            else:
                                sign_title.configure(text="Card No. is Long/Short/Not Numeric", fg="red")
                        else:
                            sign_title.configure(text="Phone Number already in use", fg="red")
                    else:
                        sign_title.configure(text="Invalid Phone No.", fg="red")
                else:
                    sign_title.configure(text="Email too long (how even)", fg="red")
    else:
        sign_title.configure(text="Name is too long(get a new one)", fg="red")

#sign_title.configure(text="Invalid Values, Check Again!", fg="red")
        

def balance(payment, passwd, cvv, user):
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
                    addmessage.configure(text="Transaction Successful",fg = "green")
                    activebalance(addbalance, user)
                
                else:
                    addmessage.configure(text="Invalid CVV!",fg = "red")
                
            else:
                addmessage.configure(text="CVV is not numeric!",fg = "red")
        else:
            addmessage.configure(text="Invalid password!",fg = "red")
        
        con.commit()

def sendlogic(user, payment, passwd, cvv, recieve):
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
                        activebalance(sendbalance, user)
                        sendmessage.configure(text="Transaction Successful",fg = "green")
                        mc.execute(f"select accno from userinfo where phone = {recieve}")
                        y=(mc.fetchone())[0]
                        transactionappend(str(recieve), "Debit", user)
                        transactionappend(str(user), "Credit", y)
                    else:
                        sendmessage.configure(text="Invalid Phone No.",fg = "red")
                else:
                    sendmessage.configure(text="Invalid CVV!",fg = "red")                    
            else:
                sendmessage.configure(text="CVV is not numeric!",fg = "red")
        else:
            sendmessage.configure(text="Invalid password!",fg = "red")
    con.commit()      
    return
    
def activebalance(message, user):
    global bal
    x=mc.execute(f"select balance from userinfo where accno = {user}")
    bal=mc.fetchone()
    message.configure(text="Balance is ₹"+str(bal[0]))
    homeMoney.configure(text="Your balance is ₹"+str(bal[0]))



def transactionappend(to, credit_debit, usernow):
    x=mc.execute(f"select balance from userinfo where accno = {usernow}")
    bal=mc.fetchone()
    mc.execute(f"insert into transaction_history (acc_no, date_of_transaction, debit_credit, recipient, balance, Time) values ({usernow}, CURDATE(), '{credit_debit}', '{to}', {bal[0]}, CURTIME())")
    con.commit()



def transactionlist(user):
    x=mc.execute(f"select date_of_transaction, Time, debit_credit, recipient, balance from transaction_history where acc_no = {user}")
    listall=mc.fetchall()
    y=mc.execute(f"select name from userinfo where accno = {user}")
    name1=mc.fetchone()
    name=""
    for i in range(len(name1[0].split())):
        if i==0:
            name+=name1[0].split()[i]
        else:
            name+="_"+name1[0].split()[i]        
    f=open(f"Transaction history of {name}.csv", "w", newline="")
    write=csv.writer(f)
    field=("Date of Transaction", "Time", "Debit/Credit", "Recipient", "Balance")
    write.writerow(field)
    for i in listall:
          write.writerow(i)
    f.close()
    os.system(f"libreoffice --calc Transaction\ history\ of\ {name[0]}.csv") 
    





    
#Page Functions will appear here
def loginwindow():
    global Login
    global LoginPass
    #Login Prompt
    Login = Toplevel(root)
    Login.resizable(width=False, height=False)
    Login.title("iPay: Login")
    #Login Page Elements
    LoginTitle   =  Label(  Login,  text="Welcome! Log in or Sign up" )
    LogUser      =  Label(  Login,  text="Username:")
    LoginUser    =  Entry(  Login)
    LogPass      =  Label(  Login,  text="Password:")
    LoginPass    =  Entry(  Login,  show="*")
    LoginButton  =  Button( Login,  text="Login",   command=lambda: getlogin(LoginUser.get(), LoginPass.get()),   padx=77)         #auth() func to authenthicate saved login
    SignupButton =  Button( Login,  text="Sign Up", command=signuppage, padx=77)         #signup() func. to add account to system
    exitButton   =  Button( Login,  text="Exit",    command=closelogin)
    

    #Login Page Grid
    LoginTitle.grid(row=0, column=0, pady=5, padx=50, columnspan=3) #Title
    LogUser.grid(row=2, column=0, pady=25, padx=0)  #Title
    LoginUser.grid(row=2, column=2, pady=0, padx=0) #Field
    LogPass.grid(row=3, column=0, pady=25)          #Title
    LoginPass.grid(row=3, column=2, pady=0, padx=0) #Field
    LoginButton.grid(row=5, column=0, pady=0, padx=0)#button
    SignupButton.grid(row=5, column=2, pady=0, padx=0)#button
    exitButton.grid(row=6, column=0, pady=0, padx=0, columnspan=3, sticky=E+W)#button


def homepage(user):
    #closes otp window and opens Homepage
    global loginwindow
    global home
    global homeMoney
    Login.destroy()
    home = Toplevel()
    home.resizable(width=False, height=False)
    home.title("iPay Home")

    #Logic
    mc.execute(f"select name from userinfo where accno = {user}")
    getname = mc.fetchone()
    x=mc.execute(f"select balance from userinfo where accno = {user}")
    bal=mc.fetchone()
        
    

    #HomePage Elements
    homeTitle = Label(home, text=f"Welcome back {getname[0]}")
    homeMoney = Label(home, text="Your balance is ₹"+str(bal[0]))
    homeExit = Button(home, text="Exit", command=closehome, width=25)
    homePay = Button(home, text="""Pay
electricity
bill""", command=lambda: payelectric(user), padx=20)
    homeAdd=Button(home, text="Add Money", command=lambda: addmoneywindow(user), pady=26, padx=14)
    homeTransacthistory=Button(home, text="""Transaction
history""", padx=11, pady=14, command=lambda: transactionlist(user))
    homeSend=Button(home, text="Send money", pady=25, padx=10, command=lambda: sendmoneywindow(user))
    

    #HomePage Grid
    homeTitle.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
    homeMoney.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
    homeExit.grid(row=6, column=0, columnspan=3)
    homePay.grid(row=2, column=2)
    homeAdd.grid(row=2, column=0)
    homeTransacthistory.grid(row=3, column=0)
    homeSend.grid(row=3, column=2)

    
def signuppage():
    global sign_title
    signup = Toplevel()
    signup.resizable(width=False, height=False)
    signup.title("Sign up!")

    sign_title=Label(signup, text="Enter Details below")
    sign_name=Label(signup, text="Name(no spaces) :")
    sign_username=Label(signup, text="Username:")
    sign_email=Label(signup, text="Email:")
    sign_phone=Label(signup, text="Phone Number:")
    sign_pass=Label(signup, text="Password:")
    sign_cardno=Label(signup, text="Card Number:")
    sign_cardexpiry=Label(signup, text="Card Expiry:")
    sign_cvv=Label(signup, text="CVV:")
    sign_signup=Button(signup, text="Sign up", padx=80, command=lambda: signup_get(signup_name.get(), signup_username.get(), signup_email.get(), signup_phone.get(), signup_pass.get(), signup_cardno.get(), str(signup_card_month.get()), str(signup_card_year.get()), signup_cvv.get()))
    sign_back=Button(signup, text="Back", command=signup.destroy, padx=90)
    signup_name=Entry(signup)
    signup_username=Entry(signup)
    signup_email=Entry(signup)
    signup_phone=Entry(signup)
    signup_pass=Entry(signup, show="*")
    signup_cardno=Entry(signup)
    signup_card_month=Spinbox(signup, from_=1, to=12, width=8, state = "readonly")
    signup_card_year=Spinbox(signup, from_=2021, to=2026, width=8, state = "readonly")
    signup_cvv=Entry(signup, show="*")

    
    sign_title.grid(row=0, column=0, columnspan=3)
    sign_name.grid(row=1, column=0)
    sign_username.grid(row=2, column=0)
    sign_email.grid(row=3, column=0)
    sign_phone.grid(row=4, column=0)
    sign_pass.grid(row=5, column=0)
    sign_cardno.grid(row=6, column=0)
    sign_cardexpiry.grid(row=7, column=0)
    sign_cvv.grid(row=8, column=0)
    sign_signup.grid(row=9, column=0, padx=5)
    sign_back.grid(row=9, column=1, columnspan=2)
    signup_name.grid(row=1, column=1, pady=10, padx=5, columnspan=2)
    signup_username.grid(row=2, column=1, pady=5, columnspan=2)
    signup_email.grid(row=3, column=1, pady=5, columnspan=2)
    signup_phone.grid(row=4, column=1, pady=5, columnspan=2)
    signup_pass.grid(row=5, column=1, pady=5, columnspan=2)
    signup_cardno.grid(row=6, column=1, pady=5, columnspan=2)
    signup_card_month.grid(row=7, column=1)
    signup_card_year.grid(row=7, column=2)
    signup_cvv.grid(row=8, column=1, pady=5, columnspan=2)

    
    
def payelectric(user):
    #Try and except so that previous instance is closed before another is opened
    try:
        global bill1
        bill1.destroy()
        return
    except:
        print()
    finally:
        global billTitle
        global billbalance
        x=mc.execute(f"select balance from userinfo where accno = {user}")
        bal=mc.fetchone()
        bill1 = Toplevel()
        bill1.resizable(width=False, height=False)
        bill1.title("Pay Bills")
        n=StringVar()

        
        #Bill Page Elements
        billbalance=Label(bill1,text="Balance is ₹"+str(bal[0]))
        billTitle = Label(bill1 ,text="Pay Electricity bill")
        billAccHeading = Label(bill1, text="Enter Bill no.:", padx=5)
        billamount = Label(bill1, text="Enter Amount:", padx=5)
        billAccpasswd = Label(bill1, text="Enter Password:", padx=5)
        billAccCVV = Label(bill1, text="Enter CVV:", padx=5)
        billboard = Label(bill1, text="Select Board:")
        billboard_select=ttk.Combobox(bill1, textvariable=n, width=15, state = "readonly")
        billClose = Button(bill1, text="Close", command=bill1.destroy, fg="red", padx=50, pady=10)
        billAccEntry = Entry(bill1,width=16)
        billamount_Entry = Entry(bill1,width=16)
        billAccpasswd_Entry = Entry(bill1,width=16, show="*")
        billAccCVV_Entry = Entry(bill1,width=16, show="*")
        billPayButton = Button(bill1, text="Pay!", padx=50, pady=10,command=lambda: calculate_elec(int(billamount_Entry.get()), billAccpasswd_Entry.get(), billAccCVV_Entry.get(), billboard_select.get(), billAccEntry.get(), user), fg="green")
        billboard_select['values'] = ('BESCOM','CESC Mysore','GESCOM','HESCOM','MESCOM')
        billboard_select.current(1)


        #Bill page Grid
        billTitle.grid(row=0, column=0, columnspan=3, pady=5)
        billAccHeading.grid(row=2, column=0)
        billboard.grid(row=4, column=0, pady=5, padx=5)
        billboard_select.grid(row=4, column=2)
        billClose.grid(row=10, column=2, pady=5, padx=6)
        billAccEntry.grid(row=2, column=2, pady=5)
        billPayButton.grid(row=10, column=0, pady=5, padx=19)
        billAccpasswd.grid(row=5, column=0, pady=5, padx=5)
        billAccCVV.grid(row=6, column=0, pady=5, padx=5)
        billAccpasswd_Entry.grid(row=5, column=2, pady=5, padx=5)
        billAccCVV_Entry.grid(row=6, column=2, pady=5, padx=5)
        billamount.grid(row=3, column=0, pady=5, padx=5)
        billamount_Entry.grid(row=3, column=2, pady=5, padx=5)
        billbalance.grid(row=1, column=0, columnspan=3, padx=5, pady=5)



def addmoneywindow(user):
    try:
        global addmoney
        addmoney.destroy()
        return
    except:
        print()
    finally:
        global addmessage
        global addbalance
        x=mc.execute(f"select balance from userinfo where accno = {user}")
        bal=mc.fetchone()
        addmoney = Toplevel()
        addmoney.title("Add Money")
        addmoney.resizable(width=False, height=False)

    
        addbalance=Label(addmoney,text="Balance is ₹"+str(bal[0]))
        addmessage = Label(addmoney, text="Enter Details below")
        addpay = Label(addmoney, text="Amount to be added:")
        addpass = Label(addmoney, text="Enter Password:")
        addcvv = Label(addmoney, text="Enter CVV:")
        addpay_ent = Entry(addmoney, width=15)
        addpass_ent = Entry(addmoney, show="*", width=15)
        addcvv_ent = Entry(addmoney, width=15, show="*")
        addpay_but = Button(addmoney, text="ADD", padx=50, pady=10, fg="green", activeforeground="green", command=lambda: balance(int(addpay_ent.get()), addpass_ent.get(), addcvv_ent.get(), user))
        addexit_but = Button(addmoney, text="Back", command=addmoney.destroy, padx=50, pady=10, fg="red", activeforeground="red")


        addpay.grid(row=2, column=0, pady=5, padx=3)
        addpass.grid(row=3, column=0, pady=5)
        addcvv.grid(row=4, column=0, pady=5)
        addpay_ent.grid(row=2, column=2, padx=3)
        addpass_ent.grid(row=3, column=2)
        addcvv_ent.grid(row=4, column=2)
        addpay_but.grid(row=5, column=0)
        addexit_but.grid(row=5, column=2)
        addmessage.grid(row=1, column=0, columnspan=3)
        addbalance.grid(row=0, column=0, columnspan=3, pady=5)



def sendmoneywindow(user):
    try:
        global sendmoney
        sendmoney.destroy()
        return
    except:
        print()
    finally:
        global sendmessage
        global sendbalance
        x=mc.execute(f"select balance from userinfo where accno = {user}")
        bal=mc.fetchone()
        sendmoney=Toplevel()
        sendmoney.title("Send Money")
        sendmoney.resizable(width=False, height=False)


        sendbalance=Label(sendmoney, text="Balance is ₹"+str(bal[0]))
        sendmessage=Label(sendmoney, text="Send Money to another account")
        sendrecipientuser=Label(sendmoney, text="Reciever's username")
        sendpayment=Label(sendmoney, text="Enter Amount:")
        sendpass=Label(sendmoney, text="Enter Password:")
        sendcvv=Label(sendmoney, text="Enter CVV:")
        sendrecipientuser_entry=Entry(sendmoney, width=15)
        sendpayment_entry=Entry(sendmoney, width=15)
        sendpass_entry=Entry(sendmoney, show="*", width=15)
        sendcvv_entry=Entry(sendmoney, show="*", width=15)
        sendpay=Button(sendmoney, text="Pay!", fg="green", padx=50, pady=10, command=lambda: sendlogic(user, int(sendpayment_entry.get()), sendpass_entry.get(), sendcvv_entry.get(), sendrecipientuser_entry.get()))
        sendback=Button(sendmoney, command=sendmoney.destroy, text="Back", fg="red", padx=50, pady=10)


        sendbalance.grid(row=1, column=0, columnspan=3, pady=10)
        sendmessage.grid(row=0, column=0, columnspan=3, pady=5)
        sendrecipientuser.grid(row=2, column=0, pady=5, padx=5)
        sendrecipientuser_entry.grid(row=2, column=2, pady=5, padx=5)
        sendpass.grid(row=4, column=0, pady=5)
        sendpass_entry.grid(row=4, column=2, pady=5)
        sendcvv.grid(row=5, column=0, pady=5)
        sendcvv_entry.grid(row=5, column=2, pady=5)
        sendpayment.grid(row=3, column=0, pady=5)
        sendpayment_entry.grid(row=3, column=2, pady=5)
        sendpay.grid(row=6, column=0)
        sendback.grid(row=6, column=2)


root=Tk()
root.withdraw()
loginwindow()

if close==1:
    root.destroy()
