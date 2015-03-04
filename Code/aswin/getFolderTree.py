import cgi
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper

if __name__== '__main__':
    form        =cgi.FieldStorage()
    email       =form['email']
    print MongoDBWrapper().getFolderTree(email)
