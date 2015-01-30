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
        f           = open(filePath, 'rb')
        #argument for filePath and storagePath is the same
        #so no problem with saving filenames with same name in dropbox because
        #files with same name will be stored in different folder

        #saving to dropbox folder can don't have initial /
        #eg saving in /animal/monkey.pdf just write animal/monkey.pdf
        #works for both uploading and downloading
        response    = self.client.put_file(virtualPath+'/'+matchObj.group(1), f)
        f.close()

    def downloadFile(self, saveLocation, storagePath):
        f, metadata = self.client.get_file_and_metadata(storagePath)
        #this will extract the filename from storagePath
        #.* is greedy in nature, so it will cut at last /
        matchObj= re.match(r".*/(.*)", storagePath)
        out         = open(saveLocation+'/'+matchObj.group(1), 'wb')
        out.write(f.read())
        out.close()
        print "downloaded, metadata:/n"
        pprint.pprint(metadata)

"""
aswin= DropboxWrapper('aswin.setiadi@gmail.com')
aswin.initClient()
localpath='animals/hello.txt'
virtualpath='collection//text'
aswin.uploadFile(localpath, virtualpath)
#aswin.downloadFile('C:/Users/aswin/Downloads',localpath)
"""