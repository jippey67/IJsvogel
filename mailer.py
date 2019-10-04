import yagmail

def mailer(address, passw, payload):
    address1 = "jeroenwalta@gmail.com"
    address2 = "jeroen@optieclub.nl"
    addressList = [address1, address2]
    yag = yagmail.SMTP(address, passw)
    yag.send(to=addressList, subject='order filled', contents=payload)

