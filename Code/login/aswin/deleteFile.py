__author__ = 'aswin'
import cgi
import cgitb; cgitb.enable()
from lib.MongoDBWrapper import MongoDBWrapper

if __name__== '__main__':
    form  =cgi.FieldStorage()
    email       =form['email']
    filePath    =form['TCSApath']
    ##/file.xyz means file in the root
    MongoDBWrapper().delFile(email, '/'+filePath)