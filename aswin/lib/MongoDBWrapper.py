import pprint
import re

__author__ = 'aswin'

from pymongo import MongoClient
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper


import os

class MongoDBWrapper:

    """
    This class handle communication between the python program and the mongodb
    database        =database
    collection      =table
    record          =row

    """



    def __init__(self, databaseName, addr, port):
        #TEMPORARY!!!!
        #app key, secret key, authToken
        self.DROPBOX={
                'aswin.setiadi@gmail.com'     :['wnutjjtdxel1kjd', '8o7lycghr5oyqj8', 'QpgYDBNMAjIAAAAAAAAACzAmq7dm0Cy1W3gvFw1uW7-eFWqNTYHSOBG-7juHmRCM'],
                'aswin_setiadi@hotmail.com'   :['n9knxl91ajgtr9c', 'fws52sln0heuauy', '6JdVwA4dAh0AAAAAAAAB-U6VBBZ-Iff9YpMmq2kJgGkc6vXxwFIAtF6x-B6wgphj']
        }

        #TEMPORARY!!!
        self.GOOGLE_DRIVE={
                'aswin.setiadi@gmail.com'     :{
                    'clientID'      : '732832513896-4l3c4s2sddpfm35l752m5p5an6oae2r2.apps.googleusercontent.com',
                    'clientSecret'  : 'AB3lhPz6ldoSC2EWIrUu1qI0',
                    'redirectURI'   : 'https://www.example.com/oauth2callback',
                    "auth_uri"      : "https://accounts.google.com/o/oauth2/auth",
                    "token_uri"     : "https://accounts.google.com/o/oauth2/token",
                    "credentials"   : '{"_module": "oauth2client.client", "token_expiry": "2015-01-27T04:01:40Z", "access_token": "ya29.CAGg0i66u2j4P08HE-iH7KcZvPGwhhhiuWuSwBHEetg8l5drBBBIJGDzMej8kUV5_lWqYQP0477Zow", \
                                      "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.CAGg0i66u2j4P08HE-iH7KcZvPGwhhhiuWuSwBHEetg8l5drBBBIJGDzMej8kUV5_lWqYQP0477Zow", \
                                      "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/xljWdWPUJ0eAGr0CyBt0OXMY5lY2rROOuWIOpliZnlEMEudVrK5jSpoR30zcRFq6"}, \
                                      "client_id": "732832513896-4l3c4s2sddpfm35l752m5p5an6oae2r2.apps.googleusercontent.com", "id_token": null, "client_secret": "AB3lhPz6ldoSC2EWIrUu1qI0", \
                                      "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/xljWdWPUJ0eAGr0CyBt0OXMY5lY2rROOuWIOpliZnlEMEudVrK5jSpoR30zcRFq6", "user_agent": null}'
                }
            }
        self.client         = MongoClient(addr, port)
        self.db             = self.client[databaseName]
        self.aCollection    = None

        self.accessToken    = None
        self.credential     = None


    #upload
    def _uploadDropbox(self, accessToken, filePath, virtualPath):
        #this object initiation automatically get authToken from ros database in DropboxWrapper class
        wrapper= DropboxWrapper(accessToken)
        wrapper.uploadFile(filePath, virtualPath)

    def _uploadBox(self):
        pass

    def _uploadGoogleDrive(self, credential, filePath, parentID):
        wrapper= GoogleDriveWrapper(credential)
        fileID=wrapper.uploadFile(filePath=filePath, parent_id=parentID)
        return fileID


    #get storage size

    def _getDropboxRemainingStorage(self, accessToken):
        return DropboxWrapper(accessToken).getDropboxStorageSizeLeft()

    def _getBoxRemainingStorage(self):
        pass

    def _getGoogleDriveRemainingStorage(self, credentials):
        return GoogleDriveWrapper(credentials).getStorageSizeLeft()


    #set existing collection
    def setCollection(self, collectionName):
        self.aCollection    = self.db[collectionName]

    def printActiveCollection(self):
        print self.aCollection


    #private function

    def _getAllVirtualPathList(self, email):
        self.setCollection(email)
        aList=[]
        storages=self.aCollection.find(
            {},{'_id':0,'metadata.virtualPath':1}
        )
        for storage in storages:
            for path in storage['metadata']:
                aList.append(path['virtualPath'])

        return aList

    def _lastItemCheck(self, lastItem, pointer):
        #left with last item, could be a file or a folder
        matchObj=re.match(r'.+(\.).+', lastItem)
        if matchObj is not None:
            #its a file, add if there are no duplicate files
            if lastItem not in pointer.keys():
                pointer[lastItem]='file'
        else:
            #its a folder, add if there are no duplicate folders
            if lastItem not in pointer.keys():
                pointer[lastItem]={}

    #replace parent path record with this new record
    #e.g. inserting /aswin/setiadi/awesome.pdf will replace /aswin/setiadi
    def _replaceVirtualOldPath(self, email, newVirtualPath, chosenStorage=None, newRecord=None):

        newItem=newVirtualPath.split('/')[-1]
        m=re.match(r'(.*)/%s$' % newItem, newVirtualPath)
        path=m.group(1)

        aList=self._getAllVirtualPathList(email)
        exist=False
        for virtualPathItem in aList:
            if virtualPathItem == path:
                #path exist for folder to be created
                exist= True

                #storage is googledrive, must include fileID
                if newRecord is not None:
                    self.aCollection.update(
                        {
                             'metadata.virtualPath':virtualPathItem
                        },
                        {
                            '$set':{
                                'metadata.$.virtualPath':newRecord['virtualPath'],
                                'metadata.$.fileID'     :newRecord['fileID']
                            }
                        }
                    )
                else:
                    self.aCollection.update(
                        {
                             'metadata.virtualPath':virtualPathItem
                        },
                        {
                            '$set':{
                                'metadata.$.virtualPath':newVirtualPath
                            }
                        }
                    )
                print 'db updated.'
                break
        if not exist:
            if chosenStorage is None:
                chosenStorage=self.getLargestRemainingStorage(email)
            if newRecord is None:
                newRecord={
                    'virtualPath':newVirtualPath
                }
            self.aCollection.update(
                {
                    'type':chosenStorage
                },
                {
                    '$push':{'metadata':newRecord}
                }

            )
            print 'db updated'

    #utility function
    def addAccount(self, collectionName):
        self.setCollection(collectionName)
        placeHolder= {
            'placeholder'           :'placeholder'

        }
        docID= self.aCollection.insert(placeHolder)
        print docID
        print 'acc added successfully\n##########################################'

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
            self.credential= self.GOOGLE_DRIVE[email]['credentials']
            #all files that is going to gDrive will be stored in same folder, TCSA
            #gDrive handle file naming with id instead of original name, so same files can exist
            #but can uniquely identifiable
            folderMetaData=GoogleDriveWrapper(self.credential).createTCSAFolder()
            print folderMetaData['id']
            newStorageRecord['rootID']=folderMetaData['id']

        docID= self.aCollection.insert(newStorageRecord)
        print docID
        print 'storage(%s) added successfully\n##########################################' % (type)



    def upload(self, email, virtualPath, fileLocation):
        self.setCollection(email)
        fileSize= os.stat(fileLocation).st_size
        #print "file size: ",fileSize, " bytes"
        #cos of (group), the / will reach till just before last part of the path
        filename= re.match(r".*/(.*)", fileLocation).group(1)


        chosenStorage=self.getLargestRemainingStorage(email)
        if chosenStorage == 'dropbox':
            #ros function here
            self._uploadDropbox(self.accessToken, fileLocation, virtualPath)
            #update database
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
            self._replaceVirtualOldPath(email, virtualPath+'/'+filename, chosenStorage, newRecord)

    def download(self, email, virtualPath, savePath):
        #find where the file is stored, return pymongo cursor object, convert to list
        self.setCollection(email)
        record= self.aCollection.find(
            {
                'metadata.virtualPath':virtualPath
            },
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

    def getFolderTree(self,email):
        folderTree={'root':{}}

        aList=self._getAllVirtualPathList(email)

        for aPath in aList:
            pointer=folderTree['root']
            splittedPath=aPath.split('/')[1:]

            #item(file/folder) inside root folder
            if len(splittedPath)==1:
                self._lastItemCheck(splittedPath[-1], pointer)
            else:

                for i in range(0, len(splittedPath)-1):
                    #folder ald exist
                    if splittedPath[i] in pointer.keys():
                            pointer=pointer[splittedPath[i]]
                    else:
                    #folder not exist yet
                            pointer[splittedPath[i]]={}
                            pointer=pointer[splittedPath[i]]

                self._lastItemCheck(splittedPath[-1], pointer)
        pprint.pprint(folderTree)

    def delFile(self, email, virtualPath):
        self.setCollection(email)
        item=virtualPath.split('/')[-1]
        m=re.match(r'(.*)/%s' % item, virtualPath)

    def createFolder(self, email, newVirtualPath):
        self.setCollection(email)
        self._replaceVirtualOldPath(email, newVirtualPath)



    #miscelanous
    def getLargestRemainingStorage(self, email):
        self.setCollection(email)
        storageSizePair={}
        #return a list of 1 element(dictionary), chose dict element called 'storage'
        #will return [{u'type': u'dropbox', u'metadata': []},{u'type': u'googledrive', u'metadata': []}], etc
        storageList=self.aCollection.find({},{'_id':0,'type':1})
        for storage in storageList:
            if storage['type'] == 'dropbox':
                #ROS function here
                self.accessToken= self.DROPBOX[email][2]
                storageSizePair['dropbox']=self._getDropboxRemainingStorage(self.accessToken)
            elif storage['type'] == 'box':
                raise NotImplementedError
            elif storage['type'] == 'googledrive':
                #ROS server here
                self.credential= self.GOOGLE_DRIVE[email]['credentials']
                storageSizePair['googledrive']=self._getGoogleDriveRemainingStorage(self.credential)
        #itermitems() will generate a set of tuples eg. ('a', 1000), the key argument dictate
        #the function to compare the second value(1000), hence the function x[1]
        #return (key, value) tuple so put [0] to get the storage
        chosenStorage= max(storageSizePair.iteritems(), key= lambda x: x[1])[0]
        #TODO
        chosenStorage='dropbox'
        print chosenStorage, ' has largest remaining storage.'
        return chosenStorage

    def removePath(self, email, storage, path):
        self.setCollection(email)
        test= self.aCollection.update(
            {
                'type':storage
            },
            {
                '$pull':{
                    'metadata':{
                        'virtualPath':path
                    }
                }
            }
        )
#mongodb = MongoDBWrapper('test', 'localhost', 27017)
#mongodb.removePath('aswin.setiadi@gmail.com', 'googledrive', '/testfile.txt')