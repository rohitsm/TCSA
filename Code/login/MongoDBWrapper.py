from __future__ import division
__author__ = 'aswin'

import pprint
import re
from pymongo import MongoClient
#from pymongo.collection import Collection
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper
from BoxWrapper import BoxWrapper
import sys,os
import traceback
import ConfigParser
#import shutil
#import heapq
from operator import itemgetter
import zfec

#ross library
#from gdrive_conn import get_gdrive_credentials
#from models import *
from aswin.Test import Test
class MongoDBWrapper:
    """
    This class handle communication between the python program and the mongodb
    database        =database
    collection      =table
    record          =row

    """



    def __init__(self):
        config      = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),'mongodbconfig.ini'))
        section     =config.sections()[0]
        allOptions  =config.options(section)
        databaseName=config.get(section, allOptions[0])
        addr        =config.get(section, allOptions[1])
        port        =config.getint(section, allOptions[2])


        self.DROPBOX    ='dropbox'
        self.BOX        ='box'
        self.GOOGLEDRIVE='googledrive'
        #upper threshold of storage
        self.STORAGE_LIMIT_BUFFER=1024.0
        self.client         = MongoClient(addr, port)
        self.db             = self.client[databaseName]

        #each collection represent a user
        self.aCollection    = None
        #for dropbox
        self.accessToken    = None
        #for googledrive
        self.credential     = None
        #for box
        self.tupleForBox    = None


    ###################################################################################################################
    def _getAccessToken(self, email):
        #return get_dropbox_token(email)
        return Test().getAuthToken(email)
    def _getCredential(self, email):
        #return get_gdrive_credentials(email)
        return Test().getCredentials(email)

    def _getBoxIDToken(self, email):
        #ros function here to be made

        aTuple=Test().getBoxIDToken(email)
        self.setCollection(email)
        aRecord=list(self.aCollection.find(
            {'type':'box'},
            {"_id":0,
             "accessToken":1,
             "refreshToken":1
            }
        ))[0]

        return (
            aTuple[0],
            aTuple[1],
            #use from Test instead
            #aTuple[2],
            #aTuple[3]
            aRecord['accessToken'],
            aRecord['refreshToken']
        )

    ###################################################################################################################
    #get storage size
    def _getDropboxStorage(self, accessToken):
        #tuple (quotaleft, totalquota)
        return DropboxWrapper(accessToken).getDropboxStorageSizeLeft()

    def _getBoxStorage(self, tupleForBox):
        wrapper= BoxWrapper(tupleForBox)
        aTuple = wrapper.getBoxStorageSizeLeft()
        accessT, refreshT= wrapper.refreshToken()
        self._saveNewBoxTokenToMongoDB(accessT, refreshT)
        return aTuple

    def _getGoogleDriveStorage(self, credentials):
        #tuple (quotaleft, totalquota)
        return GoogleDriveWrapper(credentials).getStorageSizeLeft()

    ###################################################################################################################

    def setCollection(self, email):
        try:
            self.aCollection    = self.db[email]
            return True
        except TypeError as e:
            traceback.format_exc()
            return False
    ###################################################################################################################
    def _getRemainingStorage(self, email):


        aList=[]
        storageList=self.aCollection.find({},{'_id':0,'type':1})
        #return a list of 1 element(dictionary), chose dict element called 'storage'
        #will return [{u'type': u'dropbox'},{u'type': u'googledrive'},{}]
        #pymongo cursor object cant be iterated more than once

        for storage in storageList:
            if not storage:
                #means this record is the foldertree, not storage record with field type
                continue
            if storage['type'] == 'dropbox':
                try:
                    self.accessToken= self._getAccessToken(email)
                    s=self._getDropboxStorage(self.accessToken)
                    aList.append(("dropbox", s[0], s[1]))
                except Exception as e:
                    print traceback.format_exc()
                    return False
            elif storage['type'] == 'box':
                try:
                    self.tupleForBox= self._getBoxIDToken(email)
                    aTuple=self._getBoxStorage(self.tupleForBox)
                    aList.append(('box', aTuple[0], aTuple[1]))
                except Exception:
                    print traceback.format_exc()
                    return False
            elif storage['type'] == 'googledrive':
                try:
                    self.credential= self._getCredential(email)
                    ss=self._getGoogleDriveStorage(self.credential)
                    aList.append(("googledrive", ss[0], ss[1] ))
                except Exception as e:
                    print traceback.format_exc()
                    return False

        #sorted in ascending order
        aList= sorted(aList, key= lambda x: x[1])
        print aList[-1][0], ' has largest remaining storage.'
        #element of aList is a tuple=(storage name, storage left, total storage)
        #aList is a list of tuple e.g:('dropbox',123.45, 300)
        return aList
    def _addNewVirtualPath(self, chosenStorage, newRecord):
        """
        :param newVirtualPath   :new virtualPath to be saved in mongodb
        :param chosenStorage    :as the name suggest
        :param newRecord        :mongodb record for storing file in googledrive(it needs fileID)

        call this method to add newVirtualPath to the database

        note: need to update the function design in the future cause the newVirtualPath is redundant when newRecord is
              not none
        """
        try:
            self.aCollection.update(
                {'type':chosenStorage},
                {'$push':{'metadata':newRecord}}
            )
            print "%s added" % newRecord
            return True
        except Exception as e:
            print "_addNewVirtualPath:mongodb update operation fail"
            print traceback.format_exc()
            return False
            '''
            pprint.pprint(list(self.aCollection.find(
                {'type':chosenStorage},
                {    '_id':0,
                     'type':1,
                     'metadata':{
                         '$elemMatch':{
                            'virtualPath':newVirtualPath
                         }
                     }
                }
            )))
            '''
    def _removeVirtualPath(self, virtualPath, storage):
        #will also remove duplicate virtualpath, but limited to same storage
        test= self.aCollection.update(
            #if query is empty, can only update first storage, if path in second position in db, the query will not reach it
            #might wipe all entry in that storage according to the parameter(once during experiment, not sure why)
            {'type':storage},
            {
                '$pull':{
                    'metadata':{
                        'virtualPath':virtualPath
                    }
                }
            }
        )
    def _getGoogleDriveFileID(self, virtualPath):
        #storage is pymongo cursor object, put [0] will become record object/ dictionary object
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
    def _saveNewBoxTokenToMongoDB(self, access_token, refresh_token):
        print "new access token:%s\n new refresh token%s" % (access_token, refresh_token)
        self.aCollection.update(
            {"type":self.BOX},
            {'$set':{'accessToken':access_token, 'refreshToken':refresh_token}}

        )
        print "box access and refresh token updated..."
    #public function
    ###################################################################################################################
    def addAccount(self, email):
        #create account collection in mongodb
        if not self.setCollection(email):
            print "Fail initiating user collection with this email. Returning"
            return False
        #we need placeholder cause mongodb won't create a collection until there is a record added to it
        #but now with the folder tree metadata kept in mongodb, we used it to replace placeholder
        foldertree= {
            'value'             :"",
            'foldertree'        :1

        }
        try:
            docID= self.aCollection.insert(foldertree)
            print 'acc added successfully\n##########################################'
            self.client.disconnect()
            return True

        except Exception as e:
            print traceback.format_exc()
            return False

    def addStorage(self, storagetype, email):
        #create storage record under an account collection
        #for adding ##BOX## storage, access_token can still be used within 1 hour, refresh token got 1x chance to be used
        if not self.setCollection(email):
            print "Fail initiating user collection with this email. Returning"
            return False
        check=list(self.aCollection.find({'type':storagetype}))
        if check:
            #db already contains such storage type
            print "fail to add storage: %s. it has already existed. returning false" % storagetype
            return False
        newStorageRecord= {
                    'type'       :storagetype,
                    'metadata'   :[]
        }
        try:
            if storagetype=='googledrive':
                #all files that is going to gDrive will be stored in same folder, TCSA
                #gDrive handle file naming with id instead of original name, so same files can exist
                #but can uniquely identifiable
                self.credential= self._getCredential(email)
                if not self.credential:
                    #self.credential =None
                    print "fail to get credential from Ross function returning"
                    return False
                folderMetaData      =GoogleDriveWrapper(self.credential).createTCSAFolder()
                if not folderMetaData:
                    #if above returned False means fail create TCSA folder through googledrive API call
                    return False
                newStorageRecord['TCSAFolderID']=folderMetaData['id']

            elif storagetype==self.BOX:

                self.tupleForBox= self._getBoxIDToken(email)
                if not self.tupleForBox:
                    #self.tupleForBox returning None
                    print "fail to get 4 box parameteres from Ross function. Returning False"
                    return False
                folderID           =BoxWrapper(self.tupleForBox).createFolder("TCSA")
                if not folderID:
                    #error occur and it return False
                    return False
                print folderID
                print type(folderID)
                newStorageRecord['TCSAFolderID']= folderID
                newStorageRecord['accessToken'] = self.tupleForBox[2]
                newStorageRecord['refreshToken']= self.tupleForBox[3]



            docID= self.aCollection.insert(newStorageRecord)
            #print docID
            print 'storage(%s) added successfully\n##########################################' % (storagetype)
            self.client.disconnect()
            return True

        except Exception as e:
            print traceback.format_exc()
            return False

    def deleteStorage(self, storagetype, email):
        try:
            self.setCollection(email)
            aRecord=list(self.aCollection.find(
                {'type':storagetype},
                {'metadata':1}
            ))[0]
            paths=[]
            for key in aRecord:
                if key=='metadata':
                    for path in aRecord[key]:
                        #get all virtual path under this storage, compile them into a list and then
                        #send them to Phyu so she can know which files are deleted
                        paths.append(path['virtualPath'].split('/')[-1])
            #aggregate the list items into a string, each path seperated by comma
            returnString=','.join(paths)
            self.aCollection.remove({'type':storagetype})
            "%s deleted from mongodb" % storagetype
            return returnString
        except Exception as e:
            print traceback.format_exc()
            return False

    def upload(self, email, fileName, fileContent):
        #email          =user email
        #fileName       =file name
        #fileLocation   =file content as string
        try:
            print "__aswin upload__"
            self.setCollection(email)
            filePath='/TCSA/%s' % fileName
            entryExist=list(self.aCollection.find(
                {'metadata.virtualPath':filePath},
                {}
            ))
            if entryExist:
                print "file already exist in database. Returning False..."
                self.client.close()
                return False
            else:
                print "file not exist in database. Starting to add record..."

            fileSize= len(fileContent)

            #[storagename, quotaleft, totalquota]

            aListofList=self._getRemainingStorage(email)
            #note: box accessToken is refreshed, must reinitiate self.tupleForBox
            if not aListofList:
                print"fail to upload. user has not registered any storage to TCSA. returning False"
                self.client.disconnect()
                return False
            #-1 will get storage with largest remaining quota cause sorted in ascending order
            if fileSize>(aListofList[-1][1]-self.STORAGE_LIMIT_BUFFER):
                print "upload fail due to file size larger than the largest available cloud storag, aborting upload operation..."
                self.client.disconnect()
                return False

            chosenStorage=aListofList[-1][0]
            #uncomment to manually chose storage
            #chosenStorage='dropbox'
            #NOTE
            #access token, credentials etc. already taken care by _getRemainingStorage()


            if chosenStorage == 'dropbox':
                #self.accessToken initiated from self._getRemainingStorage(email)
                wrapper= DropboxWrapper(self.accessToken)
                if not wrapper.uploadFile(dropboxFilePath=filePath, fileContent=fileContent):
                    #fail to upload, abort operation
                    print "Fail to upload file to dropbox due to API error, returning False"
                    self.client.disconnect()
                    return False
                newRecord={
                    'virtualPath': filePath
                }
                if not self._addNewVirtualPath('dropbox', newRecord):
                    self.client.disconnect()
                    return False

            elif chosenStorage == 'box':
                TCSAFolderID    =list(self.aCollection.find(
                    {'type':'box'},
                    {'_id':0, 'TCSAFolderID':1}
                ))[0]['TCSAFolderID']
                self.tupleForBox=self._getBoxIDToken(email)
                boxwrapper          =BoxWrapper(self.tupleForBox)
                fileID        =boxwrapper.uploadFileContent(filename=fileName,
                                                                  filecontent=fileContent,
                                                                  TCSAFolderID=TCSAFolderID)
                accessT, refreshT   = boxwrapper.refreshToken()
                self._saveNewBoxTokenToMongoDB(accessT, refreshT)
                newRecord={
                    'virtualPath': filePath,
                    'fileID'     : fileID
                }

                if not self._addNewVirtualPath(self.BOX, newRecord):
                    self.client.disconnect()
                    return False



            elif chosenStorage == 'googledrive':
                #get TCSA folder id
                #[0] means first item in pymongo cursor object, then get the value from key TCSAFolderID
                TCSAFolderID  =list(self.aCollection.find(
                    {'type':'googledrive'},
                    {'_id':0, 'TCSAFolderID':1}
                ))[0]['TCSAFolderID']

                #fileLocation= '/home/rohit008/TCSA/Code/login/files/'+self.getTempFolderName(email)
                #if not os.path.exists(fileLocation):
                #    os.makedirs(fileLocation)
                #filePath =fileLocation+'/'+fileName+'.txt'
                #open(filePath, 'wb').write(fileContent)
                #self.credential initiated from self._getRemainingStorage(email)
                wrapper =GoogleDriveWrapper(self.credential)
                file    =wrapper.uploadFileContent(filename=fileName, filecontent=fileContent, parent_id=TCSAFolderID)

                #UPDATE DATABASE FOR GOOGLEDRIVE SCENARIO
                newRecord={
                    'virtualPath': filePath,
                    'fileID'     : file['id']
                }

                if not self._addNewVirtualPath('googledrive', newRecord):
                    self.client.disconnect()
                    return False

            self.client.disconnect()
            #shutil.rmtree(fileLocation)
            #os.removedirs(fileLocation)
            return True
        except Exception as e:
            print traceback.format_exc()
            self.client.disconnect()
            return False

    def download(self, email, filename):
        try:
            self.setCollection(email)
            print "__aswin download__"
            #find where the file is stored, return pymongo cursor object, convert to list
            filePath='/TCSA/%s'%filename
            record= list(self.aCollection.find(
                {},
                {    '_id':0,
                     'type':1,
                     'metadata':{
                         '$elemMatch':{
                            'virtualPath':filePath
                         }
                     }
                }

            ))

            self.client.disconnect()
            #pprint.pprint(record)
            content= False
            for eachStorage in record:

                if not eachStorage:
                    #eachStorage is empty record --> {}
                    #this record is foldertree record
                    continue
                #if 'metadata' is in eachStorage key list
                if 'metadata' in eachStorage:
                    #this record is the storage record that has the sought after file

                    #call respective storage api
                    #0 means index number of metadata list element
                    if eachStorage['type']=='dropbox' and 'erasureFile' not in eachStorage['metadata'][0]:
                        print 'found record in %s' % eachStorage['type']
                        #call ross func
                        self.accessToken=self._getAccessToken(email)

                        wrapper=DropboxWrapper(self.accessToken)
                        content= wrapper.downloadFile(filePath)

                    elif eachStorage['type']=='box' and 'erasureFile' not in eachStorage['metadata'][0]:
                        print 'found record in %s with boxFileID %s' % (eachStorage['type'], eachStorage['metadata'][0]['fileID'])
                        fileID=eachStorage['metadata'][0]['fileID']
                        #call ross func
                        self.tupleForBox=self._getBoxIDToken(email)
                        boxwrapper= BoxWrapper(self.tupleForBox)
                        content= boxwrapper.downloadFile(fileID)
                        accessT, refreshT   = boxwrapper.refreshToken()
                        self._saveNewBoxTokenToMongoDB(accessT, refreshT)

                        content=content.getvalue()
                        print content

                    elif eachStorage['type']=='googledrive' and 'erasureFile' not in eachStorage['metadata'][0]:
                        print 'found record in %s' % eachStorage['type']
                        fileID=eachStorage['metadata'][0]['fileID']
                        #call ross func to get crendentials
                        self.credential=self._getCredential(email)
                        wrapper=GoogleDriveWrapper(self.credential)
                        content= wrapper.downloadFile(fileID)

                    if content:
                        print "download successfull:\n%s\n" % content
                        return content

            print 'no record found in all storage\n returning False'
            return content
        except Exception as e:
            print traceback.format_exc()
            return False

    def upload_metadata(self, email, metadata):
        print "__aswin upload_metadata__"
        try:
            self.setCollection(email)
            r=list(self.aCollection.find(
            {"foldertree":1},{"_id":0,"value":1}
            ))
            if not r:
                #record has not exist, insert new one
                #with new addAccount, this scenario shouldn't be happening
                record={"foldertree":1,"value":metadata}
                self.aCollection.insert(record)
            else:
                #record exist, update it
                self.aCollection.update(
                    {
                         'foldertree':1
                    },
                    {
                        '$set':{'value':metadata}
                    }
                )


            self.client.disconnect()
            print "metadata: %s\nhas been uploaded" % metadata
            return True
        except Exception as e:
            print "error, upload_metadata has failed."
            print traceback.format_exc()
            self.client.disconnect()
            return False

    def download_metadata(self, email):
        print "__aswin download_metadata__"
        try:
            self.setCollection(email)
            metadata=list(self.aCollection.find(
                {"foldertree":1},{"_id":0,"value":1}
            ))
            self.client.disconnect()
            #print metadata
            for item in metadata:
                if item:
                    #example of item is a record {"value":"assdfksl12"}
                    #list metadata contains element>0
                    #query return at least 1 record result
                    if item['value'] != "":
                        #foldertree only have root folder
                        print "item[value]=",item['value']
                        return item['value']
            print "no encrypted metadata record found, aborting"
            return "NONE"
        except Exception as e:
            print "fail to download metadata, returning False"
            print traceback.format_exc()
            return False


    def delete(self, email, fileName):
        try:
            print "__aswin delete__"
            f='/TCSA/%s'%fileName
            pathRecord=None
            self.setCollection(email)
            #get all path and their respective storage,including the path to be deleted
            queryResult=list(self.aCollection.find(
                {"metadata.virtualPath":f},
                {"_id":0}
            ))

            if len(queryResult)==0:
                print "no record in database for this file, returning False..."
                return False
            elif len(queryResult)==1:
                #file is stored in 1 type of storage
                if queryResult[0]['type']=='dropbox':
                    #ros function
                    self.accessToken=self._getAccessToken(email)
                    wrapper=DropboxWrapper(self.accessToken)
                    wrapper.deleteFile(f)

                elif queryResult[0]['type']=="box":
                    raise NotImplementedError
                elif queryResult[0]['type']=="googledrive":
                    #ros function here
                    self.credential=self._getCredential(email)
                    wrapper=GoogleDriveWrapper(self.credential)
                    for record in queryResult[0]['metadata']:
                        #cause query return a list of item inside metadata
                        if record['virtualPath']==f:
                            wrapper.deleteFile(record['fileID'])

            elif len(queryResult)==3:
                raise NotImplementedError

            #delete virtualPath record in db
            self._removeVirtualPath(f, queryResult[0]['type'])
            print "file record [%s] deleted in the mongo database..." %f
            self.client.disconnect()
            return True
        except Exception as e:
            print traceback.format_exc()
            return False

    def spreadData(self, email):
        try:
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
                    print "%s exceed ratio\nusage=%s\nusagelimit(ratio)=%s" % (storage[0],"{:,}".format(usage),"{:,}".format(usageRatio))
                    #storage name, storage amount used, storage size within ratio
                    exceedRatioStorageList.append([storage[0], usage, usageRatio])
                else:
                    print "%s below ratio\nusage=%s\nusagelimit(ratio)=%s" % (storage[0], "{:,}".format(usage), "{:,}".format(usageRatio))
                    #storage name, quota left
                    belowRatioStorageList.append([storage[0], storage[1]])
                    #sorted ascending order
                    belowRatioStorageList=sorted(belowRatioStorageList, key= itemgetter(1))

            for fullStorage in exceedRatioStorageList:
                #bytes toBeRemoved
                toBeRemoved= fullStorage[1]-fullStorage[2]

                #get file list and respective size in fullStorage
                accessToken= self._getAccessToken(email)
                wrapper=DropboxWrapper(accessToken=accessToken)
                files=wrapper.getFileList()
                for i in xrange(len(files)-1,-1,-1):
                    reObj= re.match(r'^/TCSA/.*', files[i][0])
                    if reObj:
                        print "this record in TCSA folder:%s, exclude it"% files[i][0]
                        del files[i]

                #sorted in ascending order
                files= sorted(files, key= itemgetter(1))
                if belowRatioStorageList:
                    #exist storage that doesnt exceed ratio limit
                    for j in xrange(len(belowRatioStorageList)-1, -1, -1):
                        #create folder fromDropbox in googledrive
                        if belowRatioStorageList[0][0]=='googledrive':
                            self.credential=self._getCredential(email)
                            wrapper= GoogleDriveWrapper(self.credential)
                            fromDropboxMetadata= wrapper.createFolder('fromDropbox')
                            fromDropboxFolderID= fromDropboxMetadata['id']

                        self.accessToken=self._getAccessToken(email)
                        dropboxWrapper= DropboxWrapper(self.accessToken)
                        #while dropbox usage is larger that its allowed ratio and googledrive quotaLeft>0
                        while exceedRatioStorageList[0][1]>exceedRatioStorageList[0][2] and belowRatioStorageList[j][1]>0:
                            #download largest file(last item in list cause sorted ascending) from dropbox, keep the metadata
                            filePath=files[-1][0]
                            fileName= filePath.split('/')[-1]
                            fileMetadata= dropboxWrapper.downloadFile(filePath)
                            #upload this metadata to googledrive
                            wrapper.uploadFileContent(fileName, filecontent=fileMetadata,parent_id=fromDropboxFolderID)
                            #delete file in dropbox
                            dropboxWrapper.deleteFile(filePath)
                            #delete file entry in variable files
                            exceedRatioStorageList[0][1]=exceedRatioStorageList[0][1]-files[-1][1]
                            del files[-1]
                        if exceedRatioStorageList[0][1]<=exceedRatioStorageList[0][2]:
                            break


                #print 'Top 10 biggest files:'

                #for path, metadata in heapq.nlargest(10, files.items(), key=lambda x: x[1]['bytes']):
                #    print 't%s: %d bytes' % (path, metadata['bytes'])

                #break
        except Exception as e:
            print traceback.format_exc()
            return False

    def getTempFolderName(self, email):
        self.setCollection(email)
        aRecord=self.aCollection.find(
            {},
            {'_id':1}
        )
        return str(aRecord[0]['_id'])

