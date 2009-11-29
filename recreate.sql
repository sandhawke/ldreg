--
--  USE WITH EXTREME CAUTION.   WILL DELETE EVERYTHING IN THE DATABASE
--  TABLES THAT WE USE.
--
--  use like this:    mysql ldreg < recreate.sql 
--
--
DROP TABLE IF EXISTS `scan`;
CREATE TABLE `scan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) NOT NULL,
  `time_begun` int(11) NOT NULL,
  `time_first_triple` int(11),
  `triples` int(11) NOT NULL,
  `time_complete` int(11),
  `last_modified` char(32),
  `status` int(8),
  PRIMARY KEY (id),
  FOREIGN KEY (source_id) REFERENCES iri (id)
);
--
--
--
DROP TABLE IF EXISTS `term_use`;
CREATE TABLE `term_use` (
  `local` varchar(255) NOT NULL,
  `namespace_id` int(11) NOT NULL,
  `scan_id` int(11) NOT NULL,
  `type` varchar(1) NOT NULL,
  `count` int(11),
  PRIMARY KEY (`local`,`namespace_id`,`scan_id`,`type`),
  FOREIGN KEY (namespace_id) REFERENCES iri (id),
  FOREIGN KEY (scan_id) REFERENCES scan (id)
);
--
--
--
DROP TABLE IF EXISTS `iri`;
CREATE TABLE `iri` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` text,
  PRIMARY KEY (`id`)
);
--
--
--
DROP TABLE IF EXISTS `regq`;
CREATE TABLE `regq` (
  `tracker_id` int(11) NOT NULL,
  `source_id` int(11) NOT NULL,
  `when_added` int(11) NOT NULL,
  `when_done` int(11)
);
--
--
--
DROP TABLE IF EXISTS `trackers`;
CREATE TABLE `trackers` (
  `scan_id` int(11) NOT NULL,
  `tracker_id` int(11) NOT NULL,
  `is_primary` BOOLEAN NOT NULL
);

         	      