import os
import pprint
import re
from lib.DropboxWrapper import DropboxWrapper
from lib.MongoDBWrapper import MongoDBWrapper


class Main:

    def __init__(self):
        self.exit    =False
        self.mongodb =MongoDBWrapper('test', 'localhost', 27017)

        self.selection = {
            1:self.register,
            2:self.addStorage,
            3:self.upload,
            4:self.download,
            5:self.getfoldertree,
            6:self.deleteFile,
            7:self.createFolder,
            8:self.deleteFolder,
            9:self.renameFolder,
            10:self.doexit
        }

        self.storageType = {
            1:'dropbox',
            2:'box',
            3:'googledrive'
        }
    def register(self):
        email       =raw_input("enter email address:")
        print "putting these info into database..."
        self.mongodb.addAccount(email)
        #put these onto mongodb for record

    def addStorage(self):
        email       =raw_input("enter email address:")
        storage     =int(raw_input("1.dropbox\n"
                                   "2.box\n"
                                   "3.googledrive\n"
                                   "choose 1-3 to add storage for account %s: " % (email)))
        self.mongodb.addStorage(self.storageType[storage], email)


    def upload(self):
        email           ='aswin.setiadi@gmail.com'
        #to upload file in root folder, pass ''
        virtualPath     ='/images'
        fileLocation    ='files/monkey.jpg'
        self.mongodb.upload(email, virtualPath, fileLocation)

    def download(self):
        email           ='aswin.setiadi@gmail.com'
        virtualPath     ='/movies/comedy/monkey.jpg'
        saveLocation    ='C:/Users/aswin/Downloads'
        self.mongodb.download(email, virtualPath, saveLocation)

        pass

    def getfoldertree(self):
        email='aswin.setiadi@gmail.com'
        self.mongodb.getFolderTree(email)

    def deleteFile(self):
        email='aswin.setiadi@gmail.com'
        virtualPath='/furniture/chair/chair/chair.jpg'
        self.mongodb.delFile(email, virtualPath)


    def createFolder(self):
        #to create folder in root folder, pass''
        email       ='aswin.setiadi@gmail.com'
        virtualPath ='/files/animal/primate'
        self.mongodb.createFolder(email, virtualPath)


    def deleteFolder(self):
        pass


    def renameFolder(self):
        pass

    def doexit(self):
        self.exit = True

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
                                "9. renamefolder\n"
                                "10. exit\n"
                                "enter 1-10:"
                                ))
            if choice in self.selection.keys():
                self.selection[choice]()

            else:
                print "please enter 1-10 only!!!"


Main().start()