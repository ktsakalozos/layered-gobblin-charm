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
From the Gobblin unit, start the wikipedia ingestion demo job as the `gobblin` user:

    juju ssh gobblin/0
    sudo su gobblin -c "gobblin-mapreduce.sh --conf wikipedia.pull --jars /usr/lib/gobblin/lib/gobblin-example.jar"

The output will be in hdfs under /gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id>

List and get the job output file in avro format.

    hdfs dfs -ls /gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id>
    hdfs dfs -get /gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id>/<Output.avro>

Transform to JSON.

    curl -O http://central.maven.org/maven2/org/apache/avro/avro-tools/1.7.7/avro-tools-1.7.7.jar
    java -jar avro-tools-1.7.7.jar tojson --pretty <Output.avro> > output.json

## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
