
from tkinter import *
from tkinter import messagebox
import time
import threading
from splinter import Browser
import re
from urllib.request import urlopen

import sys # for debug purpose
import os
import time
# path for chromedriver	
chromedriver_path = os.path.dirname(os.path.realpath(__file__))
executable_path = {'executable_path': chromedriver_path + '\chromedriver.exe'}

b = Browser('chrome', headless=True, **executable_path)

class GTENROLLAPP(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("GT ENROLL")
        self.resizable(False, False)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=50, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainPage, RollingPage):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="news")

        self.showFrame("MainPage")

        self.updateURL = "https://raw.githubusercontent.com/by-the-w3i/MSU_ROLL/master/VERSION"
        self.downloadURL = "https://github.com/by-the-w3i/MSU_ROLL"
        self.version = "1.0"



    def showFrame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def checkUpdates(self):
        try:
            with urlopen(self.updateURL) as response:
                latest_version = response.read().decode('utf-8').strip()
                if self.version != latest_version:
                    messagebox.showinfo(
                        "Update",
                        "Current Version: {}\n\nThe latest version {} is out.\n\nPlease download from {}".format(self.version, latest_version, self.downloadURL)
                    )
                else:
                    messagebox.showinfo(
                        "Update",
                        "Current version is the latest one."
                    )
        except:
            messagebox.showwarning(
                "Internet Error",
                "The Internet is NOT CONNECTED."
            )




class MainPage(Frame):
    def __init__(self, master, controller):
        # all the courses targets
        self.targets = []

        Frame.__init__(self, master)
        self.controller = controller
        # self.pack(padx=50, pady=20)
        # self.master.geometry('{}x{}'.format(500, 300))
        # self.master.tk_setPalette(background='#545454')

        Label(self, text="GT ID:").grid(row=0, column=0, sticky=E)
        Label(self, text="PASSWORD:").grid(row=1, column=0, sticky=E)

        self.ID_entry = Entry(self)

        self.PW_entry = Entry(self, show="*")

        self.ID_entry.grid(row=0, column=1, columnspan=2, sticky=(E,W))
        self.PW_entry.grid(row=1, column=1, columnspan=2, sticky=(E,W))
        self.ID_entry.focus_set()

        # Message(self, text="Seperate by a single space." ,fg='red', anchor=E, width=50).grid(row=3, columnspan=3)
        Label(self, text="CRN:").grid(row=3, column=0, sticky=E)
        self.sub_entry = Entry(self, width=10)
        self.sub_entry.insert(0,'99999')
        self.sub_entry.grid(row=3, column=1, columnspan=2, sticky=(E,W))

        Button(self, text="add to list", command=self.addCourse).grid(row=4, column=2, sticky=(E,W))

        self.courses = Listbox(self)
        self.courses.grid(row=5, column=0, columnspan=2)

        Button(self, text="delete", command=self.delCourse).grid(row=5, column=2, sticky=(E,W))

        Button(self, text="Start Enrolling >>>", command=self.rolling).grid(row=6,columnspan=3, sticky=(E,W))
        Button(self, text="Check for updates", command=lambda:self.controller.checkUpdates()).grid(row=7,columnspan=3, sticky=(E,W))


    def authentication(self, ID, PW):
        try:
            URL = " https://login.gatech.edu/cas/login?service=http%3A%2F%2Fbuzzport.gatech.edu%2Fsso"
			#replace "https://buzzport.gatech.edu/misc/preauth.html?"
            b.visit(URL)
            if b.is_element_present_by_id('username', wait_time=4):
               b.find_by_id("username").fill(ID)
            if b.is_element_present_by_id('password', wait_time=4):
               b.find_by_id("password").fill(PW)
            b.find_by_value("LOGIN").click()
            #print (b.html, "\n", b.url)
			
            if b.is_element_present_by_id('duo_iframe', wait_time=4):
              with b.get_iframe('duo_iframe') as iframe:
                if not iframe.is_element_present_by_css('.positive.auth-button', wait_time=5):
                   print ("No TFA")
                else:
                   print ("Found TFA")
                   time.sleep(5) # avoid invisible element issue				   
                   push = iframe.find_by_css('.positive.auth-button').first
                   push.click()

                   if not b.is_element_present_by_id('campusDirectory', wait_time=20):
                       print ("Not Authenticated")
                       return False					   
                   
                   print ("TFA html\n", b.html)
                   return True
						
            return False
        except:

            messagebox.showwarning(
                "System Error",
                "Error:{}\n{}".format(sys.exc_info()[0], sys.exc_info()[1])
            )

    def addCourse(self):
        course = self.sub_entry.get()
        
        if not course.isdigit():
            messagebox.showwarning(
                "Add Error",
                "Year: Please input a valid CRN! (make sure there is no space)"
            )

        else:
            info = course
            if info not in self.targets:
                self.targets.append(info)
                self.courses.insert(END, info)
            else:
                messagebox.showwarning(
                    "Add Error",
                    "Duplicate: {}".format(info)
                )

    def delCourse(self):
        to_del = self.courses.curselection()
        if len(to_del)==0 :
            messagebox.showwarning(
                "Delete Error",
                "No active course is selected ..."
            )
        else:
            ind = to_del[0]
            self.targets.remove(self.courses.get(ind))
            self.courses.delete(ind)


    def rolling(self):
        if len(self.targets)==0:
            messagebox.showwarning(
                "Error",
                "No class in the list. Please click 'add to list'."
            )
        elif self.ID_entry.get()=="" or self.PW_entry.get()=="":
            messagebox.showwarning(
                "Error",
                "NETID and PASSWORD can not be empty."
            )
            if self.ID_entry.get()=="":
                self.ID_entry.focus_set()
            else:
                self.PW_entry.focus_set()
        elif not self.authentication(self.ID_entry.get(), self.PW_entry.get()):
            messagebox.showwarning(
                "Error",
                "GT user name or PASSWORD or TFA is not correct."
            )
            self.ID_entry.focus_set()
        else:
            understand = messagebox.askyesno(
                "Notice",
                "Keep Computer Turned On and Connected to Internet."
            )
            if understand:
                self.controller.showFrame("RollingPage")
                self.controller.frames["RollingPage"].start_thread()
                # print("rollings")
            else:
                msg = messagebox.showinfo(
                    "Stay Calm",
                    "Do nothing"
                )

