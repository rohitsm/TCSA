import cgi, os
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper

try:
    import msvcrt
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)
except ImportError:
    print 'import msvcrt fail'

form        =cgi.FieldStorage()

#these 3 should be the argument for the data in ajax call
#uploading to root folder should have string '/' in TCSApath
#uploading to a folder e.g. imageFolder should put string '/imageFolder' in TCSApath
fileitem    =form['file']
email       =form['email']
folderPath  =form['TCSApath']


#check if file has reached to this server completely
if fileitem.filename:
        #retrieve filename without the folder path to prevent directory traversal attack
        fn=os.path.basename(fileitem.filename)
        fileLocation='files/'+fn
        #todo change 'files/' to be dynamic
        open('files/'+fn, 'wb').write(fileitem.file.read())
        print 'file has been saved in files folder...'
        MongoDBWrapper.upload(email, folderPath, fileLocation)
        print 'file uploaded to cloud storage..'
        os.remove(fileLocation)
        print 'file deleted from local folder..'


