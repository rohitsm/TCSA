__author__ = 'aswin'

from dropbox.client import DropboxClient
import traceback


class DropboxWrapper:

    def __init__(self, accessToken):
        try:
            self.client     = DropboxClient(accessToken)
        except Exception as e:
            print traceback.format_exc()
    #Dropbox operation utilities~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getDropboxStorageSizeLeft(self):
        #accInfo is a dict object
        #return tuple (quota left, total quota)
        #both or long type
        try:
            accInfo     = self.client.account_info()
            quota_info  = accInfo['quota_info']
            #print "used: ", quota_info['normal']
            quotaLeft   = quota_info['quota']-quota_info['shared']-quota_info['normal']
            print "dropbox storage remaining: %s bytes" % quotaLeft

            return (quotaLeft, quota_info['quota'])
        except Exception as e:
            print traceback.format_exc()
            return False


    def uploadFile(self, dropboxFilePath, fileContent):
        #assume filePath contain filename, virtualPath does not
        #matchObj= re.match(r".*/(.*)", filePath)
        #filename='/'+matchObj.group(1)
        #f           = open(filePath, 'rb')
        #argument for filePath and storagePath is the same
        #so no problem with saving filenames with same name in dropbox because
        #files with same name will be stored in different folder

        #saving to dropbox folder can don't have initial /
        #eg saving in /animal/monkey.pdf just write animal/monkey.pdf
        #works for both uploading and downloading
        #but try to use it constantly

        #dropboxFilePath   = name of the encrypted file
        #fileContent= stream of char of the file
        response    = self.client.put_file(dropboxFilePath, fileContent, overwrite=True)
        if response:
            return response
        else:
            return False

    def downloadFile(self, dropboxFilePath):
        #f          =file like object
        #metadata   = dict object, describing file
        f, metadata = self.client.get_file_and_metadata(dropboxFilePath)
        content= f.read()
        f.close()
        #return a stream of char of the file
        if metadata:
            return content
        else:
            return False

    def deleteFile(self, dropboxFilePath):
        '''
        deleting non-existent file/folder will raise an error
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

        response=self.client.file_delete(dropboxFilePath)
        if response:
            return response
        else:
            return False

    def getFileList(self, files=None, cursor=None, excludedFolder=None):
        '''

        :param files            : list of the files
        :param cursor           : cursor object to iterate through delta function of dropbox
        :param excludedFolder   : folder to be excluded, so the files within won't be added to the list
        :return                 : [filepath, filesize]
        '''
        if files is None:
            #files = {}
            files=[]
        has_more = True
        while has_more:
            result = self.client.delta(cursor)
            cursor = result['cursor']
            has_more = result['has_more']

            #raw_input("pause dropboxWrapper")
            for lowercase_path, metadata in result['entries']:
                if metadata is not None:
                    # no metadata indicates a deleted file record
                    if not metadata['is_dir']:
                        #files[metadata['path']] = metadata['size']
                        files.append((metadata['path'], metadata['bytes']))
        return files

if __name__=='__main__':
    print min([1,2,3,4,5,6,7,8], key=lambda x:abs(x-6.5))
    if not None:
        print False