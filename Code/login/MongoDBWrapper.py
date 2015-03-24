from __future__ import division
__author__ = 'aswin'

import pprint
import re
from pymongo import MongoClient
#from pymongo.collection import Collection
from DropboxWrapper import DropboxWrapper
from GoogleDriveWrapper import GoogleDriveWrapper
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
            #return get_dropbox_token(email)
            return Test().getAuthToken(email)
    def _getCredential(self, email):
            #return get_gdrive_credentials(email)
            return Test().getCredentials(email)
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
                raise NotImplementedError

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

    def _getAnyStorage(self):
        #can be dropbox,box, googledrive
        recordList=self.aCollection.find({},{'_id':0,'type':1})
        for record in recordList:
            if record:
                #means this record is the storage record which have field type
                return record['type']


    def _getAllVirtualPathList(self):
        aListOfList=[]
        storages=self.aCollection.find(
            {},{'_id':0,'metadata':1, 'type':1}
        )
        for storage in storages:
            if not storage:
                #this record is the foldertree 1, no metadata, must skip
                continue
            else:
                if storage['type'] == 'dropbox':
                    for path in storage['metadata']:
                        aListOfList.append((path['virtualPath'], storage['type']))
                elif storage['type']== 'googledrive':
                    for path in storage['metadata']:
                            aListOfList.append((path['virtualPath'], storage['type'], path['fileID']))
        return aListOfList



    def _addNewVirtualPath(self, newVirtualPath, chosenStorage, newRecord=None):
        """
        :param newVirtualPath   :new virtualPath to be saved in mongodb
        :param chosenStorage    :as the name suggest
        :param newRecord        :mongodb record for storing file in googledrive(it needs fileID)

        call this method to add newVirtualPath to the database

        note: need to update the function design in the future cause the newVirtualPath is redundant when newRecord is
              not none
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
        print "%s added" % newVirtualPath
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
    def _removeRecordInMetadata(self, record, storage):
        test= self.aCollection.update(
            #if query is empty, can only update first storage, if path in second position in db, the query will not reach it
            #might wipe all entry in that storage according to the parameter(once during experiment, not sure why)
            {'type':storage},
            {
                '$pull':{
                    'metadata':record
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

    #public function
    ###################################################################################################################
    def addAccount(self, email):
        try:
            self.setCollection(email)
            #we need placeholder cause mongodb won't create a collection until there is a record added to it
            #but now with the folder tree metadata kept in mongodb, we used it to replace
            #placholder
            foldertree= {
                'value'             :"",
                'foldertree'        :1

            }
            docID= self.aCollection.insert(foldertree)
            print 'acc added successfully\n##########################################'
            self.client.disconnect()
            return True

        except Exception as e:
            print traceback.format_exc()
            return False

    def addStorage(self, storagetype, email):

        try:
            self.setCollection(email)
            check=list(self.aCollection.find({'type':storagetype}))
            if check:
                print "fail to add storage: %s. it has already existed. returning false" % storagetype
                return False
            newStorageRecord= {
                        'type'       :storagetype,
                        'metadata'   :[]
            }
            if storagetype=='googledrive':
                #all files that is going to gDrive will be stored in same folder, TCSA
                #gDrive handle file naming with id instead of original name, so same files can exist
                #but can uniquely identifiable
                self.credential= self._getCredential(email)
                folderMetaData=GoogleDriveWrapper(self.credential).createTCSAFolder()
                #print folderMetaData['id']
                newStorageRecord['rootID']=folderMetaData['id']


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
            aList=list(self.aCollection.find(
                {'type':storagetype},
                {'metadata':1}
            ))[0]
            paths=[]
            for key in aList:
                if key=='metadata':
                    for path in aList[key]:
                        paths.append(path['virtualPath'].split('/')[-1])

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
            fileSize= len(fileContent)

            #(storagename, quotaleft, totalquota)
            aListofList=self._getRemainingStorage(email)
            if not aListofList:
                print"fail to upload. user has not registered any storage to TCSA. returning False"
                self.client.disconnect()
                return False
            #-1 cause sorted in ascending order
            if fileSize>(aListofList[-1][1]-self.STORAGE_LIMIT_BUFFER):
                print "upload fail due to file size larger than the largest available cloud storag, aborting upload operation..."
                self.client.disconnect()
                return False

            chosenStorage=aListofList[-1][0]
            #uncomment to manually chose storage
            #chosenStorage='dropbox'
            #NOTE
            #access token, credentials etc. already taken care by _getRemainingStorage()

            filePath='/TCSA/%s' % fileName
            if chosenStorage == 'dropbox':
                wrapper= DropboxWrapper(self.accessToken)
                wrapper.uploadFile(dropboxFilePath=filePath, fileContent=fileContent)
                self._addNewVirtualPath(filePath, 'dropbox')

            elif chosenStorage == 'box':
                raise NotImplementedError

            elif chosenStorage == 'googledrive':
                #get TCSA folder id
                #[0] means first item in pymongo cursor object, then get the value from key rootID
                rootID  =list(self.aCollection.find(
                    {'type':'googledrive'},
                    {'_id':0, 'rootID':1}
                ))[0]['rootID']

                #fileLocation= '/home/rohit008/TCSA/Code/login/files/'+self.getTempFolderName(email)
                #if not os.path.exists(fileLocation):
                #    os.makedirs(fileLocation)
                #filePath =fileLocation+'/'+fileName+'.txt'
                #open(filePath, 'wb').write(fileContent)

                wrapper =GoogleDriveWrapper(self.credential)
                file    =wrapper.uploadFileContent(filename=fileName, filecontent=fileContent, parent_id=rootID)

                #UPDATE DATABASE FOR GOOGLEDRIVE SCENARIO
                newRecord={
                    'virtualPath': filePath,
                    'fileID'     : file['id']
                }

                self._addNewVirtualPath(filePath, 'googledrive', newRecord)

            self.client.disconnect()
            #shutil.rmtree(fileLocation)
            #os.removedirs(fileLocation)
            return True
        except Exception as e:
            print traceback.format_exc()
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

            content= False
            for eachStorage in record:
                if not eachStorage:
                    #this record is foldertree record
                    continue
                print eachStorage
                if 'metadata' in eachStorage:
                    #this record is the storage record that has the sought after file
                    print 'found record in %s' % eachStorage['type']
                    #call respective storage api
                    if eachStorage['type']=='dropbox':
                        #call ross func
                        self.accessToken=self._getAccessToken(email)

                        wrapper=DropboxWrapper(self.accessToken)
                        content= wrapper.downloadFile(filePath)

                    elif eachStorage['type']=='box':
                        raise

                    elif eachStorage['type']=='googledrive':
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
            print traceback.format_exc()
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
            return "NONE"
        except Exception as e:
            print traceback.format_exc()
            return False


    def delete(self, email, fileName):
        try:
            print "__aswin delete__"
            f='/TCSA/%s'%fileName
            pathRecord=None
            self.setCollection(email)
            #get all path and their respective storage,including the path to be deleted
            temp=self._getAllVirtualPathList()
            for t in temp:
                if t[0]==f:
                    #found the storage where file is stored
                    pathRecord=t
                    #remove this path in all path list
                    #temp.remove((f, virtualPathStorage))
                    #print 'virtualpathStorage found...'
                    break
            if pathRecord[1]=='dropbox':
                #ros function here
                self.accessToken=self._getAccessToken(email)
                wrapper=DropboxWrapper(self.accessToken)
                wrapper.deleteFile(f)

            elif pathRecord[1]=='box':
                raise NotImplementedError

            elif pathRecord[1]=='googledrive':
                #ros function here
                self.credential=self._getCredential(email)
                wrapper=GoogleDriveWrapper(self.credential)
                wrapper.deleteFile(pathRecord[2])

            #delete virtualPath record in db
            self._removePath(f, pathRecord[1])
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
    aStringOri= 'YQDonaV/BlVyboCsI18Yfc2KrG4mTMhonX7Ujkdc98j56H8cDMdzalBfydSOnPuUbS8/HgdP5fOxjEoUrtK3iDNOSgUt6rvMc7ZUdDMNvCD4OVgXTQ5JEE/MfSyJtWB8G8b+M+UwinHkwFFYCfSeBwTtrE94H9aUGq+GzIy3jPmgPGKg1y5tKQJThCsK/2eHnfGgdpqM1I8Dd+Byuos/4f4VDiezUj6A8SdnmD57lgvixerLoXDmNNUSwu4LQ/Wu8m1VkIjmKq4ZTpgxfTySdk80hluKBohaqhqleOXlVqfxhKDwYvjuc2jpY3ewjbmwSYquHnKxzD1piZfyCXHdxFu/IqU1HYzMQtDzH5YWVOvMnsCQoboN9g+p4oDMjyiR8gPauDC3VELuDiN4srvgC0Xdh/k7jPpkqQsmUHbo925TZ6pKpVNAwVaYW2yeD7U92iHcKbspHbdpQ/EZl0lJmN56emy/Gg7iVd9ZBwA/peKduwk0kj4c3S/AbuGZeATSwIk/FYupEFrN9MeMHenBcAoYphISW89yTE4EaCqgA3Zb3RZiZZTQnj60G5z40Rtt6qnUGWbm5ms3809w2AwnmcYa8mRN5gMGcWpnsZDz9cfs6/SX0O/LEyXDantfbb5bZnMtzkNay5in8ZmepTBXXuLdQHQ7baV5WTRP14DpsNk=-'
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
    print sec1+sec2
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