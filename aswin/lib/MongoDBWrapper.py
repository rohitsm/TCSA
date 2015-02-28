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

    def setCollection(self, collectionName):
        self.aCollection    = self.db[collectionName]

    ###################################################################################################################
    #internal functions assume access token or credentials are handled by the calling function
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

    def _getAllVirtualPathList(self, email):
        aListOfTuple=[]
        storages=self.aCollection.find(
            {},{'_id':0,'metadata.virtualPath':1, 'type':1}
        )
        for storage in storages:
            for path in storage['metadata']:
                aListOfTuple.append((path['virtualPath'], storage['type']))
        return aListOfTuple


    def _replaceVirtualOldPath(self, email, newVirtualPath, chosenStorage=None, newRecord=None):
        #if newRecord arg is provided, it means the calling method wants to store a file in googledrive
        """
        NOTE: new file/folder must not be in root
        replace parent path record with this new record
        e.g. inserting /aswin/setiadi/awesome.pdf will replace /aswin/setiadi
        test cases to consider:
        -create folder with parentPath exist
        -create folder without parentPath exist
        -upload file with parentpath exist and Dropbox
        -upload file with parentpath exist and Googledrive
        -upload file with parentpath not exist and Dropbox
        -upload file with parentpath not exist and Googledrive
        """
        newItem=newVirtualPath.split('/')[-1]
        m=re.match(r'(.*)/%s$' % newItem, newVirtualPath)
        #path will be like /aswin/setiadi
        path=m.group(1)

        aListOfTuple=self._getAllVirtualPathList(email)
        exist=False

        #check if parent path exist
        for virtualPathItem in aListOfTuple:
            if virtualPathItem[0] == path:
                #path exist for folder/file to be created
                ########################################################################
                exist= True


                if newRecord is not None:
                    #storage is googledrive and is a file, must include fileID
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
                    #storing file and not googledrive OR storing folder with storage decided by where parentPath is
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
                break
                ########################################################################

        #parentPath does not exist, add this newVirtualPath to database
        if not exist:
            if chosenStorage is None:
                #this can only mean the calling method intends to store new folderPath record, which can be inserted
                #in any storage, thus chosenStorage arg is not provided
                chosenStorage=self._getLargestRemainingStorage(email)
            if newRecord is None:
                #this can only mean the calling method intends to store new folder record OR
                #dropbox file record with chosenStorage as dropbox
                newRecord={
                    'virtualPath':newVirtualPath
                }
            self.aCollection.update(
                {'type':chosenStorage},
                {'$push':{'metadata':newRecord}}
            )
            #print 'db updated'



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
        if chosenStorage == 'dropbox':
            #ros function here
            self._uploadDropbox(self.accessToken, fileLocation, virtualPath)
            #update database
            if virtualPath != '':
                self._replaceVirtualOldPath(email, virtualPath+'/'+filename, chosenStorage)

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
                self._replaceVirtualOldPath(email, virtualPath+'/'+filename, chosenStorage, newRecord)
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
        storage=record[0]
        print 'found file in %s' % storage['type']
        #call respective storage api
        if storage['type']=='dropbox':
            #call ross func
            self.accessToken=self.DROPBOX[email][2]
            wrapper=DropboxWrapper(self.accessToken)
            wrapper.downloadFile(savePath, virtualPath)

        elif storage['type']=='box':
            raise

        elif storage['type']=='googledrive':
            fileID=storage['metadata'][0]['fileID']
            #call ross func to get crendentials
            self.credential=self.GOOGLE_DRIVE[email]['credentials']
            wrapper=GoogleDriveWrapper(self.credential)
            wrapper.downloadFile(fileID, savePath)

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
            matchObj=re.match(r'.+(\.).+', lastItem)
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
                virtualPathStorage=t[1]
                temp.remove((virtualPath, virtualPathStorage))
                break
                print 'virtualpathStorage found...'
        if virtualPathStorage=='dropbox':
            #ros function here
            self.accessToken=self.DROPBOX[email][2]
            wrapper=DropboxWrapper(self.accessToken)
            wrapper.deleteFile(virtualPath)
        elif virtualPathStorage=='googledrive':
            #ros function here
            self.credential=self.GOOGLE_DRIVE[email]['credentials']
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

    def getTempFolderName(self, email):
        self.setCollection(email)
        txt=self.aCollection.find(
            {},
            {'_id':1}
        )
        return txt[0]['_id']

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


if __name__ == '__main__':
    #only call these lines when this file is ran
    mongodb = MongoDBWrapper()
    #mongodb.delFile('aswin.setiadi@gmail.com','/animal/monkey.jpg')
    #mongodb.removePath('aswin.setiadi@gmail.com', 'dropbox', '/parent/path')
    #mongodb.getFolderTree('aswin.setiadi@gmail.com')
    #mongodb.getTempFolderName('aswin.setiadi@gmail.com')