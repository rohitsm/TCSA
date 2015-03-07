__author__ = 'aswin'
import pprint
import re
from pymongo import MongoClient
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper
from Test import Test
import os
import ConfigParser


#ross library
#from Code.login.dropbox_conn import get_dropbox_access_token
#from Code.login.gdrive_conn import get_gdrive_refresh_token

class MongoDBWrapper:
    """
    This class handle communication between the python program and the mongodb
    database        =database
    collection      =table
    record          =row

    """



    def __init__(self):
        config= ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),'mongodbconfig.ini'))
        section=config.sections()[0]
        allOptions  =config.options(section)
        databaseName=config.get(section, allOptions[0])
        addr        =config.get(section, allOptions[1])
        port        =int(config.get(section, allOptions[2]))


        self.client         = MongoClient(addr, port)
        self.db             = self.client[databaseName]

        #each collection represent a user
        self.aCollection    = None
        #for dropbox
        self.accessToken    = None
        #for googledrive
        self.credential     = None

        self.STORAGE_LIMIT_BUFFER=1024.0
        self.ros=False
    ###################################################################################################################
    def _getAccessToken(self, email):
        if self.ros:
            return get_dropbox_access_token()
        else:
            return Test().getAuthToken(email)
    def _getCredential(self, email):
        if self.ros:
            return get_gdrive_refresh_token()
        else:
            return Test().getCredentials(email)
    ###################################################################################################################
    #get storage size
    def _getDropboxRemainingStorage(self, accessToken):
        return DropboxWrapper(accessToken).getDropboxStorageSizeLeft()

    def _getBoxRemainingStorage(self):
        pass

    def _getGoogleDriveRemainingStorage(self, credentials):
        return GoogleDriveWrapper(credentials).getStorageSizeLeft()
    ###################################################################################################################

    def setCollection(self, email):
        self.aCollection    = self.db[email]

    ###################################################################################################################
    def _getLargestRemainingStorage(self, email):
        aList=[]
        #storageSizePair={}
        #return a list of 1 element(dictionary), chose dict element called 'storage'
        #will return [{u'type': u'dropbox', u'metadata': []},{u'type': u'googledrive', u'metadata': []}], etc
        storageList=self.aCollection.find({},{'_id':0,'type':1})
        for storage in storageList:
            if storage['type'] == 'dropbox':
                #ROS function here
                #email from phyu need to compare in session list
                #inside ross dropbox_conn implemented session checking
                self.accessToken= self._getAccessToken(email)
                #storageSizePair['dropbox']=self._getDropboxRemainingStorage(self.accessToken)
                aList.append(("dropbox", self._getDropboxRemainingStorage(self.accessToken)))
            elif storage['type'] == 'box':
                raise NotImplementedError
            elif storage['type'] == 'googledrive':
                #ROS server here
                self.credential= self._getCredential(email)
                #storageSizePair['googledrive']=self._getGoogleDriveRemainingStorage(self.credential)
                aList.append(("googledrive", self._getGoogleDriveRemainingStorage(self.credential)))

        #itermitems() will generate a set of tuples eg. ('a', 1000), the key argument dictate
        #the function to compare the second value(1000), hence the function x[1]
        #return (key, value) tuple so put [0] to get the storage
        #chosenStorage= max(storageSizePair.iteritems(), key= lambda x: x[1])[0]
        aList= sorted(aList, key= lambda x: x[1])
        print aList[0][0], ' has largest remaining storage.'
        #choseStorage is a string of either:
        #dropbox,box, googledrive
        return aList

    def _getAnyStorage(self):
        #can be dropbox,box, googledrive
        return self.aCollection.find({},{'_id':0,'type':1})[0]['type']


    def _getAllVirtualPathList(self):
        aListOfTuple=[]
        storages=self.aCollection.find(
            {},{'_id':0,'metadata.virtualPath':1, 'type':1}
        )
        for storage in storages:
            for path in storage['metadata']:
                aListOfTuple.append((path['virtualPath'], storage['type']))
        return aListOfTuple


    def _replaceVirtualOldPath(self, newVirtualPath, chosenStorage=None, newRecord=None):
        #this function is called to prevent duplicate from creating new folder/file record in database

        #if calling function is storing a folder, call with arg(email, folderPath)
        #if calling function is storing file in googldrive, call with arg(email, filePath, newRecord= mongodb record as dict)
        #if calling function is storing file in dropbox, call with arg(email, filePath)


        """
        NOTE: new file/folder must not be in root
        replace parent path record with this new record
        e.g. inserting /aswin/setiadi/awesome.pdf will replace /aswin/setiadi
        test cases to consider:
        -create folder with folderPath exist
        -create folder without folderPath exist
        -upload file with folderPath exist and Dropbox
        -upload file with folderPath exist and Googledrive
        -upload file with folderPath exist(dropbox) and Googledrive
        -upload file with folderPath not exist and Dropbox
        -upload file with folderPath not exist and Googledrive
        """

        newItem=newVirtualPath.split('/')[-1]
        m=re.match(r'(.*)/%s$' % newItem, newVirtualPath)
        #path will be like /aswin/setiadi
        path=m.group(1)

        aListOfTuple=self._getAllVirtualPathList()

        #check if parent path exist
        for virtualPathItem in aListOfTuple:
            if virtualPathItem[0] == path:
                #path exist for folder/file to be created
                ########################################################################
                exist= True
                if newRecord is not None:
                    #storage is googledrive and is a file, must include fileID
                    if virtualPathItem[1]=='googledrive':
                        #folderPath in googldrive, update this record
                        self.aCollection.update(
                            {
                                 'metadata.virtualPath':virtualPathItem[0]
                            },
                            {
                                '$set':{
                                    'metadata.$.virtualPath':newRecord['virtualPath'],
                                    'metadata.$.fileID'     :newRecord['fileID']
                                }
                            }
                        )
                    else:
                        #parentPath not googledrive, delete old record
                        self.aCollection.update(
                            #if this empty, can only update first storagerecord type
                            #and will wipe all entry in that storage according to the parameter
                            {'type':virtualPathItem[1]},
                            {
                                '$pull':{
                                    'metadata':{'virtualPath':virtualPathItem[0]}
                                }
                            }
                        )
                        #insert this new virtualPath to googledrive storage
                        self.aCollection.update(
                            {'type':'googledrive'},
                            {'$push':{'metadata':newRecord}}
                        )
                else:
                    if chosenStorage is None:
                        #calling method is createFolder
                        self.aCollection.update(
                            {
                                 'metadata.virtualPath':virtualPathItem[0]
                            },
                            {
                                '$set':{
                                    'metadata.$.virtualPath':newVirtualPath
                                }
                            }
                        )
                    else:
                        #calling method is uploadFile to a storage but must not googledrive
                        if virtualPathItem[1]==chosenStorage:
                            #file storage same as parentFolderPath storage
                            self.aCollection.update(
                                {
                                     'metadata.virtualPath':virtualPathItem[0]

                                },
                                {
                                    '$set':{
                                        'metadata.$.virtualPath':newVirtualPath
                                    }
                                }
                            )
                        else:
                            #file is stored in different storage than parentFolderPath
                            #delete old record
                            self.aCollection.update(
                                #if this query parameter empty, can only update first storagerecord type
                                #and will wipe all entry in that storage according to the parameter
                                {'type':virtualPathItem[1]},
                                {
                                    '$pull':{
                                        'metadata':{
                                            'virtualPath':virtualPathItem[0]
                                        }
                                    }
                                })
                        #insert this new virtualPath to the intended storage
                        self.aCollection.update(
                            {'type':chosenStorage},
                            {'$push':{'metadata':{'virtualPath':newVirtualPath}}}
                        )

                print 'a record has been updated.'
                return True

        #parentFolderPath does not exist, return False
        return False

    def _addNewVirtualPath(self, newVirtualPath, chosenStorage, newRecord=None):
        """
        :param email            :user account used as mongodb collection name
        :param newVirtualPath   :new virtualPath to be saved in mongodb
        :param chosenStorage    :as the name suggest
        :param newRecord        :mongodb record for storing file in googledrive(it needs fileID)
        :return                 :True if operation successful

        call this method to add newVirtualPath to the database
        """
        if newRecord is not None:
            #calling method trying to store file in googledrive
            self.aCollection.update(
                {'type':'googledrive'},
                {'$push':{'metadata':newRecord}}
            )
        else:
            self.aCollection.update(
                {'type':chosenStorage},
                {'$push':{'metadata':{'virtualPath':newVirtualPath}}}
            )

    def _removePath(self, path, storage):
        test= self.aCollection.update(
            #if query is empty, can only update first storage, if path in second position in db, the query will not reach it
            #might wipe all entry in that storage according to the parameter(once during experiment, not sure why)
            {'type':storage},
            {
                '$pull':{
                    'metadata':{
                        'virtualPath':path
                    }
                }
            }
        )

    def _getGoogleDriveFileID(self, virtualPath):
        #storage is pymongo cursor object, put [0] will become record object/ dictionary
        storage= self.aCollection.find(
            {'type':'googledrive'},
            {    '_id':0,
                 'type':1,
                 'metadata':{
                     '$elemMatch':{
                        'virtualPath':virtualPath
                     }
                 }
            }
        )[0]
        #just to make sure, just in case if the fileID is not from googledrive metadata
        if storage['type']=='googledrive':
            #metadata is a list, put [0] to access query result
            return storage['metadata'][0]['fileID']

    #public function
    ###################################################################################################################
    def addAccount(self, email):
        self.setCollection(email)
        #we need placeholder cause mongodb won't create a collection until there is a record added to it
        placeHolder= {
            'placeholder'           :'placeholder'

        }
        docID= self.aCollection.insert(placeHolder)
        print docID
        print 'acc added successfully\n##########################################'
        self.client.disconnect()

    def addStorage(self, storagetype, email):
        self.setCollection(email)
        self.aCollection.remove(
            {
                'placeholder':'placeholder'
            }
        )
        newStorageRecord= {
                    'type'       :storagetype,
                    'metadata'   :[]
        }
        if storagetype=='googledrive':
            #ROSS storage here
            self.credential= self._getCredential(email)
            #all files that is going to gDrive will be stored in same folder, TCSA
            #gDrive handle file naming with id instead of original name, so same files can exist
            #but can uniquely identifiable
            folderMetaData=GoogleDriveWrapper(self.credential).createTCSAFolder()
            #print folderMetaData['id']
            newStorageRecord['rootID']=folderMetaData['id']


        docID= self.aCollection.insert(newStorageRecord)
        #print docID
        print 'storage(%s) added successfully\n##########################################' % (storagetype)
        self.client.disconnect()



    def upload(self, email, virtualPath, fileLocation):
        self.setCollection(email)
        fileSize     = os.stat(fileLocation).st_size
        #print "file size: ",fileSize, " bytes"
        #cos of greedy first .*, the / will reach till just before last part of the path
        filename     = re.match(r".*/(.*)", fileLocation).group(1)





        #ef _uploadGoogleDrive(self, credential, filePath, parentID):
        #wrapper= GoogleDriveWrapper(credential)
        #fileID=wrapper.uploadFile(filePath=filePath, parent_id=parentID)
        #return fileID


        aListofTuple=self._getLargestRemainingStorage(email)
        if fileSize>(aListofTuple[0][1]-self.STORAGE_LIMIT_BUFFER):
            print "upload fail due to file size larger than the largest available cloud storag, aborting upload operation..."
            self.client.disconnect()
            return

        chosenStorage=aListofTuple[0][0]

        #NOTE
        #access token, credentials etc. already taken care by _getLargestRemainingStorage()


        if chosenStorage == 'dropbox':
            wrapper= DropboxWrapper(self.accessToken)
            wrapper.uploadFile(fileLocation, virtualPath)

            #update database
            if virtualPath != '':
                #file not in root folder, may need to remove existing folder record
                if not self._replaceVirtualOldPath(virtualPath+'/'+filename, chosenStorage=chosenStorage):
                    #no existing parentPath record, call below method
                    #note: in practice, this won't happen cause user cant create file in non existing parent folder
                    self._addNewVirtualPath(virtualPath+'/'+filename, chosenStorage)

        elif chosenStorage == 'box':
            raise NotImplementedError

        elif chosenStorage == 'googledrive':
            #get TCSA folder id
            rootID  =list(self.aCollection.find(
                {'type':'googledrive'},
                {'_id':0, 'rootID':1}
            ))[0]['rootID']

            wrapper =GoogleDriveWrapper(self.credential)
            file    =wrapper.uploadFile(filePath=fileLocation, parent_id=rootID)

            #UPDATE DATABASE
            newRecord={
                'virtualPath': virtualPath+'/'+filename,
                'fileID'     : file['id']
            }
            if virtualPath != '':
                #file not in root folder, may need to remove existing folder record
                if not self._replaceVirtualOldPath(virtualPath+'/'+filename, chosenStorage=chosenStorage, newRecord=newRecord):
                    #no existing parentPath record, call below method
                    #note: in practice, this won't happen cause user cant create file in non existing parent folder
                    self._addNewVirtualPath(virtualPath+'/'+filename, chosenStorage, newRecord)

        self.client.disconnect()

    def download(self, email, virtualPath, savePath):
        #find where the file is stored, return pymongo cursor object, convert to list
        self.setCollection(email)
        record= self.aCollection.find(
            {},
            {    '_id':0,
                 'type':1,
                 'metadata':{
                     '$elemMatch':{
                        'virtualPath':virtualPath
                     }
                 }
            }

        )
        for eachStorage in record:
            if 'metadata' in eachStorage:
                print 'found record in %s' % eachStorage['type']
                #call respective storage api
                if eachStorage['type']=='dropbox':
                    #call ross func
                    self.accessToken=self._getAccessToken(email)
                    wrapper=DropboxWrapper(self.accessToken)
                    wrapper.downloadFile(savePath, virtualPath)
                elif eachStorage['type']=='box':
                    raise

                elif eachStorage['type']=='googledrive':
                    fileID=eachStorage['metadata'][0]['fileID']
                    #call ross func to get crendentials
                    self.credential=self._getCredential(email)
                    wrapper=GoogleDriveWrapper(self.credential)
                    wrapper.downloadFile(fileID, savePath)
                break
            else:
                print 'no record found in %s' % eachStorage['type']
        self.client.disconnect()

    def getFolderTree(self,email):
        self.setCollection(email)
        folderTree={'root':{}}

        virtualPathList=self._getAllVirtualPathList()
        #apath -> tuple(virtualPath, storageType)
        for aPath in virtualPathList:
            pointer=folderTree['root']
            #index 0 will be empty string infront '/'
            splittedPath=aPath[0].split('/')[1:]

            if len(splittedPath)!=1:
                #this virtualPath can not be either a file or a folder in root
                for i in xrange(0, len(splittedPath)-1):
                    #for each folder in the splittedPath
                    if splittedPath[i] in pointer.keys():
                            #folder ald exist
                            pointer=pointer[splittedPath[i]]
                    else:
                    #folder/file not exist yet
                            pointer[splittedPath[i]]={}
                            pointer=pointer[splittedPath[i]]

            #left with last part of the path, could be a file or a folder
            #assume folder name cant have dot, eg fol.der
            #.folder still possible
            matchObj=re.match(r'.+(\.).+', splittedPath[-1])
            if matchObj is not None:
                #its a file, add if there is no existing record of it
                if splittedPath[-1] not in pointer.keys():
                    pointer[splittedPath[-1]]='file'
            else:
                #its a folder, add if there is no existing record of it
                if splittedPath[-1] not in pointer.keys():
                    pointer[splittedPath[-1]]={}
        self.client.disconnect()
        return folderTree
        #pprint.pprint(folderTree)


    def delFile(self, email, virtualPath):
        #/animal/monkey.jpg
        #/creature/animal.jpg
        #/animal/horse.jpg
        #/animal1/t.jpg
        #/animal11/t.jpg

        #test case:
        #delete /animal/horse.jpg
        #delete /creature/animal.jpg, must left /creature
        #delete /animal1/t.jpg

        #for test cases
        aList=[
            ('/animal/monkey.jpg','dropbox'),
             #('/creature/animal','dropbox'),
             ('/creature/animal.jpg', 'dropbox'),
              ('/animal/horse.jpg','dropbox'),
               ('/animal1/t.jpg','dropbox'),
                ('/animal11/t.jpg','googledrive'),
                ('/file.pdf', 'googledrive')
        ]
        virtualPathStorage=None
        self.setCollection(email)
        #get all path and their respective storage,including the path to be deleted
        temp=self._getAllVirtualPathList()
        for t in temp:
            if t[0]==virtualPath:
                #found the storage where file is stored
                virtualPathStorage=t[1]
                #remove this path in all path list
                temp.remove((virtualPath, virtualPathStorage))
                print 'virtualpathStorage found...'
                break

        if virtualPathStorage=='dropbox':
            #ros function here
            self.accessToken=self._getAccessToken(email)
            wrapper=DropboxWrapper(self.accessToken)
            wrapper.deleteFile(virtualPath)
        elif virtualPathStorage=='googledrive':
            #ros function here
            self.credential=self._getCredential(email)

            #find file fileID
            #storage is pymongo cursor object, put [0] will become record object/ dictionary
            storage= self.aCollection.find(
                {'type':'googledrive'},
                {    '_id':0,
                     'type':1,
                     'metadata':{
                         '$elemMatch':{
                            'virtualPath':virtualPath
                         }
                     }
                }
            )[0]
            #just to make sure, just in case
            if storage['type']=='googledrive':
                fileID=storage['metadata'][0]['fileID']
                wrapper=GoogleDriveWrapper(self.credential)
                wrapper.deleteFile(fileID)

        #delete virtualPath record in db
        self._removePath(virtualPath, virtualPathStorage)
        print "file deleted from database..."

        #check if there is a need to add parent folder record
        mObj=re.match(r'(^.+/)[^/]+$', virtualPath)
        if mObj is None:
            print 'file in root, no parentPath involved. Returning...'
            self.client.disconnect()
            return
        else:
            #file not in root folder
            print 'checking for parentPath reference in other record...'
            #get parentPath string
            parentPath=mObj.group(1)
            #change aList to temp
            for path in temp:
                #parentPath will have / behind
                #we assume there will be no /aswin if the db have /aswin/setiadi or /aswin/s.jpg ald
                nObj=re.match(r'^%s'%parentPath, path[0])
                if nObj is not None:
                    print 'found other parentPath reference: '+nObj.group()
                    print 'exist other parentPath record, no need to generate parentPath reference. Returning...'
                    self.client.disconnect()
                    return

            print 'parentPath is the only record, adding parentPath reference to db...'
            parentPathRef=parentPath.rstrip('/')
            #parentPathRef is the parent folder path of this file
            self._addNewVirtualPath(parentPathRef, virtualPathStorage)
            print '%s added.' % parentPathRef


    def createFolder(self, email, newVirtualPath):
        self.setCollection(email)
        if not self._replaceVirtualOldPath(newVirtualPath):
            #no existing parentPath record, call below method
            #note: in practice, this won't happen cause user cant create folder in non existing parent folder
            self._addNewVirtualPath(newVirtualPath, self._getAnyStorage())
        self.client.disconnect()

    def deleteFolder(self, email, folderPath):
        #experiment
        #=[1]
        #l=-1*len(t)
        #for i in xrange(l, 0, 1):
        #   print t[i]

        '''
        aList=[
            #delete red folder only in /fruit folder
            ('/fruit/re', 'googledrive'),
            ('/fruit/redd', 'googledrive'),
            #('/fruit/red', 'googledrive'),
            ('/fruit/red/apple.jpg', 'googledrive'),
            ('/fruit/red/lightred/guava.jpg', 'googledrive'),
            ('/fruit/orange/oranges.jpg', 'dropbox'),
            ('/vehicle/red/ferrari.jpg', 'googledrive'),
            ('/red/pomegranate.jpg', 'googledrive'),
            ('/food/fruit/red/100.jpg', 'googledrive'),
            ('/fruit/redd/apple.jpg', 'dropbox'),
            #delete green folder
            ('/vegetable/green/caisim.jpg', 'dropbox'),
            #delete steel folder only in root folder
            ('/utensil/steel/spoon.jpg', 'dropbox'),
            ('/utensil/steel/fork.jpg', 'dropbox'),
            ('/steel/knife.jpg', 'dropbox')
        ]
        '''
        #experiment
        self.setCollection(email)
        parentFolder= re.match(r'(.*)/[^/]+$', folderPath).group(1)
        virtualPathList= self._getAllVirtualPathList()
        if parentFolder=="":
            #folder to be delete is in root, it is save to delete all its records
            l=-1*len(virtualPathList)
            existInDropbox= False
            #count from behind cause we are removing item while iterating
            for i in xrange(l, 0, 1):
                #vPath is a tuple (path, storageType)
                vPath= virtualPathList[i]
                #deleting /thing will remove
                #/thing/food/rice.jpg
                #/thing/mouse.jpg
                #/thing

                mObj= re.match(r'(^%s)($|/.+)' % folderPath, vPath[0])
                if mObj is not None:
                    #this virtualPath contain folder to be deleted

                    #no need del cause we dont reuse virtualPathList
                    #del virtualPathList[i]

                    #remove this record in real storage
                    if vPath[1]=="dropbox":
                        if not existInDropbox:
                            #delete this folder along with subfolder/files recurseively in user's dropbox storage
                            #ros function here
                            self.accessToken=self._getAccessToken(email)
                            wrapper=DropboxWrapper(self.accessToken)
                            wrapper.deleteFile(folderPath)
                            existInDropbox=True

                    elif vPath[1]=='googledrive':
                        #if this virtualPath is a file, delete it in googledrive
                        obj=re.match(r'^.+/[^/]+\.[^/]+', vPath[0])
                        #if its a folder, only remove record in mongodb
                        if obj is not None:
                            #its a file
                            #ros function here
                            self.credential=self._getCredential(email)

                            #find file fileID
                            fileID=self._getGoogleDriveFileID(vPath[0])
                            wrapper=GoogleDriveWrapper(self.credential)
                            wrapper.deleteFile(fileID)


                    #remove record in our database
                    self._removePath(vPath[0], vPath[1])
                    print "[%s] is removed from mongodb" % vPath[0]
        else:
            #folder to be deleted is in another folder, have to make sure there is an existing record of the parent folder in
            #another virtualPath record, else parent folder record will ceast to exist :)

            #in most cases, user only delete folder with small amount of subfolder/files
            #x= number fo virtualPath to be deleted will be small
            #so its better to use this method which go through
            #before delete all records containing this folder, must check if parent folder record exist in other records
            parentExist=False
            existInDropbox=False
            for i in xrange(0, len(virtualPathList)):
                #in reality, no need to include checking for parent folder using $ symbol
                #eg: /food/fruit /food user want delete fruit folder in food
                #in reality /food wont exist cause the program prevent unnecessary record like /food here
                reObj= re.match(r'^%s($|/.+)' % parentFolder, virtualPathList[i][0])
                if reObj is not None:
                    #this item contain parent folder
                    reObj2= re.match(r'(^%s)($|/.+)'%folderPath, virtualPathList[i][0])
                    if reObj2 is not None:
                        #this item contain folder to be deleted
                        if virtualPathList[i][1]=='dropbox':
                            if not existInDropbox:
                                #delete this folder along with subfolder/files recurseively in user's dropbox storage
                                #ros function here
                                self.accessToken=self._getAccessToken(email)
                                wrapper=DropboxWrapper(self.accessToken)
                                wrapper.deleteFile(folderPath)
                                existInDropbox=True

                        elif virtualPathList[i][1]=='googledrive':
                            #need determine if it is a file or folder
                            obj=re.match(r'.+/[^/]+\.[^/]+$', virtualPathList[i][0])
                            #if its a folder, only remove record in mongodb
                            if obj is not None:
                                #its a file
                                #ros function here
                                self.credential=self._getCredential(email)

                                #find file fileID
                                fileID=self._getGoogleDriveFileID(virtualPathList[i][0])
                                wrapper=GoogleDriveWrapper(self.credential)
                                wrapper.deleteFile(fileID)

                        self._removePath(virtualPathList[i][0], virtualPathList[i][1])
                    else:
                        #this item contain parent folder but not folder to be deleted
                        parentExist=True
            if not parentExist:
                #this mean there is no other record keeping parentPath history
                #must add a parentFolder record to the database
                s=self._getAnyStorage()
                self._addNewVirtualPath(parentFolder, s)

        self.client.disconnect()



    def renameFolder(self):
        aList=[
            '/fruit/red/apple.jpg',
            '/fruit/orange/oranges.jpg'
        ]



    def renameFile(self):
        raise NotImplementedError



    def getTempFolderName(self, email):
        self.setCollection(email)
        aRecord=self.aCollection.find(
            {},
            {'_id':1}
        )
        return aRecord[0]['_id']

if __name__ == '__main__':
    #only call these lines when this file is ran
    mongodb = MongoDBWrapper()
    #mongodb.delFile('aswin.setiadi@gmail.com','/animal/monkey.jpg')
    #mongodb.removePath('aswin.setiadi@gmail.com', 'dropbox', '/parent/path')
    #mongodb.getFolderTree('aswin.setiadi@gmail.com')
    #mongodb.getTempFolderName('aswin.setiadi@gmail.com')
    #mongodb.download('aswin.setiadi@gmail.com',
    #                 '/files/animal/monkey.jpg',
    #                 'C:/Users/aswin/Downloads')
    #mongodb._removePath('aswin.setiadi@gmail.com', '/fruits/orange/orange.jpg', 'dropbox')
    #mongodb.deleteFolder('aswin.setiadi@gmail.com', '/fruit/red')
    #mongodb._addPath('test@test.com','box', '/fruits/purple/eggplant.jpg')
    #print mongodb.getTempFolderName('aswin.setiadi@gmail.com')