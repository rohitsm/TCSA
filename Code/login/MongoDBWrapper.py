from __future__ import division
__author__ = 'aswin'

import pprint
import re
from pymongo import MongoClient
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper
import os
import ConfigParser
import sys


import heapq
#ross library
from models import *
#from aswin.Test import Test
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
    ###################################################################################################################
    def _getAccessToken(self, email):
            return get_dropbox_token(email)
            #return Test().getAuthToken(email)
    def _getCredential(self, email):
            return get_gdrive_token(email)
            #return Test().getCredentials(email)
    ###################################################################################################################
    #get storage size
    def _getDropboxStorage(self, accessToken):
        #tuple (quotaleft, totalquota)
        return DropboxWrapper(accessToken).getDropboxStorageSizeLeft()

    def _getBoxStorage(self):
        pass

    def _getGoogleDriveStorage(self, credentials):
        #tuple (quotaleft, totalquota)
        return GoogleDriveWrapper(credentials).getStorageSizeLeft()

    ###################################################################################################################

    def setCollection(self, email):
        self.aCollection    = self.db[email]

    ###################################################################################################################
    def _getRemainingStorage(self, email):
        aList=[]
        #storageSizePair={}
        #return a list of 1 element(dictionary), chose dict element called 'storage'
        #will return [{u'type': u'dropbox', u'metadata': []},{u'type': u'googledrive', u'metadata': []}], etc
        storageList=self.aCollection.find({},{'_id':0,'type':1})
        #pprint.pprint(list(storageList))
        #pymongo cursor object cant be used more than once
        #if gone through once, next loop will have nothing
        for storage in storageList:
            if not storage:
                continue
            if storage['type'] == 'dropbox':
                #ROS function here
                #email from phyu need to compare in session list
                #inside ross dropbox_conn implemented session checking
                self.accessToken= self._getAccessToken(email)
                #storageSizePair['dropbox']=self._getDropboxRemainingStorage(self.accessToken)
                s=self._getDropboxStorage(self.accessToken)
                aList.append(("dropbox", s[0], s[1]))
            elif storage['type'] == 'box':
                raise NotImplementedError
            elif storage['type'] == 'googledrive':
                #ROS server here
                self.credential= self._getCredential(email)
                #storageSizePair['googledrive']=self._getGoogleDriveRemainingStorage(self.credential)
                ss=self._getGoogleDriveStorage(self.credential)
                aList.append(("googledrive", ss[0], ss[1] ))

        #itermitems() will generate a set of tuples eg. ('a', 1000), the key argument dictate
        #the function to compare the second value(1000), hence the function x[1]
        #return (key, value) tuple so put [0] to get the storage
        #chosenStorage= max(storageSizePair.iteritems(), key= lambda x: x[1])[0]

        #sorted in ascending order
        aList= sorted(aList, key= lambda x: x[1])
        print aList[-1][0], ' has largest remaining storage.'
        #(storage name, storage left, storage size)
        #aList is a list of tuple e.g:('dropbox',123.45)
        print aList
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
            if not storage:
                continue
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
    def _removeListItem(self, dict, storage):
        test= self.aCollection.update(
            #if query is empty, can only update first storage, if path in second position in db, the query will not reach it
            #might wipe all entry in that storage according to the parameter(once during experiment, not sure why)
            {'type':storage},
            {
                '$pull':{
                    'metadata':dict
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



    def upload(self, email, fileName, fileContent):
        #email          =user email
        #virtualpath    =
        #fileLocation   =file content
        try:
            print "__aswin upload__"
            self.setCollection(email)
            fileSize= len(fileContent)
            ##fileSize     = os.stat(fileLocation).st_size
            #print "file size: ",fileSize, " bytes"
            #cos of greedy first .*, the / will reach till just before last part of the path
            #filename     = re.match(r".*/(.*)", fileLocation).group(1)





            #ef _uploadGoogleDrive(self, credential, filePath, parentID):
            #wrapper= GoogleDriveWrapper(credential)
            #fileID=wrapper.uploadFile(filePath=filePath, parent_id=parentID)
            #return fileID

            #(storagename, quotaleft, totalquota)
            aListofTuple=self._getRemainingStorage(email)
            #-1 cause sorted in ascending order
            if fileSize>(aListofTuple[-1][1]-self.STORAGE_LIMIT_BUFFER):
                print "upload fail due to file size larger than the largest available cloud storag, aborting upload operation..."
                self.client.disconnect()
                return
            #
            chosenStorage=aListofTuple[-1][0]
            #NOTE
            #access token, credentials etc. already taken care by _getRemainingStorage()


            if chosenStorage == 'dropbox':
                wrapper= DropboxWrapper(self.accessToken)
                wrapper.uploadFile(fileName, fileContent)

                #update database
                #if virtualPath != '':
                    #file not in root folder, may need to remove existing folder record
                    #if not self._replaceVirtualOldPath(virtualPath+'/'+filename, chosenStorage=chosenStorage):
                        #no existing parentPath record, call below method
                        #note: in practice, this won't happen cause user cant create file in non existing parent folder
                     #   self._addNewVirtualPath(virtualPath+'/'+filename, chosenStorage)
                #else:
                    #file in root folder, add new instance of record
                self._addNewVirtualPath('/'+fileName, chosenStorage)

            elif chosenStorage == 'box':
                raise NotImplementedError

            elif chosenStorage == 'googledrive':
                #get TCSA folder id
                rootID  =list(self.aCollection.find(
                    {'type':'googledrive'},
                    {'_id':0, 'rootID':1}
                ))[0]['rootID']

                #todo
                fileLocation= 'files/'+self.getTempFolderName(email)
                filePath =fileLocation+'/'+fileName
                open(filePath, 'wb').write(fileContent)
                wrapper =GoogleDriveWrapper(self.credential)
                file    =wrapper.uploadFile(filePath=filePath, parent_id=rootID)

                #UPDATE DATABASE
                newRecord={
                    'virtualPath': '/'+fileName,
                    'fileID'     : file['id']
                }

                self._addNewVirtualPath('/'+fileName, chosenStorage, newRecord)

            self.client.disconnect()
            return True
        except Exception as e:
            print e

    def download(self, email, filename):
        #find where the file is stored, return pymongo cursor object, convert to list
        self.setCollection(email)
        print "__aswin download__"
        record= list(self.aCollection.find(
            {},
            {    '_id':0,
                 'type':1,
                 'metadata':{
                     '$elemMatch':{
                        'virtualPath':'/'+filename
                     }
                 }
            }

        ))
        content= False
        print record
        for eachStorage in record:
            if not eachStorage:
                continue
            if 'metadata' in eachStorage:
                print 'found record in %s' % eachStorage['type']
                #call respective storage api
                if eachStorage['type']=='dropbox':
                    #call ross func
                    self.accessToken=self._getAccessToken(email)

                    wrapper=DropboxWrapper(self.accessToken)
                    content= wrapper.downloadFile(filename)
                    print content
                    print "file downloaded"
                elif eachStorage['type']=='box':
                    raise

                elif eachStorage['type']=='googledrive':
                    fileID=eachStorage['metadata'][0]['fileID']
                    #call ross func to get crendentials
                    self.credential=self._getCredential(email)
                    wrapper=GoogleDriveWrapper(self.credential)
                    content= wrapper.downloadFile(fileID)
                break
            else:
                print 'no record found in %s' % eachStorage['type']
        self.client.disconnect()
        return content

    def upload_metadata(self, email, metadata):
        print "__aswin upload_metadata__"
        self.setCollection(email)
        r=list(self.aCollection.find(
        {"foldertree":1},{"_id":0,"value":1}
        ))
        if not r:
            record={"foldertree":1,"value":metadata}
            self.aCollection.insert(record)
        else:
            self.aCollection.update(
                {
                     'foldertree':1
                },
                {
                    '$set':{'value':metadata}
                }
            )


        self.client.disconnect()
        return True

    def download_metadata(self, email):
        print "__aswin download_metadata__"
        self.setCollection(email)
        metadata=list(self.aCollection.find(
            {"foldertree":1},{"_id":0,"value":1}
        ))
        print metadata
        for item in metadata:
            if not item:
                print item['value']
                self.client.disconnect()
                return item['value']
        print "False"
        return False

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


    def delete(self, email, fileName):
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
        print "__aswin delete__"
        f='/'+fileName
        virtualPathStorage=None
        self.setCollection(email)
        #get all path and their respective storage,including the path to be deleted
        temp=self._getAllVirtualPathList()
        for t in temp:
            if t[0]==f:
                #found the storage where file is stored
                virtualPathStorage=t[1]
                #remove this path in all path list
                temp.remove((f, virtualPathStorage))
                print 'virtualpathStorage found...'
                break

        if virtualPathStorage=='dropbox':
            #ros function here
            self.accessToken=self._getAccessToken(email)
            wrapper=DropboxWrapper(self.accessToken)
            wrapper.deleteFile(f)
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
                            'virtualPath':f
                         }
                     }
                }
            )[0]
            #just to make sure, just in case
            #if storage['type']=='googledrive':
            fileID=storage['metadata'][0]['fileID']
            wrapper=GoogleDriveWrapper(self.credential)
            wrapper.deleteFile(fileID)

        #delete virtualPath record in db
        self._removePath(f, virtualPathStorage)
        print "file record deleted in the mongo database..."
        self.client.disconnect()
        return True


        #check if there is a need to add parent folder record
        mObj=None
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
        raise NotImplementedError

    def renameFile(self):
        raise NotImplementedError

    def spreadData(self, email):
        self.setCollection(email)
        #storages will be a list of tuple(storagename, quotaleft,totalquota)
        exceedRatioStorageList=[]
        belowRatioStorageList=[]
        storages=self._getRemainingStorage(email)
        print storages
        totalStorages   = sum([t[2] for t in storages])
        totalUsage      = sum([t[2]-t[1] for t in storages])
        ratio           = totalUsage/totalStorages
        print ratio
        for storage in storages:
            usage=storage[2]-storage[1]
            usageRatio=ratio*storage[2]
            if usage>usageRatio:
                print "%s exceed ratio" % storage[0]
                exceedRatioStorageList.append((storage[0], usage, usageRatio))
            else:
                print "%s below ratio" % storage[0]
                belowRatioStorageList.append((storage[0], storage[1]))

        for fullStorage in exceedRatioStorageList:
            #bytes toBeRemoved
            toBeRemoved= fullStorage[1]-fullStorage[2]
            #get file list and respective size in fullStorage
            accessToken= self._getAccessToken(email)
            wrapper=DropboxWrapper(accessToken=accessToken)
            files, cursor= wrapper.getMetadata()

            print 'Top 10 biggest files:'

            for path, metadata in heapq.nlargest(10, files.items(), key=lambda x: x[1]['bytes']):
                print 't%s: %d bytes' % (path, metadata['bytes'])

            break

    def getTempFolderName(self, email):
        self.setCollection(email)
        aRecord=self.aCollection.find(
            {},
            {'_id':1}
        )
        return str(aRecord[0]['_id'])

