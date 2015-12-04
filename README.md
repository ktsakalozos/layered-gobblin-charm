## Overview

"Gobblin is a universal data ingestion framework for extracting, transforming,
and loading large volume of data from a variety of data sources, 
e.g., databases, rest APIs, FTP/SFTP servers, filers, etc., onto Hadoop."
from the [Gobblin wiki](https://github.com/linkedin/gobblin/wiki) 

## Usage
This charm leverages our pluggable Hadoop model with the `hadoop-plugin`
interface. This means that you will need to deploy a base Apache Hadoop cluster
to run Gobblin. The suggested deployment method is to use the
[apache-analytics-sql](https://jujucharms.com/apache-analytics-sql/)
bundle. This will deploy the Apache Hadoop platform with a single Gobblin
unit that communicates with the cluster by relating to the
`apache-hadoop-plugin` subordinate charm:

    juju deploy apache-hadoop-hdfs-master hdfs-master
    juju deploy apache-hadoop-yarn-master yarn-master
    juju deploy apache-hadoop-compute-slave compute-slave
    juju deploy apache-hadoop-plugin plugin
    juju deploy gobblin

    juju add-relation yarn-master hdfs-master
    juju add-relation compute-slave yarn-master
    juju add-relation compute-slave hdfs-master
    juju add-relation plugin yarn-master
    juju add-relation plugin hdfs-master
    juju add-relation gobblin plugin


## Testing the deployment

### Smoke test Gobblin
From the Gobblin unit, start the Demo ingestion job as the `gobblin` user:

    juju ssh gobblin/0

TODO: Edit from here on
    sudo su gobblin -c .....

From the Hive console, verify sample commands execute successfully:

    show databases;
    create table test(col1 int, col2 string);
    show tables;
    quit;

Exit from the Hive unit:

    exit

### Smoke test HiveServer2
From the Hive unit, start the Beeline console as the `hive` user:

    juju ssh hive/0
    sudo su hive -c beeline

From the Beeline console, connect to HiveServer2 and verify sample commands
execute successfully:

    !connect jdbc:hive2://localhost:10000 hive password org.apache.hive.jdbc.HiveDriver
    show databases;
    create table test2(a int, b string);
    show tables;
    !quit

Exit from the Hive unit:

    exit


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
