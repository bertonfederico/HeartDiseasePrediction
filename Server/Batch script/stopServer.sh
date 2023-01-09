#!/bin/bash 

#STOP HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh

pkill -f ../lib/openscoring-server-executable-2.1.1.jar