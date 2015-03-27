import pyotp
import time
import qrcode
from PIL import Image

# base32key = pyotp.random_base32()
base32key = 'QT2UATPAFB5LVIIK'
print "base32key = ", base32key

totp = pyotp.TOTP(base32key)
email1 = totp.provisioning_uri("admin@tcsa.com")
print "Email: ", email1

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(email1)
qr.make(fit=True)

img = qr.make_image()
print img
img.save('qrcode.png')

print "totp.now(): ", totp.now()

code = raw_input("Code:")
print "totp.verify(code): ", totp.verify(code)

# for i in range (1, 100):
# 	print "TOTP: %s %s" %(i, totp.now())
# 	time.sleep(1)


# img = qrcode.make(prov_uri)


