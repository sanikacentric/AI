# Stage 1: Use confluentinc/cp-kafka to copy Kafka libraries
FROM confluentinc/cp-kafka:latest as kafka-libs

# Create the directory for Kafka JAR files in a location with appropriate permissions
RUN mkdir -p /tmp/kafka/libs

# Copy Kafka client libraries from the identified paths
RUN cp /usr/share/java/kafka/* /tmp/kafka/libs/ || cp /usr/share/java/cp-base-new/* /tmp/kafka/libs/

# Stage 2: Use openjdk:11 as the base image for JMeter
FROM openjdk:11

# Install wget and curl
RUN apt-get update && apt-get install -y wget curl && apt-get clean

# Install JMeter
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.4.1.tgz -O /tmp/apache-jmeter-5.4.1.tgz
RUN tar -xzf /tmp/apache-jmeter-5.4.1.tgz -C /opt/
RUN ln -s /opt/apache-jmeter-5.4.1 /opt/jmeter

# Create the directory for Kafka JAR files in JMeter
RUN mkdir -p /opt/jmeter/lib/ext

# Copy Kafka JAR files from the first stage
COPY --from=kafka-libs /tmp/kafka/libs/* /opt/jmeter/lib/ext/

# Download additional Kafka JAR files and dependencies
RUN curl -L -o /opt/jmeter/lib/ext/kafka-clients-3.3.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.1/kafka-clients-3.3.1.jar && \
    curl -L -o /opt/jmeter/lib/ext/lz4-1.9.2.jar https://repo1.maven.org/maven2/org/lz4/lz4/1.9.2/lz4-1.9.2.jar && \
    curl -L -o /opt/jmeter/lib/ext/snappy-java-1.1.8.4.jar https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.8.4/snappy-java-1.1.8.4.jar

# Copy additional JARs if any
COPY jars/ /opt/jmeter/lib/ext/

# Copy the JMeter test plan
COPY testplan12.jmx /opt/jmeter/testplan12.jmx

# Verify the JAR files
RUN ls -la /opt/jmeter/lib/ext/

# Set the entry point to run JMeter
ENTRYPOINT ["/opt/jmeter/bin/jmeter", "-n", "-t", "/opt/jmeter/testplan12.jmx", "-l", "/opt/jmeter/logs/testplan.log"]
