import cgi
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper

if __name__== '__main__':
    form        =cgi.FieldStorage()
    email       =form['email']
    #generate unique folder for this user
    folderName  =MongoDBWrapper().getTempFolderName(email)
    saveLocation='files/'+ folderName
    MongoDBWrapper().download(email, folderName, saveLocation)