class RollingPage(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller


        Button(self, text="FAQs",command=self.faqs).pack()
        label = Label(self, text="Enrolling class for you ...")
        label.pack(side="top", fill="x", pady=10)
        button = Button(self, text="STOP Rolling and Quit",
                        command=lambda:controller.destroy())
        button.pack()


        Button(self, text="Live Status:",command=self.liveStatus).pack(pady=(10,0))
        self.msg = Message(self, text="Validating class list ...", width=500, fg="#25a5e4")
        self.msg.pack()

        self.status_table = {}
        self.ready_table = {}


    def start_thread(self):
        thread = threading.Thread(target=self.looping, args=())
        thread.daemon = True
        thread.start()

    def faqs(self):
        messagebox.showwarning(
            "FAQs",
            ">> ISSUES:\n Do not exit program"
        )

    def liveStatus(self):
        messagebox.showwarning(
            "Live Status",
            "[ERROR]\nThis class is not found.\n\n[READY]\nThis class will be enrolled when someone drops it.\n\n[ENROLLED]\nCongratulations!!! You Successfully enrolled this class.\n\n[FAILED]\nEnroll failed due to permission denied. (You may not have the right to enroll this class or You have already enrolled this class)"
        )

    def updateStatus(self, cls_lst, finish=False):
        clor = "#25a5e4"
        msg = ""
        for c in cls_lst:
            if c in self.status_table:
                msg += "[{}] {}\n".format(self.status_table[c], c)
            else:
                break
        if finish:
            msg += "\nEnroll FINISHED!!!\nPlease check your GT schedule."
            clor = "red"
        self.msg.configure(text=msg, fg=clor)

    def updateReady(self, contents):
        for k in self.ready_table:
            c = self.ready_table[k][1]
            plan_idx = re.findall('<a id="(.+)?" title="Enroll in {}"'.format(c), contents)[0][-1]
            self.ready_table[k][0] = plan_idx

    def looping(self):
        NETID = self.controller.frames["MainPage"].ID_entry.get()
        PASSWD = self.controller.frames["MainPage"].PW_entry.get()
        CLS_LST = self.controller.frames["MainPage"].targets

        #URL = "https://oscar.gatech.edu/pls/bprod/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu"
        URL_2 = "https://oscar.gatech.edu/pls/bprod/bwskfcls.p_sel_crse_search"
        URL_1 = "https://buzzport.gatech.edu/render.UserLayoutRootNode.uP?uP_tparam=utf&utf=%2Fcp%2Fip%2Flogin%3Fsys%3Dsct%26url%3Dhttps%3A%2F%2Foscar.gatech.edu/pls/bprod%2Fztgkauth.zp_authorize_from_login"
        URL_0 = "https://buzzport.gatech.edu/render.userLayoutRootNode.uP?uP_root=root"
        """
        b.visit(URL)
        print ("looping\n", b.html)
		
        home = b.find_by_css(".removable.dragTab.deleteTab.noFramedTab")[2]
        home.click()

        print (b.url, "looping home\n")

        oscar = b.find_by_css(".uportal-channel-text")[9]
        oscar.click()		
		
        print (b.url, "looping oscar\n")
		"""

        b.visit(URL_0)
        print (b.html, "\nlooping 0\n", b.url)
        b.visit(URL_1)		
        print (b.html, "\nlooping 1\n", b.url)
        b.visit(URL_2)		
        print (b.html, "\nlooping 2\n", b.url)
		
        pterm = b.find_by_id('term_input_id')
        pterm.select('201802')
        submit = b.find_by_value('Submit')
        submit.click()

        print (b.html, "\nlooping 3\n", b.url)

        sub = b.find_by_id('subj_id') 
        sub.select('ECE')
        submit = b.find_by_value('Course Search')
        submit.click()
		
        print (b.html, "\nlooping 4\n", b.url)
	
		
        for course in CLS_LST:            
            try:
                course = course			
                #to be implemented		
            except:
                # print("Error:", sys.exc_info()[0])
                self.status_table[course] = "ERROR"

            self.updateStatus(CLS_LST)


if __name__ == "__main__":
    root = GTENROLLAPP()
    root.mainloop()
