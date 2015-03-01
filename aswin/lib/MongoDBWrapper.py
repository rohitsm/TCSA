__author__ = 'aswin'
import pprint
import re
from pymongo import MongoClient
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper
from Test import Test

import os
import ConfigParser


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
        allOptions=config.options(section)
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


    #upload
    def _uploadDropbox(self, accessToken, filePath, virtualPath):
        wrapper= DropboxWrapper(accessToken)
        wrapper.uploadFile(filePath, virtualPath)

    def _uploadBox(self):
        raise NotImplementedError

    def _uploadGoogleDrive(self, credential, filePath, parentID):
        wrapper= GoogleDriveWrapper(credential)
        fileID=wrapper.uploadFile(filePath=filePath, parent_id=parentID)
        return fileID
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
        storageSizePair={}
        #return a list of 1 element(dictionary), chose dict element called 'storage'
        #will return [{u'type': u'dropbox', u'metadata': []},{u'type': u'googledrive', u'metadata': []}], etc
        storageList=self.aCollection.find({},{'_id':0,'type':1})
        for storage in storageList:
            if storage['type'] == 'dropbox':
                #ROS function here
                #email from phyu need to compare in session list
                self.accessToken= Test().getAuthToken(email)
                storageSizePair['dropbox']=self._getDropboxRemainingStorage(self.accessToken)
            elif storage['type'] == 'box':
                raise NotImplementedError
            elif storage['type'] == 'googledrive':
                #ROS server here
                self.credential= Test().getCredentials(email)
                storageSizePair['googledrive']=self._getGoogleDriveRemainingStorage(self.credential)
        #itermitems() will generate a set of tuples eg. ('a', 1000), the key argument dictate
        #the function to compare the second value(1000), hence the function x[1]
        #return (key, value) tuple so put [0] to get the storage
        chosenStorage= max(storageSizePair.iteritems(), key= lambda x: x[1])[0]
        print chosenStorage, ' has largest remaining storage.'
        #choseStorage is a string of either:
        #dropbox,box, googledrive
        return chosenStorage

    def _getAnyStorage(self):

        #can be dropbox,box, googledrive
        return aStorage
    def _getAllVirtualPathList(self, email):
        aListOfTuple=[]
        storages=self.aCollection.find(
            {},{'_id':0,'metadata.virtualPath':1, 'type':1}
        )
        for storage in storages:
            for path in storage['metadata']:
                aListOfTuple.append((path['virtualPath'], storage['type']))
        return aListOfTuple


    def _replaceVirtualOldPath(self, email, newVirtualPath, newRecord=None):
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

        aListOfTuple=self._getAllVirtualPathList(email)

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
                            #if this empty, can only update first storagerecord type and will wipe
                            {'type':virtualPathItem[1]},
                            {
                                '$pull':{
                                    'metadata':{
                                        'virtualPath':virtualPathItem[0]
                                    }
                                }
                            }
                        )
                        #insert this new virtualPath to googledrive storage
                        self.aCollection.update(
                            {'type':'googledrive'},
                            {'$push':{'metadata':newRecord}}
                        )
                else:
                    #storing file not in googledrive OR storing folder with storage decided by where parentPath is
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
                #print 'a record has been updated.'
                return True

        #parentFolderPath does not exist, return False
        return False

    def _addNewVirtualPath(self, email, newVirtualPath, chosenStorage, newRecord=None):
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
            self.credential= Test.getCredentials(email)
            #all files that is going to gDrive will be stored in same folder, TCSA
            #gDrive handle file naming with id instead of original name, so same files can exist
            #but can uniquely identifiable
            folderMetaData=GoogleDriveWrapper(self.credential).createTCSAFolder()
            #print folderMetaData['id']
            newStorageRecord['rootID']=folderMetaData['id']


        docID= self.aCollection.insert(newStorageRecord)
        print docID
        print 'storage(%s) added successfully\n##########################################' % (type)
        self.client.disconnect()



    def upload(self, email, virtualPath, fileLocation):
        self.setCollection(email)
        fileSize     = os.stat(fileLocation).st_size
        #print "file size: ",fileSize, " bytes"
        #cos of greedy first .*, the / will reach till just before last part of the path
        filename     = re.match(r".*/(.*)", fileLocation).group(1)

        chosenStorage=self._getLargestRemainingStorage(email)
        #todo
        #chosenStorage='dropbox'
        #access token, credentials etc. already taken care by _getLargestRemainingStorage()
        if chosenStorage == 'dropbox':
            self._uploadDropbox(self.accessToken, fileLocation, virtualPath)
            #update database
            if virtualPath != '':
                #file not in root folder, may need to remove existing folder record
                if not self._replaceVirtualOldPath(email, virtualPath+'/'+filename, chosenStorage):
                    #no existing parentPath record, call below method
                    #note: in practice, this won't happen cause user cant create file in non existing parent folder
                    self._addNewVirtualPath(email, virtualPath, chosenStorage)

        elif chosenStorage == 'box':
            raise NotImplementedError

        elif chosenStorage == 'googledrive':
            #get TCSA folder id
            rootID  =list(self.aCollection.find(
                {'type':'googledrive'},
                {'_id':0, 'rootID':1}
            ))[0]['rootID']
            file=self._uploadGoogleDrive(self.credential, fileLocation, rootID)

            #UPDATE DATABASE
            newRecord={
                'virtualPath': virtualPath+'/'+filename,
                'fileID'     : file['id']
            }
            if virtualPath != '':
                #file not in root folder, may need to remove existing folder record
                if not self._replaceVirtualOldPath(email, virtualPath+'/'+filename, chosenStorage, newRecord):
                    #no existing parentPath record, call below method
                    #note: in practice, this won't happen cause user cant create file in non existing parent folder
                    self._addNewVirtualPath(email, virtualPath, chosenStorage)

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
                    self.accessToken=Test().getAuthToken(email)
                    wrapper=DropboxWrapper(self.accessToken)
                    wrapper.downloadFile(savePath, virtualPath)
                elif eachStorage['type']=='box':
                    raise

                elif eachStorage['type']=='googledrive':
                    fileID=eachStorage['metadata'][0]['fileID']
                    #call ross func to get crendentials
                    self.credential=Test().getCredentials(email)
                    wrapper=GoogleDriveWrapper(self.credential)
                    wrapper.downloadFile(fileID, savePath)
                break
            else:
                print 'no record found in %s' % eachStorage['type']
        self.client.disconnect()

    def getFolderTree(self,email):
        self.setCollection(email)
        folderTree={'root':{}}

        virtualPathList=self._getAllVirtualPathList(email)
        #apath -> tuple(virtualPath, storageType)
        for aPath in virtualPathList:
            pointer=folderTree['root']
            #index 0 will be empty string infront '/'
            splittedPath=aPath[0].split('/')[1:]

            if len(splittedPath)!=1:
                #this virtualPath can not be either a file or a folder in root
                for i in range(0, len(splittedPath)-1):
                    #for each folder in the splittedPath
                    if splittedPath[i] in pointer.keys():
                            #folder ald exist
                            pointer=pointer[splittedPath[i]]
                    else:
                    #folder/file not exist yet
                            pointer[splittedPath[i]]={}
                            pointer=pointer[splittedPath[i]]

            #left with last part of the path, could be a file or a folder
            matchObj=re.match(r'.+(\.).+', splittedPath[-1])
            if matchObj is not None:
                #its a file, add if there is no existing record of it
                if splittedPath[-1] not in pointer.keys():
                    pointer[splittedPath[-1]]='file'
            else:
                #its a folder, add if there is no existing record of it
                if splittedPath[-1] not in pointer.keys():
                    pointer[splittedPath[-1]]={}

        return folderTree
        #pprint.pprint(folderTree)
        self.client.disconnect()

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
        temp=self._getAllVirtualPathList(email)
        for t in temp:
            if t[0]==virtualPath:
                #found the storage where file is stored
                virtualPathStorage=t[1]
                #remove this path in all path list
                temp.remove((virtualPath, virtualPathStorage))
                break
                print 'virtualpathStorage found...'
        if virtualPathStorage=='dropbox':
            #ros function here
            self.accessToken=Test.getAuthToken(email)
            wrapper=DropboxWrapper(self.accessToken)
            wrapper.deleteFile(virtualPath)
        elif virtualPathStorage=='googledrive':
            #ros function here
            self.credential=Test.getCredentials(email)
            storage= self.aCollection.find(
                {},
                {    '_id':0,
                     'type':1,
                     'metadata':{
                         '$elemMatch':{
                            'virtualPath':virtualPath
                         }
                     }
                }

            )[0]
            if storage['type']=='googledrive':
                fileID=storage['metadata'][0]['fileID']
                wrapper=GoogleDriveWrapper(self.credential)
                wrapper.deleteFile(fileID)
            else:
                assert 'error fileID not found'

        #delete virtualPath record in db
        self.aCollection.update(
                    {'type':virtualPathStorage},
                    {'$pull':
                         {'metadata':
                              {'virtualPath':virtualPath}
                         }
                    }
                )
        print "file deleted from database..."
        #if file in root eg. /a.pdf, it will return none
        mObj=re.match(r'(^.+/)[^/]+$', virtualPath)
        if mObj is None:
            print 'file in root, no parentPath involved. Returning...'
        else:
            #file not in root folder
            print 'checking for parentPath reference in other record...'
            #get parentPath string
            parentPath=mObj.group(1)
            #change aList to temp
            for path in temp:
                nObj=re.match(r'^%s'%parentPath, path[0])
                if nObj is not None:
                    print 'found other parentPath reference: '+nObj.group()
                    print 'exist other parentPath record, no need to generate parentPath reference. Returning...'
                    self.client.disconnect()
                    return

            print 'parentPath is the only record, adding parentPath reference to db...'
            parentPathRef=parentPath.rstrip('/')

            newRecord={'virtualPath':parentPathRef}
            self.aCollection.update(
                {'type':virtualPathStorage},
                {'$push':{'metadata':newRecord}}
            )
            print '%s added.' % parentPathRef
        self.client.disconnect()


    def createFolder(self, email, newVirtualPath):
        self.setCollection(email)
        self._replaceVirtualOldPath(email, newVirtualPath)
        self.client.disconnect()

    def deleteFolder(self):
        raise NotImplementedError

    def renameFolder(self):
        raise NotImplementedError



    #experiment function
    ###################################################################################################################
    def _removePath(self, email, storage, path):
        self.setCollection(email)

        test= self.aCollection.update(
            #if this empty, can only update first storagerecord type and will wipe
            #all entry in that storage according to the parameter
            {'type':storage},
            {
                '$pull':{
                    'metadata':{
                        'virtualPath':path
                    }
                }
            }
        )
        '''
        newRecord={'virtualPath':'/parent/path'}
        self.aCollection.update(
            {'type':storage},
            {'$push':{'metadata':newRecord}}
        )
        '''
    def getTempFolderName(self, email):
        self.setCollection(email)
        txt=self.aCollection.find(
            {},
            {'_id':1}
        )
        return txt[0]['_id']

if __name__ == '__main__':
    #only call these lines when this file is ran
    mongodb = MongoDBWrapper()
    #mongodb.delFile('aswin.setiadi@gmail.com','/animal/monkey.jpg')
    #mongodb.removePath('aswin.setiadi@gmail.com', 'dropbox', '/parent/path')
    #mongodb.getFolderTree('aswin.setiadi@gmail.com')
    #mongodb.getTempFolderName('aswin.setiadi@gmail.com')
    #mongodb.download('aswin.setiadi@gmail.com',
    #                 '/images/monkey.jpg',
    #                 'C:/Users/aswin/Downloads')
    #mongodb._removePath('aswin.setiadi@gmail.com', 'googledrive', '/furniture/chair/chair/table.jpg')