![highlevel](/images/highlevel.png)

# set up java enviroment
```
yum install java-1.8.0-openjdk
```

# set up Kafka

To install and set up Kafka , please follow the Kafka quick start guide https://kafka.apache.org/quickstart
```
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties

bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
```
in order for remote server to produce to the local kafka broker, the broker ip needs to be advertised by modifying the config/server.properties
```
vi config/server.properties

advertised.listeners=PLAINTEXT://[server_ip]:9092
```

# fluentd output to kafka

install the plugin
```
[root@linux1 ~]# td-agent-gem install fluent-plugin-kafka
Fetching: fluent-plugin-kafka-0.12.1.gem (100%)
Successfully installed fluent-plugin-kafka-0.12.1
Parsing documentation for fluent-plugin-kafka-0.12.1
Installing ri documentation for fluent-plugin-kafka-0.12.1
Done installing documentation for fluent-plugin-kafka after 0 seconds
```

configure fluentd:
```
[root@linux1 ~]# vi /etc/td-agent/td-agent.conf

<source>
  @type syslog
  port 1514
  tag system
</source>


<match {system.**}>
  @type copy
  <store>
    @type kafka2
    brokers 10.49.64.214:9092
    use_event_time true
    <buffer eventService>
      @type file
      path /var/log/td-agent/buffer/td
      flush_interval 3s
    </buffer>
    <format>
      @type json
    </format>
    topic_key eventService
    default_topic eventService
  </store>
  <store>
    @type stdout
  </store>
</match>

note: in my lab, the "topic_key" does not work, I have to use "default_topic"
```

check fluentd log:
```
[root@linux1 ~]# tail -f /var/log/td-agent/td-agent.log
2019-11-21 11:06:11 -0500 [info]: gem 'fluentd' version '0.14.25'
2019-11-21 11:06:11 -0500 [info]: adding match pattern="{system.**}" type="copy"
2019-11-21 11:06:11 -0500 [info]: #0 brokers has been set: ["10.49.64.214:9092"]
2019-11-21 11:06:11 -0500 [info]: adding source type="syslog"
2019-11-21 11:06:11 -0500 [info]: #0 starting fluentd worker pid=26625 ppid=26620 worker=0
2019-11-21 11:06:11 -0500 [info]: #0 initialized kafka producer: fluentd
2019-11-21 11:06:11 -0500 [info]: #0 listening syslog socket on 0.0.0.0:1514 with udp
2019-11-21 11:06:11 -0500 [info]: #0 fluentd worker is now running worker=0
2019-11-21 08:05:59.000000000 -0500 system.daemon.info: {"host":"vmx101","ident":"cscript","message":"RPM_TEST_RESULTS: test-owner=northstar-ifl test-name=ge-0/0/5.0 loss=0 min-rtt=1 max-rtt=42 avgerage-rtt=12 jitter=82.364"}
2019-11-21 08:05:59.000000000 -0500 system.daemon.info: {"host":"vmx101","ident":"cscript","message":"RPM_TEST_RESULTS: test-owner=northstar-ifl test-name=ge-0/0/6.0 loss=0 min-rtt=8 max-rtt=14 avgerage-rtt=19.67 jitter=29.2"}
```

manually check if events are received from fluentd on kafka
```
root@ubuntu:~/kafka_2.12-2.3.0# bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic eventService --from-beginning
{"host":"vmx101","ident":"cscript","message":"RPM_TEST_RESULTS: test-owner=northstar-ifl test-name=ge-0/0/6.0 loss=0 min-rtt=8 max-rtt=14 avgerage-rtt=19.67 jitter=29.2"}
{"host":"vmx101","ident":"cscript","message":"RPM_TEST_RESULTS: test-owner=northstar-ifl test-name=ge-0/1/1.0 loss=0 min-rtt=67 max-rtt=67 avgerage-rtt=35.5 jitter=77.987"}
```

# healthbot output to kafka
follow https://damianoneill.github.io/healthbot/docs/kafka on how to configure healthbot to send notificatio to kafka

manually check if events are received:
```
root@ubuntu:~/kafka_2.12-2.3.0# bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic eventService --from-beginning

{"device-id": "vmx101", "group": "group_all", "keys": {"_instance_id": "[\"interface-status\"]", "_playbook_name": "interface-status", "interface-name": "ge-0/1/1"}, "message": "ge-0/1/1 op state UP", "rule": "interface_status", "severity": "normal", "topic": "external", "trigger": "op-down"}
```