if __name__ == '__main__':
    #only call these lines when this file is ran
    #mongodb = MongoDBWrapper()
    #mongodb.deleteStorage('googledrive','aswin.setiadi@gmail.com')
    '''
    aStringOri= "hello world"
    if len(aStringOri) % 2 !=0:
        #append 0 if string length is odd
        aString=aStringOri+'0'
        isOdd=True
    else:
        aString=aStringOri
    #ceiling division
    mid= (len(aString)-1)//2+1
    #print mid
    #string index is inclusive
    sec1= aString[:mid]
    sec2= aString[mid:]
    list= zfec.Encoder(2, 3).encode([sec1, sec2])
    corrected= ''.join(zfec.Decoder(2,3).decode([list[0], list[2],], [0,2]))
    if isOdd:
        corrected=corrected[:-1]
    if corrected==aStringOri:
        print corrected
        print True
    else:
        print corrected
        print False
    '''
    m=MongoDBWrapper()
    #m.addStorage('box', 'aswin.setiadi@gmail.com')
    #m.upload_metadata()
    #m.download_metadata()
    #m.upload('aswin.setiadi@gmail.com', 'abFile', "abFile")
    m.download('aswin.setiadi@gmail.com', 'abFile')
    #m.delete('aswin.setiadi@gmail.com', 'abcd1234')
    #print m.getTempFolderName('aswin.setiadi@gmail.com')
    #m.setCollection('aswin.setiadi@gmail.com')
    #m._removeVirtualPath('/TCSA/abcd1234', 'googledrive')