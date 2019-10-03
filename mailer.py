import yagmail
import specifications

def mailer(payload):
    address1 = "jeroenwalta@gmail.com"
    address2 = "jeroen@optieclub.nl"
    addressList = [address1, address2]
    yag = yagmail.SMTP(specifications.mail_a, specifications.mail_p)
    yag.send(to=addressList, subject='order filled', contents=payload)

