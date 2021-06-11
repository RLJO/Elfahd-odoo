import urllib2
import cookielib
from getpass import getpass
import sys

user = 'gannas.hr'
password = '123456Aa'
to = '966548981892'
message = 'Test'
sender = 'GannasCo'

url = 'http://www.jawalbsms.ws/api.php/sendsms?'
data = 'user=%s&pass=%s&to=%s&message=%s&sender=%s' % (user, password, to, message, sender)

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

opener.addheaders = [('User-Agent',
                      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36')]
try:
    usock = opener.open(url, data)
except IOError:
    print "Error while logging in."
    sys.exit(1)
send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
try:
    sms_sent_page = opener.open(send_sms_url)
except IOError:
    print "Error while sending message"
    sys.exit(1)
print "SMS has been sent."