if __name__ == '__main__':
    #only call these lines when this file is ran
    mongodb = MongoDBWrapper()
    #mongodb.spreadData('aswin.setiadi@gmail.com')
    #mongodb.delFile('aswin.setiadi@gmail.com','/animal/monkey.jpg')
    #mongodb.removePath('aswin.setiadi@gmail.com', 'dropbox', '/parent/path')
    #mongodb.getFolderTree('aswin.setiadi@gmail.com')
    #mongodb.getTempFolderName('aswin.setiadi@gmail.com')
    #mongodb.download('aswin.setiadi@gmail.com', 't.txt')
    #mongodb._removePath('aswin.setiadi@gmail.com', '/fruits/orange/orange.jpg', 'dropbox')
    #mongodb.deleteFolder('aswin.setiadi@gmail.com', '/fruit/red')
    #mongodb._addPath('test@test.com','box', '/fruits/purple/eggplant.jpg')
    #print mongodb.getTempFolderName('aswin.setiadi@gmail.com')
    #print mongodb._getRemainingStorage('aswin.setiadi@gmail.com')
    #mongodb.upload('aswin.setiadi@gmail.com', 'abc', 'kasdfhajsdhf23234242')
    #mongodb.deleteFolder('aswin.setiadi@gmail.com', '/abc')
    #mongodb.upload_metadata('aswin.setiadi@gmail.com', 'aswinsetiadi')
    #mongodb.setCollection('aswin.setiadi@gmail.com')
    #mongodb._removeListItem({'foldertree':'aswinsetiadi'}, 'googledrive')
    #mongodb.upload_metadata('aswin.setiadi@gmail.com', 'hello')
    #mongodb.upload_metadata('aswin.setiadi@gmail.com', "aswin")
    #mongodb.download_metadata('aswin.setiadi@gmail.com')
    #mongodb.addStorage()
    #mongodb.upload('aswin.setiadi@gmail.com', "t.txt", "hello world")
    #mongodb.delete('aswin.setiadi@gmail.com', 't.txt')
    #mongodb.download('aswin.setiadi@gmail.com', '/Getting Started.pdf')
    #mongodb.upload_metadata('aswin.setiadi@gmail.com', 'encrypted folder tree here')