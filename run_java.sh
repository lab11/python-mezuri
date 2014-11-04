#!/usr/bin/env bash

# It blows my mind that people find _this_ acceptible

if [ -n "$1" ]; then
	DIR="$1"
else
	DIR=/Users/ppannuto/Documents/workspace/PytonTestProj
	echo "Using default DIR=$DIR"
	echo "To override path, pass path as argument to this script"
fi

# /Library/Java/JavaVirtualMachines/jdk1.7.0_45.jdk/Contents/Home/bin/java

java -Dfile.encoding=US-ASCII -classpath $DIR/bin:$DIR/libs/py4j0.8.2.1.jar:$DIR/libs/commons-lang-2.3.jar:$DIR/libs/geronimo-jaxrs_1.1_spec-1.0.jar:$DIR/libs/gson-2.1.jar:$DIR/libs/slf4j-api-1.6.1.jar:$DIR/libs/slf4j-simple-1.6.1.jar:$DIR/libs/wink-1.4.jar:$DIR/libs/wink-client-1.4.jar:$DIR/libs/wink-common-1.4.jar:$DIR/libs/wink-json-provider-1.4.jar:$DIR/libs/wink-server-1.4.jar:$DIR/libs/commons-codec-1.6.jar:$DIR/libs/commons-logging-1.1.3.jar:$DIR/libs/fluent-hc-4.3.5.jar:$DIR/libs/httpclient-4.3.5.jar:$DIR/libs/httpclient-cache-4.3.5.jar:$DIR/libs/httpcore-4.3.2.jar:$DIR/libs/httpmime-4.3.5.jar:$DIR/libs/jackson-annotations-2.4.1.jar:$DIR/libs/jackson-core-2.4.1.1.jar:$DIR/libs/jackson-databind-2.4.1.3.jar:$DIR/libs/jackson-dataformat-xml-2.4.1.jar:$DIR/libs/jackson-jaxrs-base-2.4.1.jar:$DIR/libs/jackson-jaxrs-json-provider-2.4.1.jar:$DIR/libs/jackson-jaxrs-xml-provider-2.4.1.jar:$DIR/libs/jackson-module-jaxb-annotations-2.4.1.jar:$DIR/libs/aggregate-rest-interface-2014-07-15.jar:$DIR/libs/json-20140107.jar:$DIR/libs/wink-0.1-SNAPSHOT.jar org.opendatakit.py.example.EntryPoint
