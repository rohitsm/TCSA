import cgi
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper


form        =cgi.FieldStorage()

email       =form['email']
folderName  =MongoDBWrapper().getTempFolderName(email)
saveLocation='files/'+ folderName
MongoDBWrapper().download(email, folderName, saveLocation)

if __name__== '__main__':
    print 'nothing'