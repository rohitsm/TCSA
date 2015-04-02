import StringIO
from googleapiclient.http import MediaIoBaseUpload

__author__ = 'aswin'

from boxsdk import OAuth2
from boxsdk import Client
from aswin.Test import Test
import traceback




class BoxWrapper:

    def __init__(self, aTuple):

        try:
            self.accessToken    = aTuple[2]
            self.refreshtoken   = aTuple[3]
            self.oauth= OAuth2(
                client_id       =aTuple[0],
                client_secret   =aTuple[1],
                access_token    =self.accessToken,
                refresh_token   =self.refreshtoken
                )
            self.client= Client(self.oauth)
        except Exception:
            print traceback.format_exc()



    def getBoxStorageSizeLeft(self):
        try:
            user        = self.client.user(user_id=unicode('me')).get()
            spaceLeft   = user['space_amount']
            totalSpace  = spaceLeft+user['space_used']
            return (spaceLeft, totalSpace)
        except Exception:
            print traceback.format_exc()
            return False

    def createFolder(self, folderName, parentID=unicode(0)):
        try:
            folder=self.client.folder(folder_id=parentID).create_subfolder(unicode(folderName))
            #folder is a Folder object
            return folder.get()['id']
        except Exception:
            print traceback.format_exc()
            return False

    def uploadFileContent(self, filename, filecontent, TCSAFolderID):
        #convert filecontent from string to stringIO object

        filedata= StringIO.StringIO(filecontent)

        try:
            folder=self.client.folder(folder_id=TCSAFolderID)
            fileID=folder.upload_stream(filedata, file_name=filename).get()['id']
            #return File object
            return fileID
        except Exception:
            print traceback.format_exc()
            return False

    def downloadFile(self, fileID):
        try:
            fileStream=StringIO.StringIO()
            self.client.file(fileID).download_to(fileStream)
            return fileStream
        except Exception:
            print traceback.format_exc()
            return False



    def refreshToken(self):
        print "old access token:%s\n old refresh token:%s" % (self.accessToken, self.refreshtoken)
        return self.oauth.refresh(self.accessToken)

if __name__=="__main__":
    b=BoxWrapper(Test().getBoxIDToken('aswin.setiadi@gmail.com'))


    #print b.client.user(user_id='me').get()

    #redirect_url=unicode('http://localhost')
    #auth_url, csrf_token = oauth.get_authorization_url(redirect_url)
    #print auth_url
    #print csrf_token