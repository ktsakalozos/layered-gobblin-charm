## Overview

"Gobblin is a universal data ingestion framework for extracting, transforming,
and loading large volume of data from a variety of data sources, 
e.g., databases, rest APIs, FTP/SFTP servers, filers, etc., onto Hadoop."
from the [Gobblin wiki](https://github.com/linkedin/gobblin/wiki) 

## Usage
This charm is uses the Hadoob base layer and the HDFS interface to pull its dependencies
and act as a client to a Hadoop namenode. Here is how to deploy the Hadoop infrastructure:

    juju quickstart apache-processing-mapreduce

Deploy the Gobblin charm and relate it to tha neme node:
 
    juju deploy gobblin
    juju add-relation gobblin plugin


## Testing the deployment

### Smoke test Gobblin
From the Gobblin unit, start the wikipedia ingestion demo job as the `gobblin` user:

    juju ssh gobblin/0
    cd /tmp
    sudo su gobblin -c "gobblin-mapreduce.sh --conf wikipedia.pull --jars /usr/lib/gobblin/lib/gobblin-example.jar"

The output will be in hdfs under /user/gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id> .
You can set the output directory through the ``--workdir`` flag. 

List and get the job output file(s) in avro format.

    hdfs dfs -ls /user/gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id>
    hdfs dfs -get /user/gobblin/work/job-output/gobblin/example/wikipedia/WikipediaOutput/<Your_Job_Id>/<Path_To_Output>/<Output.avro>

Transform to JSON.

    curl -O http://central.maven.org/maven2/org/apache/avro/avro-tools/1.7.7/avro-tools-1.7.7.jar
    java -jar avro-tools-1.7.7.jar tojson --pretty <Output.avro> > output.json

## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
