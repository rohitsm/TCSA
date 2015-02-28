__author__ = 'aswin'

import dropbox
import pprint
import re

class DropboxWrapper:

    def __init__(self, accessToken):
        self.client     = dropbox.client.DropboxClient(accessToken)
    #Dropbox operation utilities~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getDropboxStorageSizeLeft(self):
        #accInfo is a dict object
        accInfo     = self.client.account_info()
        quota_info  = accInfo['quota_info']
        #print "used: ", quota_info['normal']
        quotaLeft   = quota_info['quota']-quota_info['shared']-quota_info['normal']
        print "dropbox storage remaining: %s bytes" % quotaLeft
        return quotaLeft


    def uploadFile(self, filePath, virtualPath):
        #assume filePath contain filename, virtualPath does not
        matchObj= re.match(r".*/(.*)", filePath)
        filename='/'+matchObj.group(1)
        f           = open(filePath, 'rb')
        #argument for filePath and storagePath is the same
        #so no problem with saving filenames with same name in dropbox because
        #files with same name will be stored in different folder

        #saving to dropbox folder can don't have initial /
        #eg saving in /animal/monkey.pdf just write animal/monkey.pdf
        #works for both uploading and downloading
        #but try to use it constantly
        response    = self.client.put_file(virtualPath+filename, f)
        f.close()

    def downloadFile(self, saveLocation, storagePath):
        f, metadata = self.client.get_file_and_metadata(storagePath)
        #this will extract the filename from storagePath
        #.* is greedy in nature, so it will cut at last /
        matchObj= re.match(r".*/(.*)", storagePath)
        fileName= '/'+matchObj.group(1)

        out         = open(saveLocation+fileName, 'wb')
        out.write(f.read())
        out.close()

    def deleteFile(self, filePath):
        '''
        sample response from file_delete(path)
        {
            "size": "0 bytes",
            "is_deleted": true,
            "bytes": 0,
            "thumb_exists": false,
            "rev": "1f33043551f",
            "modified": "Wed, 10 Aug 2011 18:21:30 +0000",
            "path": "/test .txt",
            "is_dir": false,
            "icon": "page_white_text",
            "root": "dropbox",
            "mime_type": "text/plain",
            "revision": 492341
        }
        '''
        response=self.client.file_delete(filePath)
        return response


"""
aswin= DropboxWrapper('aswin.setiadi@gmail.com')
aswin.initClient()
localpath='animals/hello.txt'
virtualpath='collection//text'
aswin.uploadFile(localpath, virtualpath)
#aswin.downloadFile('C:/Users/aswin/Downloads',localpath)
"""