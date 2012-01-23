#from http://zetcode.com/databases/mysqlpythontutorial/
import sys 
import json
import time

def mysql_date(d):
    return time.strftime('%Y-%m-%d %H:%M:%S', d)

class Db:
    statements= {
        'msg': "INSERT INTO `email`.`msg` (gm_msg_uid, gm_thread_id, labels, subject, sender, date, sync_session, message_id, imap_uid) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'body': "INSERT INTO `email`.`body` (`gm_msg_uid`, `raw`, `headers_json`, `body_text`) VALUES ( %s, %s, %s, %s )",
        'ex': "INSERT INTO `email`.`ex` (`sync_id`, `type`,`ex_msg`,  `message`, `traceback`) VALUES (%s, %s, %s, %s, %s)",
        'sync': "INSERT INTO `email`.`sync` (`start`, `end`, `status`) VALUES (%s, %s, %s)",
        'sync_update': "UPDATE `email`.`sync` SET `status` = %s, `import_success` = %s, `import_error` = %s, `import_duplicate` = %s WHERE idsync = %s"
    }

    def __init__(self, conn, interval):
        self.conn = conn
        # init connection
        cur = self.conn.cursor()
        cur.execute("SET NAMES utf8; SET CHARACTER SET utf8; SET character_set_connection=utf8")
        cur.close()
        self.start = interval[0]
        self.end = interval[1]
        self.sessionid = self.add_sync_record(self.start, self.end)
        print "Sync session id: "+str(self.sessionid)

    def esc_str(self,s):
        return s

    def save_processing_results(self, res, numdups):
        counter = 0
        for i in res:
            if i == True:
                counter = counter + 1
        self.with_conn(self.execute, ("sync_update", (
            "finished",
            counter,
            len(res) - counter,
            numdups,
            self.sessionid)))

    def with_conn(self, fun, args=None):
        ret = None
        cur = self.conn.cursor()
        try:
            ret = fun(cur, args) if args is not None else fun(cur)
        except Exception, e:
            cur.close()
            raise
        cur.close()
        return ret

    def execute(self, cur, args):
        table = args[0]
        values = args[1]
        cur.execute(self.statements[table], values)

    def add_sync_record(self, start, end):
        def work(cur):
            self.execute(cur, ('sync',(mysql_date(start), mysql_date(end), "unfinished")))
            cur.execute("SELECT LAST_INSERT_ID()")
            return cur.fetchone()[0]
        return self.with_conn(work)        

    def add_msg(self, raw_msg, parsed_msg):
        #X-GM-MSGID': '1357631546161653087', 'To': [u'hulyesegek@googlegroups.com'], 'Message-ID'
        #(gm_msg_uid, gm_thread_id, labels, subject, sender, date, sync_session, message_id)
        self.with_conn(self.execute, ('msg', (
            self.esc_str(parsed_msg['headers']['x-gm-msgid']),
            self.esc_str(parsed_msg['headers']['x-gm-thrid']),
            self.esc_str(parsed_msg['headers']['x-gm-labels']),
            self.esc_str(parsed_msg['headers']['subject'][0]),
            self.esc_str(parsed_msg['headers']['from'][0]),
            mysql_date(parsed_msg['headers']['python_time']),
            self.sessionid,
            self.esc_str(parsed_msg['headers']['message-id'][0]),
            self.esc_str(parsed_msg['headers']['imap-uid'])
            )))
        #(`gm_msg_uid`, `raw`, `headers_json`, `body_text`)
        del parsed_msg['headers']['python_time']
        self.with_conn(self.execute, ('body', (
            self.esc_str(parsed_msg['headers']['x-gm-msgid']),
            self.esc_str('\n'.join(raw_msg)),
            self.esc_str(json.dumps(parsed_msg['headers'])),
            self.esc_str(parsed_msg['body'])
            )))

    def save_ex(self, ex_data, raw_msg):
        return self.with_conn(self.execute, ('ex', (
            self.sessionid, 
            self.esc_str(ex_data['type']),
            self.esc_str(ex_data['value']),
            self.esc_str(raw_msg),
            self.esc_str(json.dumps(ex_data['traceback'])))))

    def filter_duplicate_msgids(self, uids):
        def work(cur):
            dups_query = "select imap_uid from email.msg where imap_uid in ("+",".join(uids)+")"
            non_dups = set(uids)
            cur.execute(dups_query)
            for row in cur.fetchall():
                print row[0]
                non_dups.remove(str(row[0]))
            return list(non_dups)
        return self.with_conn(work)

    def close(self):
        self.conn.commit()
        self.conn.close()
