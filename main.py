# Program generates the commands to create a nfs volume on NetApp storage
# pip install tkinter
# pip install pyperclip

import tkinter
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Button
from tkinter import messagebox
import pyperclip as pc

inputDataDict = {
            'lidCode':'',
            'sbgCode':'',
            'bacCode;':'',
            'shareName':'',
            'shareSize':'',
            'vserver':'',
            'volumeName':'',
            'aggr':'',
            'snapshot':'',
            'percentSnap':'',
            'snapmirror':'',
            'ritm':'',
            'sctask':'',
            'chg':'',
            'owner':'',
            'comment':'',
            'efficiency':'',
            'exportPolicyCmds':'',
            'volumeName':'',
            'cmdText':''
            }

# cmdText = 'Initial Value of cmdText'    #declare global var for pyperclip3

aggrList = []
vserverList = []
snapshotList = []
efficiencyList = []

def readFile(textFile,list):
    file = open(textFile, 'r')
    for line in file:
        line = line.strip()
        if list == aggrList:
            aggrList.append(line)
        elif list == vserverList:
            vserverList.append(line)
        elif list == snapshotList:
            snapshotList.append(line)
        elif list == efficiencyList:
            efficiencyList.append(line)
    file.close()

def getInput():
    inputDataDict['lidCode'] = lidEntry.get()
    inputDataDict['sbgCode'] = sbgEntry.get()
    inputDataDict['bacCode'] = bacEntry.get()
    inputDataDict['shareName'] = shareNameEntry.get()
    inputDataDict['shareSize'] = shareSizeEntry.get()
    inputDataDict['vserver'] = vserverComboBox.get()
    inputDataDict['aggr'] = aggrComboBox.get()
    inputDataDict['snapshot'] = snapshotComboBox.get()
    inputDataDict['snapmirror'] = snapmirrorComboBox.get()
    inputDataDict['efficiency'] = efficiencyComboBox.get()
    inputDataDict['ritm'] = ritmEntry.get()
    inputDataDict['chg'] = chgEntry.get()
    inputDataDict['sctask'] = sctaskEntry.get()
    inputDataDict['owner'] = ownerEntry.get()
    inputDataDict['comment'] = commentText.get('1.0','end-1c')
    # create volume name
    svm = inputDataDict['vserver']
    inputDataDict['volumeName'] = f'{inputDataDict["lidCode"]}_{inputDataDict["sbgCode"]}_{inputDataDict["bacCode"]}_{inputDataDict["shareName"]}_{svm[-4:]}'
    
    # get the IP addresses for export-policy, can have spaces, commas, tabs and line returns
    exportIps = []
    exportIps = exportIpsText.get('1.0','end-1c')
    exportIps = exportIps.replace(' ',',')
    exportIps = exportIps.replace('\t',',')
    exportIps = exportIps.replace('\n',',')
    exportIps = exportIps.split(',')
    newIps = []
    for i in exportIps:
        if i != '':
            newIps.append(i)
    exportIps = newIps
    x=1
    exportRulesList = []
    for i in exportIps:
        exportCmd = (f'export-policy rule create -vserver {inputDataDict["vserver"]} -policyname {inputDataDict["volumeName"]} -clientmatch {i} -rorule any -rwrule any -protocol nfs -superuser any -ruleindex {x}')
        exportRulesList.append(exportCmd)
        x = x+1
    inputDataDict['exportPolicyCmds'] = '\n'.join(exportRulesList)

    # determine snapmirror and snapshot config
    inputDataDict['percentSnap'] = ''
    if inputDataDict['snapmirror'] == 'unprotected' and inputDataDict['snapshot'] == "none":
        inputDataDict['percentSnap'] = '0'
    else:
        inputDataDict['percentSnap'] = '10'
        inputDataDict['shareSize'] = round((float(inputDataDict['shareSize']) / 0.9),2)
        inputDataDict['shareSize'] = str(inputDataDict['shareSize'])
    checkForMissing()

