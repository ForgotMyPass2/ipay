#iPay Code

from tkinter import *
from tkinter import ttk
import mysql.connector
import random

con=mysql.connector.connect(user="ipay", password="test", auth_plugin="mysql_native_password", host="localhost", database="ipay")
mc=con.cursor()
#"mc" is cursor variable.
#Globals used: Login

#==================================
#       backend functions
#==================================


def closewindow(name):
    name.destroy()
    #if name=="Login" or name=="home":
    #    root.destroy()

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

def addbalance(payment, passwd, cvv, user): #addmoney function
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
                    #success("Success!", "₹"+str(payment)+" has been added to your account", window)
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
    e_card_year=Spinbox(signup, from_=2021, to=2026, width=8, state = "readonly")
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
    print(type(user))

    
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
        global addmessage
        addmoney = Toplevel()
        addmoney.title("Add Money")
        addmoney.resizable(width=False, height=False)

    
        balance=Label(addmoney,text="Balance is ₹"+currentbal)
        addmessage = Label(addmoney, text="Enter Details below")
        pay = Label(addmoney, text="Amount to be added:")
        passw = Label(addmoney, text="Enter Password:")
        cvv = Label(addmoney, text="Enter CVV:")
        e_pay = Entry(addmoney, width=15)
        e_pass = Entry(addmoney, show="*", width=15)
        e_cvv = Entry(addmoney, width=15, show="*")
        pay_but = Button(addmoney, text="ADD", padx=50, pady=10, fg="green", activeforeground="green", command=lambda: addbalance(int(e_pay.get()), e_pass.get(), e_cvv.get(), user))
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
        balance.grid(row=0, column=0, columnspan=3, pady=5)

#=============================================
#       start of program execution
#=============================================
root=Tk()
root.withdraw()
loginwindow()    
    
