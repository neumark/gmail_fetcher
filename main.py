import datetime
import fetcher
import ex_catcher
import db
import optparse
import time
import sys

def parseargs():
    def ptime(s):
        return time.strptime(s, "%d-%b-%Y")
    parser = optparse.OptionParser(usage="""\
Fetches messages from gmail.
Usage: %prog -s startdate -e enddate
""")
    parser.add_option('-s', '--start', type='string', action="store", metavar="START", help="start date")
    parser.add_option('-e', '--end', type='string', action="store", metavar="END", help="end date")
    opts, args = parser.parse_args()
    if not opts.start or not opts.end:
        parser.print_help()
        sys.exit(1)
    return (ptime(opts.start), ptime(opts.end))

# make imap query
def get_msg_list(fetcher, dbobj):
    imap_results = fetcher.query("hulyesegek", start, end)
    new_results = dbobj.filter_duplicate_msgids(imap_results) # or "[Gmail]/All Mail"
    return (new_results, len(imap_results))

# process new results
def process_email(raw):
    print "processing:  "+raw[0]
    def work():
        dbobj.add_msg(raw, fetcher.parse_email(raw))
    status, result = ex_catcher.maybe_ex(work)
    if (status == "exception"):
        dbobj.save_ex(result, "\n".join(raw))
        return False
    return True

if __name__ == '__main__':
    start, end = parseargs()
    dbobj = db.Db({
        'host':"127.0.0.1",
        'user':"email", 
        'passwd':"email",
        'db':"email",
        'use_unicode':True,
        'charset':"utf8"}, (start, end))
    fetcher = fetcher.Fetcher() 
    fetcher.auth('localhost', 1995)
    new_uids, num_imap_results = get_msg_list(fetcher, dbobj)
    print "IMAP Server returned " + str(num_imap_results) + " results ("+str(len(new_uids))+" new)"
    processing_results = []
    if len(new_uids) > 0:
        raw_mails = fetcher.fetch_emails(new_uids)
        print "Received "+str(len(raw_mails))+" raw emails from server."
        processing_results = [process_email(raw_email) for raw_email in raw_mails]
    dbobj.save_processing_results(processing_results, num_imap_results - len(new_uids))
    dbobj.close()
