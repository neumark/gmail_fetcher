  CREATE TABLE `msg` (
  `gm_msg_uid` bigint(20) unsigned NOT NULL,
  `gm_thread_id` bigint(20) unsigned DEFAULT NULL,
  `labels` varchar(2048) DEFAULT NULL,
  `subject` varchar(2048) NOT NULL,
  `sender` varchar(512) NOT NULL,
  `date` datetime NOT NULL,
  `sync_session` int(11) NOT NULL,
  `message_id` varchar(511) NOT NULL,
  `imap_uid` int(11) NOT NULL,
  PRIMARY KEY (`gm_msg_uid`),
  UNIQUE KEY `gm_msg_uid_UNIQUE` (`gm_msg_uid`),
  KEY `thread` (`gm_thread_id`),
  KEY `subject` (`subject`(255)),
  KEY `date` (`date`),
  KEY `labels` (`labels`(255)),
  KEY `fk_sync` (`sync_session`),
  KEY `message_id` (`message_id`(255)),
  KEY `sender` (`sender`(255)),
  KEY `imap_uid` (`imap_uid`),
  CONSTRAINT `fk_sync` FOREIGN KEY (`sync_session`) REFERENCES `sync` (`idsync`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ; 

CREATE TABLE `sync` (
  `idsync` int(11) NOT NULL AUTO_INCREMENT,
  `start` date NOT NULL,
  `end` date NOT NULL,
  `status` varchar(16) DEFAULT NULL,
  `import_success` int(11) DEFAULT NULL,
  `import_error` int(11) DEFAULT NULL,
  `import_duplicate` int(11) DEFAULT NULL,
  PRIMARY KEY (`idsync`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8 ;

CREATE TABLE `body` (
  `gm_msg_uid` bigint(20) NOT NULL,
  `raw` longtext NOT NULL,
  `headers_json` text NOT NULL,
  `body_text` text NOT NULL,
  PRIMARY KEY (`gm_msg_uid`),
  FULLTEXT KEY `bodytext` (`body_text`),
  FULLTEXT KEY `headertext` (`headers_json`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 ;

CREATE TABLE `ex` (
  `idex` int(11) NOT NULL AUTO_INCREMENT,
  `sync_id` int(11) DEFAULT NULL,
  `type` varchar(127) DEFAULT NULL,
  `message` mediumtext,
  `traceback` text,
  `ex_msg` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`idex`),
  KEY `sync` (`sync_id`)
) ENGINE=InnoDB AUTO_INCREMENT=242 DEFAULT CHARSET=utf8 ;
