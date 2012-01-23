#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://stackoverflow.com/questions/261655/converting-a-list-of-tuples-into-a-dict-in-python
#Making a proxy: ssh -L1993:imap.gmail.com:993 login@shell-account.com
import imaplib
import getpass
import email
import email.header
import email.utils
import quopri
import re
import HTMLParser
import time
import datetime
import ex_catcher

class Fetcher:
    gm_header_re = re.compile("^(\d+) \(X-GM-THRID (\d+) X-GM-MSGID (\d+) X-GM-LABELS \(([^\)]*)\) UID (\d+) RFC822 {(\d+)}$")
    def parse_email(self, full_message):
        raw_email = full_message[1]
        gm_headers = full_message[0]
        email_message = email.message_from_string(raw_email)
        def stripbrackets(msgid):
            if msgid[0] == "<":
                msgid = msgid[1:]
            if msgid[-1] == ">":
                msgid = msgid[0:-1]
            return msgid
        def parse_headers():
            hdict = {}
            for hdr, val in email_message.items():
                uval = u''
                for decoded_val in email.header.decode_header(val):
                    uval = uval + unicode(decoded_val[0], decoded_val[1] if decoded_val[1] is not None else "ascii")
                hdict.setdefault(hdr.lower(), []).append(uval)
            groups = self.gm_header_re.match(gm_headers).groups()
            hdict['x-gm-thrid'] = unicode(groups[1])
            hdict['x-gm-msgid'] = unicode(groups[2])
            hdict['x-gm-labels'] = unicode(groups[3])
            hdict['imap-uid'] = unicode(groups[4])
            hdict['message-id'] = [stripbrackets(hdict['message-id'][0])]
            hdict['python_time'] = datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(hdict['date'][0]))).timetuple()
            return hdict

        def get_first_text_block():
            def toutf(part):
                charset = part.get_content_charset() if part.get_content_charset() is not None else 'ascii'
                s = part.get_payload(decode=True)
                if part.get_content_type() == "text/html":
                    h = HTMLParser.HTMLParser()
                    return h.unescape(unicode(s, charset))
                else:
                    return unicode(quopri.decodestring(s), charset)
            maintype = email_message.get_content_maintype()
            if maintype == 'multipart':
                for part in email_message.get_payload():
                    if part.get_content_maintype() == 'text':
                        return toutf(part)
                    elif maintype == 'text':
                        return toutf(email_message)
            else:
                return toutf(email_message)
        return {
            'headers': parse_headers(),
            'body': get_first_text_block(),
            'raw': full_message
        }

    def fetch_emails(self, uids):
        result, data = self.mail.uid('fetch', ','.join(uids), '(RFC822 X-GM-THRID X-GM-MSGID X-GM-LABELS X-GM-MSGID)')
        return [data[i] for i in range(0, len(data) - 1, 2)]

    def make_query(self, start, end):
        def fmttime(t):
            return time.strftime("%d-%b-%Y", t)
        return '(SENTSINCE {startdate}) (SENTBEFORE {enddate})'.format(startdate=fmttime(start), enddate=fmttime(end))

    def auth(self, host = 'imap.gmail.com', port = 993, username=None, password=None):
        mail = imaplib.IMAP4_SSL(host, port) #imap.gmail.com and 993 if no proxy
        mail.login(
            username if username is not None else raw_input("Please enter your email address: "), 
            password if password is not None else getpass.getpass())
        self.mail = mail

    def query(self, folder="[Gmail]/All Mail", start = (datetime.date.today() - datetime.timedelta(1)), end = (datetime.date.today())):
        # Out: list of "folders" aka labels in gmail.
        self.mail.select(folder) # connect to "All Mail" folder.
        imapquery = self.make_query(start, end)
        print "IMAP query is "+imapquery
        status, data = self.mail.uid('search', None, imapquery)
        return data[0].split()
