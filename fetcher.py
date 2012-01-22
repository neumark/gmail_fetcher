#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#Making a proxy: ssh -L993:imap.gmail.com:993 neumark@info.ilab.sztaki.hu
import imaplib
import getpass
import datetime
import email

def parse_email(raw_email):
    email_message = email.message_from_string(raw_email)
    print email_message['To']
    print email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
    print email_message.items() # print all headers
    # note that if you want to get text content (body) and the email contains
    # multiple payloads (plaintext/ html), you must parse each message separately.
    # use something like the following: (taken from a stackoverflow post)
    def get_first_text_block(self, email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
                elif maintype == 'text':
                    return email_message_instance.get_payload()

def fetch_email(mail, uid):
    result, data = mail.uid('fetch', uid, '(RFC822)')
    return data[0][1]

def auth():
    mail = imaplib.IMAP4_SSL('localhost') #imap.gmail.com if no proxy
    username=raw_input("Please enter your email address: ")
    password=getpass.getpass()
    mail.login(username, password)
    # Out: list of "folders" aka labels in gmail.
    mail.select("[Gmail]/All Mail") # connect to "All Mail" folder.
    date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=date))
    raw_message = fetch_email(mail, data[0].split()[-1])
    parse_email(raw_message)

auth()
