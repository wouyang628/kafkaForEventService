![highlevel](/images/highlevel.png)

# kafkaScalaEventSubscription

To install and set up Kafka , please follow the Kafka quick start guide https://kafka.apache.org/quickstart
```
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties

bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
```


# set up java enviroment
```
yum install java-1.8.0-openjdk
```


in order for remote server to produce to the local kafka broker, the broker ip needs to be advertised by modifying the config/server.properties
```
vi config/server.properties

advertised.listeners=PLAINTEXT://[server_ip]:9092
```

# fluentd output to kafka

```
[root@linux1 ~]# td-agent-gem install fluent-plugin-kafka
Fetching: fluent-plugin-kafka-0.12.1.gem (100%)
Successfully installed fluent-plugin-kafka-0.12.1
Parsing documentation for fluent-plugin-kafka-0.12.1
Installing ri documentation for fluent-plugin-kafka-0.12.1
Done installing documentation for fluent-plugin-kafka after 0 seconds
```