def checkForMissing():
    # check for missing mandatory fields
    if inputDataDict['lidCode'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the LID')
    elif inputDataDict['sbgCode'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the SGB')
    elif inputDataDict['bacCode'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the BAC')
    elif inputDataDict['shareName'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Share Name')
    elif inputDataDict['shareSize'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Share Size')
    elif inputDataDict['vserver'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Vserver')
    elif inputDataDict['aggr'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Aggregate')
    elif inputDataDict['snapshot'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Snapshot Policy')
    elif inputDataDict['snapmirror'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Snapmirror Policy')
    elif inputDataDict['efficiency'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Efficiency Policy')
    elif inputDataDict['exportPolicyCmds'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Export Policy IPs')
    elif inputDataDict['owner'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Owner/Requester Email')
    elif inputDataDict['comment'] == '':
        tkinter.messagebox.showwarning(title='Error',message='You forgot the Comment')
    else:
        writeCommands(inputDataDict)

def rewriteFrames():
    cmdOutputFrame.grid_remove()
    backButton.grid_remove()
    copyButton.grid_remove()
    volInfoFrame.grid(row = 0,column = 0,sticky="news", padx=20, pady=20)
    ticketInfoFrame.grid(row = 1,column = 0, sticky = "news", padx=20, pady=20)
    createButton.grid(row=0, column=0,ipadx=5, ipady=5,padx=10, pady=10)

def writeCommands(input): # input is a dictionary of all the variables needed for the commands..i.e. inputDataDict populated in the getInput function
    volInfoFrame.grid_remove()
    ticketInfoFrame.grid_remove()
    createButton.grid_remove()
    backButton.grid(row=0,column=0,ipadx=5,ipady=5,padx=10,pady=10)
    copyButton.grid(row=0,column=1,ipadx=5,ipady=5,padx=10,pady=10)
    cmdOutputFrame.grid(row = 0,column = 0,sticky="news", padx=20, pady=20)
    cmdOutputText = tkinter.Text(cmdOutputFrame, wrap=tkinter.WORD, width=100, height=25, font=("Courier", 10))
    cmdOutputText.grid(row=1, column=0)
    cmdOutputText.insert("1.0", f'vol create -vserver {input["vserver"]} -volume {input["volumeName"]} -size {input["shareSize"]}gb -aggregate {input["aggr"]} -security-style unix -state online -type RW -snapshot-policy {input["snapshot"]} -percent-snapshot-space {input["percentSnap"]} -vserver-dr-protection {input["snapmirror"]} -junction-path /{input["volumeName"]} -comment "{input["ritm"]}-{input["sctask"]}-{input["chg"]}-{input["owner"]} {input["comment"]}"\nvol efficiency on -vserver {input["vserver"]} -volume {input["volumeName"]}\nvol efficiency modify -vserver {input["vserver"]} -volume {input["volumeName"]} -policy {input["efficiency"]}\nexport-policy create -vserver {input["vserver"]} -policyname {input["volumeName"]}\n{input["exportPolicyCmds"]}\nvol modify -vserver {input["vserver"]} -volume {input["volumeName"]} -policy {input["volumeName"]}')
    for widget in cmdOutputFrame.winfo_children():
        widget.grid_configure(padx=10, pady=10)
    input['cmdText'] = cmdOutputText.get('1.0','end-1c')
    inputDataDict['cmdText'] = input['cmdText']
    # print('inside write cmds = ',input['cmdText'])

def copyCmds():     #copy text to clipboard
    pc.copy(inputDataDict['cmdText'])

#region

# read text files to populate comboBoxes
readFile('aggrList.txt',aggrList)
readFile('vserverList.txt',vserverList)
readFile('snapshotList.txt',snapshotList)
readFile('efficiencyList.txt',efficiencyList)

# Create the main window
window = tkinter.Tk()
window.title('NFS Create Volume Commands')

# Create the first frame inside the main window
frame = tkinter.Frame(window)
frame.pack()

# create "Volume Information" frame and everything in it. 
volInfoFrame = tkinter.LabelFrame(frame,text="Volume Info",bd=4)
volInfoFrame.grid(row = 0,column = 0,sticky="news", padx=20, pady=20)
# location code
lidLabel = tkinter.Label(volInfoFrame, text="LID")
lidLabel.grid(row = 0,column = 0)
lidEntry = tkinter.Entry(volInfoFrame)
lidEntry.insert(0,"abc")    
lidEntry.grid(row=0,column=1)
# department/business group code
sbgLabel = tkinter.Label(volInfoFrame, text="SBG")   
sbgLabel.grid(row = 1,column = 0)
sbgEntry = tkinter.Entry(volInfoFrame)
sbgEntry.insert(0,'temp')
sbgEntry.grid(row=1,column=1)
# billing account code
bacLabel = tkinter.Label(volInfoFrame, text="BAC")
bacLabel.grid(row = 2,column = 0)
bacEntry = tkinter.Entry(volInfoFrame)
bacEntry.insert(0,'000111')
bacEntry.grid(row=2,column=1)
# share name
shareNameLabel = tkinter.Label(volInfoFrame, text="Share Name")
shareNameLabel.grid(row = 3,column = 0)
shareNameEntry = tkinter.Entry(volInfoFrame)
shareNameEntry.insert(0,'testshare')
shareNameEntry.grid(row=3,column=1)
# share size
shareSizeLabel = tkinter.Label(volInfoFrame, text="Share Size in GB")
shareSizeLabel.grid(row=4,column = 0)
shareSizeEntry = tkinter.Entry(volInfoFrame)
shareSizeEntry.insert(0,'300')
shareSizeEntry.grid(row=4,column=1)
# vserver
vserverLabel = tkinter.Label(volInfoFrame,text="Vserver")
vserverComboBox = ttk.Combobox(volInfoFrame, values=vserverList)
vserverComboBox.insert(0,"vserver1001")
vserverLabel.grid(row=0, column=3)
vserverComboBox.grid(row=0, column=4)
#aggregate
aggrLabel = tkinter.Label(volInfoFrame,text="Aggregate")
aggrComboBox = ttk.Combobox(volInfoFrame, values=aggrList)
aggrComboBox.insert(0,'aggregate1')
aggrLabel.grid(row=1, column=3)
aggrComboBox.grid(row=1, column=4)
# snapshot policy
snapshotLabel = tkinter.Label(volInfoFrame,text="Snapshot Policy")
snapshotComboBox = ttk.Combobox(volInfoFrame, values=snapshotList)
snapshotComboBox.insert(0,'snapPolicy1')
snapshotLabel.grid(row=2, column=3)
snapshotComboBox.grid(row=2, column=4)
# snapmirror policy
snapmirrorLabel = tkinter.Label(volInfoFrame,text="Snapmirror")
snapmirrorComboBox = ttk.Combobox(volInfoFrame, values=["protected","unprotected"])
snapmirrorComboBox.insert(0,'protected')
snapmirrorLabel.grid(row=3, column=3)
snapmirrorComboBox.grid(row=3, column=4)
# efficiency policy
efficiencyLabel = tkinter.Label(volInfoFrame,text="Efficiency Policy")
efficiencyComboBox = ttk.Combobox(volInfoFrame, values=efficiencyList)
efficiencyComboBox.insert(0,'Sat_10am')
efficiencyLabel.grid(row=4, column=3)
efficiencyComboBox.grid(row=4, column=4)
# export policy
exportIpsLabel = tkinter.Label(volInfoFrame, text="Export Policy IPs")
exportIpsLabel.grid(row=5, column=0)
exportIpsText = scrolledtext.ScrolledText(volInfoFrame, wrap=tkinter.WORD, width=30, height=3, font=("Courier", 10))
exportIpsText.insert(1.0,'10.10.10.1, ,  ,\n10.10.10.2    10.10.10.3')
exportIpsText.grid(row=5, column=1, columnspan = 4, sticky = "news")
for widget in volInfoFrame.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# create the "ticketInfoFrame" and everything in it
ticketInfoFrame = tkinter.LabelFrame(frame,text="Volume Comment Info",bd=4)
ticketInfoFrame.grid(row = 1,column = 0, sticky = "news", padx=20, pady=20)
# ticket info using Service Now 
ritmLabel = tkinter.Label(ticketInfoFrame, text="RITM")
ritmLabel.grid(row = 0,column = 0)
ritmEntry = tkinter.Entry(ticketInfoFrame)
ritmEntry.insert(0,'RITM000111')
ritmEntry.grid(row=1,column=0)
chgLabel = tkinter.Label(ticketInfoFrame, text="CHG")
chgLabel.grid(row = 0,column = 1)
chgEntry = tkinter.Entry(ticketInfoFrame)
chgEntry.insert(0,'CHG000111')
chgEntry.grid(row=1,column=1)
sctaskLabel = tkinter.Label(ticketInfoFrame, text="SCTASK")
sctaskLabel.grid(row = 0,column = 2)
sctaskEntry = tkinter.Entry(ticketInfoFrame)
sctaskEntry.insert(0,'SCTASK000111')
sctaskEntry.grid(row=1,column=2)
ownerLabel = tkinter.Label(ticketInfoFrame, text="Owner/Requester Email")
ownerLabel.grid(row = 2,column = 0)
ownerEntry = tkinter.Entry(ticketInfoFrame)
ownerEntry.insert(0,'jondoe@email.com')
ownerEntry.grid(row=3,column=0,columnspan = 2)
commentLabel = tkinter.Label(ticketInfoFrame, text="Comment")
commentLabel.grid(row=4, column=0)
commentText = tkinter.Text(ticketInfoFrame, wrap=tkinter.WORD, width=30, height=2, font=("Courier", 10))
commentText.insert(1.0,'comment text')
commentText.grid(row=5, column=0, columnspan = 3)
for widget in ticketInfoFrame.winfo_children():
    widget.grid_configure(padx=10, pady=5, sticky="news")

#endregion

# create button frame and removed border from the frame
buttonFrame = tkinter.LabelFrame(frame,bd='0')
buttonFrame.grid(row=2,column=0,padx=10,pady=10)
createButton = Button(buttonFrame,text='Create Commands',bd='4',font=('Helvetica',10),command=getInput)
createButton.grid(row=0,column=0,ipadx=5,ipady=5,padx=10,pady=10)
cmdOutputFrame = tkinter.LabelFrame(frame,text="Command Output")
backButton = Button(buttonFrame,text='Back',bd='4',font=('Helvetica',10),command=rewriteFrames)
closeButton = Button(buttonFrame,text='Close',bd='4',font=('Helvetica',10),command=window.destroy)
closeButton.grid(row=0,column=2,ipadx=5,ipady=5,padx=10,pady=10)
copyButton = Button(buttonFrame,text='Copy Commands',bd='4',font=('Helvetica',10),command=copyCmds)

window.mainloop()