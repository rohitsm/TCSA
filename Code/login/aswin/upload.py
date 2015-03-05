import cgi, os
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper

'''
try:
    import msvcrt
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)
except ImportError:
    print 'import msvcrt fail'
'''

if __name__=="__main__":
    form        =cgi.FieldStorage()
    #these 3 should be the argument for the data in ajax call
    #uploading to root folder should have string '' in TCSApath
    #uploading to a folder e.g. imageFolder should put string '/imageFolder' in TCSApath
    fileitem        =form['file']
    email           =form['email']
    TCSAfolderPath  =form['TCSApath']

    #check if file has reached to this server completely
    if fileitem.filename:
            #retrieve filename without the folder path to prevent directory traversal attack
            fn=os.path.basename(fileitem.filename)
            #generate folder according to each unique user record ID
            folderPath= 'files/'+MongoDBWrapper().getTempFolderName(email)
            open(folderPath+'/'+fn, 'wb').write(fileitem.file.read())

            MongoDBWrapper.upload(email, TCSAfolderPath, folderPath+'/'+fn)
            print 'file uploaded to cloud storage..'
            #delete this unique folder belonging to this user
            os.remove(folderPath)
            print 'file deleted from local folder..'


