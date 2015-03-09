__author__ = 'aswin'

import httplib2
import re

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient import errors
from oauth2client.client import Credentials

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE  = 'https://www.googleapis.com/auth/drive'

class GoogleDriveWrapper:

    def __init__(self, credential):
        self.credential    = Credentials().new_from_json(credential)
        self.http           = self.credential.authorize(httplib2.Http())

        #cos in the constructor, http argument is = None
        self.driveService   = build('drive', 'v2', http=self.http)

    #gDrive operation utilities

    def getStorageSizeLeft(self):
        userAbout       = self.driveService.about().get().execute()
        quota           = long(userAbout['quotaBytesTotal'])
        storageRemaining= quota-long(userAbout['quotaBytesUsedAggregate'])
        print 'gDrive storage remaining: %s bytes' % storageRemaining
        return (storageRemaining,quota)

    #by default from argument parentFolderID, folder will be created inside root
    def createFolder(self, folderName, parentFolderID='root'):
        body={
            'title'     :folderName,
            'mimeType'  :'application/vnd.google-apps.folder',
            'parents'   :[{'id':parentFolderID}]
        }
        folder= self.driveService.files().insert(body=body).execute()
        print "returning whole folder metadata"
        return folder

    def createTCSAFolder(self):
        #create TCSA folder in root folder
        body={
            'title'     :'TCSA',
            'mimeType'  :'application/vnd.google-apps.folder'
        }
        folder= self.driveService.files().insert(body=body).execute()
        print 'TCSA folder id: %s' % folder['id']
        print "returning whole folder metadata"
        return folder

    def uploadFile(self, filePath, parent_id):
        filename        = re.match(r".*/(.*)", filePath).group(1)
        media_body      = MediaFileUpload(filePath, resumable=True)
        body={
            'title'         : filename
        }
        if parent_id:
            body['parents']=[{'id':parent_id}]
        try:
            #file is a dictionary
            file= self.driveService.files().insert(body=body, media_body=media_body).execute()
            print "[%s]" % file
            return file
        except errors.HttpError, error:
            print 'An error occured: %s \n returning None' % error
            return None

    def downloadFile(self, fileID):
        try:
            file        = self.driveService.files().get(fileId=fileID).execute()
            download_url= file.get('downloadUrl')
            if download_url:
                resp, content= self.driveService._http.request(download_url)
                if resp.status == 200:
                    #print 'status : %s' % resp
                    #out = open(saveLocation+'/'+file['title'], 'wb')
                    #out.write(content)
                    #out.close()
                    return content
                else:
                    print 'An error occured: %s' % resp
                    return False
        except errors.HttpError, error:
            print 'An error occured: %s' % error

    def deleteFile(self, fileID):
        try:
            self.driveService.files().delete(fileId=fileID).execute()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error

#aswin= GoogleDriveWrapper('aswin.setiadi@gmail.com')
#aswin.initDriveService()
#pprint.pprint(aswin.createFolder('animal'))
#pprint.pprint(aswin.uploadFile('animals/monkey.jpg', '0BxW12JobWFjkNGhmTHNpZjZpTjg'))
#aswin.downloadFile('0BxW12JobWFjkSGV2T0J6b19HWFE','C:/Users/aswin/Downloads')