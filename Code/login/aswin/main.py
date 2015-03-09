from lib.MongoDBWrapper import MongoDBWrapper
import pprint
import os
import re

class Main:

    def __init__(self):
        self.exit    =False

        self.selection = {
            1:self.register,
            2:self.addStorage,
            3:self.upload,
            4:self.download,
            5:self.getfoldertree,
            6:self.deleteFile,
            7:self.createFolder,
            8:self.deleteFolder,
            9:self.spreadStorage,
            10:self.doexit
        }

        self.storageType = {
            1:'dropbox',
            2:'box',
            3:'googledrive'
        }

    #todo append this to ros program
    #arg: email
    def register(self):
        email       =raw_input("enter email address:")
        print "putting these info into database..."
        MongoDBWrapper().addAccount(email)
        #put these onto mongodb for record

    #todo dont know yet
    #arg: email, storage type must be in these form below
    def addStorage(self):
        email       =raw_input("enter email address:")
        storage     =int(raw_input("1.dropbox\n"
                                   "2.box\n"
                                   "3.googledrive\n"
                                   "choose 1-3 to add storage for account %s: " % (email)))
        MongoDBWrapper().addStorage(self.storageType[storage], email)

    def upload(self):
        '''
        test case:
        gdrive:
        1) /furniture

        2)upload /furniture/table.jpg to dropbox
        1 is removed, 2 added in dropbox
        '''
        email           ='aswin.setiadi@gmail.com'
        #to upload file in root folder, pass ''
        #below example means uploading file monkey.jpg to TCSA at /images folder
        virtualPath     =''
        fileLocation    ='files/orange.jpg'
        MongoDBWrapper().upload(email, virtualPath, fileLocation)
        print 'file stored in online storage. destroying local copy..'
        #todo
        #os.remove(fileLocation)
        print 'local copy destroyed'

    #arg: email, file path in tcsa, save path(must be full path!!)
    def download(self):
        email           ='aswin.setiadi@gmail.com'
        virtualPath     ='/files/testfile.txt'
        saveLocation    ='C:/Users/aswin/Downloads'
        MongoDBWrapper().download(email, virtualPath, saveLocation)

        pass

    #arg: email
    def getfoldertree(self):
        email='aswin.setiadi@gmail.com'
        pprint.pprint(MongoDBWrapper().getFolderTree(email))

    #arg: email, file path in tcsa
    def deleteFile(self):
        email='aswin.setiadi@gmail.com'
        virtualPath='/furniture/chair/chair.jpg'
        MongoDBWrapper().delFile(email, virtualPath)


    #arg: email, folder path including new folder name
    def createFolder(self):
        #to create folder in root folder, pass''
        email       ='aswin.setiadi@gmail.com'
        virtualPath ='/image/img'
        MongoDBWrapper().createFolder(email, virtualPath)


    def deleteFolder(self):
        email='aswin.setiadi@gmail.com'
        folderPath='/furniture/chair'
        MongoDBWrapper().deleteFolder(email, folderPath)
        pass

    def spreadStorage(self):
        MongoDBWrapper().spreadData('aswin.setiadi@gmail.com')

    def doexit(self):
        self.exit = True

    #for testing purpose
    def start(self):
        #if something infront / , match will fail
        #t='/as'
        #m=re.match(r'/as$', t)
        #print m.group()
        while not self.exit:
            #test= DropboxWrapper("asetiadi", 'aswin_setiadi@hotmail.com')
            #test.getAuthTokenFromXML('files/authList.xml')

            #do something here
            #test.uploadFile('files/monyet.jpg', 'folder/monyet.jpg')

            #test.uploadFile('files/monyet.jpg')
            #test.downloadFile('folder')
            #test.getPath('/')
            #arg order: local file path, destination file path
            #test.uploadFile('files/monyet.jpg')


            choice=int(raw_input("cloud storage simulation:\n"
                                "1. register\n"
                                "2. add storage\n"
                                "3. upload\n"
                                "4. download\n"
                                "5. getfoldertree\n"
                                "6. deletefile\n"
                                "7. createfolder\n"
                                "8. deletefolder\n"
                                "9. spreadstorage\n"
                                "10. exit\n"
                                "enter 1-10:"
                                ))
            if choice in self.selection.keys():
                self.selection[choice]()

            else:
                print "please enter 1-10 only!!!"

if __name__=='__main__':
    '''
    root=["/aswin//setiadi","/aswin/setiadi/img.jpg","/aswin/setiadi.jpg","/aswin/.setiadi","/aswin/setiadi", "/aswin", "/aswinn/l"]
    path2=["/name/aswin/setiadi.jpg","/name/aswin/setiadi", "/name/aswin", "/name/aswinn"]
    path3=["/name/aswin/setiadi.jpg","/name/aswin/setiadi", "/name/aswin", "/namee/aswinn"]
    folder="/aswin"
    folder2="/name/aswin"
    folder3="/name/aswin"
    for item in root:
        #parent folder, folder, file
        reObj=re.match(r'(^%s$)|(^%s/.*/(\.?[^/\.]+$))|(^%s/.*/([^/]+\.[^/]+)$)' % (folder,folder,folder), item)
        if reObj is not None:
            #item containt folder path
            print "[%s]"%reObj.group(1)
            print "[%s]"%reObj.group(3)
            print "[%s]"%reObj.group(5)
            print "#####################"
        else:
            print "[%s]"%item
            print "$$$$$$$$$$$$$$$$$$$$$"
    '''
    test=Main()
    test.start()
'''
s=slurpy.Slurpy()
s.register(os)
s.register(Main)
s.start()
'''
