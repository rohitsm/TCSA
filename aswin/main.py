from lib.MongoDBWrapper import MongoDBWrapper
import os

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
            9:self.renameFolder,
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

    #arg: email, folder path in TCSA
    def upload(self):
        email           ='aswin.setiadi@gmail.com'
        #to upload file in root folder, pass ''
        #below example means uploading file monkey.jpg to TCSA at /images folder
        virtualPath     ='/images'
        fileLocation    ='files/monkey.jpg'
        MongoDBWrapper().upload(email, virtualPath, fileLocation)
        print 'file stored in online storage. destroying local copy..'
        os.remove(fileLocation)
        print 'local copy destroyed'

    #arg: email, file path in tcsa, save path(must be full path!!)
    def download(self):
        email           ='aswin.setiadi@gmail.com'
        virtualPath     ='/movies/comedy/monkey.jpg'
        saveLocation    ='C:/Users/aswin/Downloads'
        MongoDBWrapper().download(email, virtualPath, saveLocation)

        pass

    #arg: email
    def getfoldertree(self):
        email='aswin.setiadi@gmail.com'
        MongoDBWrapper().getFolderTree(email)

    #arg: email, file path in tcsa
    def deleteFile(self):
        email='aswin.setiadi@gmail.com'
        virtualPath='/furniture/chair/chair/chair.jpg'
        MongoDBWrapper().delFile(email, virtualPath)


    #arg: email, folder path including new folder name
    def createFolder(self):
        #to create folder in root folder, pass''
        email       ='aswin.setiadi@gmail.com'
        virtualPath ='/files/animal/primate'
        MongoDBWrapper().createFolder(email, virtualPath)


    def deleteFolder(self):
        pass

    def renameFolder(self):
        pass

    def doexit(self):
        self.exit = True

    #for testing purpose
    def start(self):
        #if something infront / , match will fail
        #t='/as'
        #m=re.match(r'/as$', t)
        #print m.group()
        test=1^20
        print test
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

test=Main()
test.start()
'''
s=slurpy.Slurpy()
s.register(os)
s.register(Main)
s.start()
'''
