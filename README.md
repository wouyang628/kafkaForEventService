# kafkaScalaEventSubscription

To install and set up Kafka , please follow the Kafka quick start guide https://kafka.apache.org/quickstart

# set up java enviroment
```
yum install java-1.8.0-openjdk
```


in order for remote server to produce to the local kafka broker, the broker ip needs to be advertised by modifying the config/server.properties
```
vi config/server.properties

advertised.listeners=PLAINTEXT://[server_ip]:9092
```
