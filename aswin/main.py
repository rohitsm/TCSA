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
        storage     =int(raw_input("1.dropbox\n2.box\n3.googledrive\nchoose 1-3 to add storage for account %s: " % (email)))
        self.mongodb.addStorage(self.storageType[storage], email)


    def upload(self):
        email           ='aswin.setiadi@gmail.com'
        virtualPath     ='/files/animal/primate'
        fileLocation    ='files/monkey.jpg'
        self.mongodb.upload(email, virtualPath, fileLocation)

    def download(self):
        email           ='aswin.setiadi@gmail.com'
        virtualPath     ='/files/horse.jpg'
        saveLocation    ='C:/Users/aswin/Downloads'
        self.mongodb.download(email, virtualPath, saveLocation)

        pass

    def getfoldertree(self):
        email='aswin.setiadi@gmail.com'
        self.mongodb.getFolderTree(email)

    def deleteFile(self):

        pass


    def createFolder(self):
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
        #find existing parent folder, remove them

        #/sound
        #buat /sound/music

        #/sound
        #/sound/music.mp3
        #buat /sound/music

        #/music
        #buat /sound/music/list
        i=['/sound/sound',
           '/sound/music.mp3',
           '/music',

        ]

        j='/music/image'
        exist=False
        newFolder=j.split('/')[-1]
        m=re.match(r'(.*)/%s$' % newFolder, j )
        path=m.group(1)
        #print path
        #print newFolder
        for k in range(0, len(i)):
            if i[k] ==path:
                #print 'replace parent %s with new path %s' % (i[k], j)
                i[k]=j
                exist=True
                break
        if not exist:
            #print '%s appended' % j
            i.append(j)
        #print i


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