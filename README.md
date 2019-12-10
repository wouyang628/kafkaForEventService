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

healthbot rule example:
```
set iceberg topic external rule interface_status keys element-name
set iceberg topic external rule interface_status sensor interface open-config sensor-name /interfaces
set iceberg topic external rule interface_status sensor interface open-config frequency 30s
set iceberg topic external rule interface_status field admin-status sensor interface path /interfaces/interface/state/admin-status
set iceberg topic external rule interface_status field admin-status type string
set iceberg topic external rule interface_status field element-name sensor interface where "/interfaces/interface/@name =~ /{{interface-name-variable}}/"
set iceberg topic external rule interface_status field element-name sensor interface path "/interfaces/interface/@name"
set iceberg topic external rule interface_status field element-name type string
set iceberg topic external rule interface_status field op-status sensor interface path /interfaces/interface/state/oper-status
set iceberg topic external rule interface_status field op-status type string
set iceberg topic external rule interface_status trigger interface_down frequency 5s
set iceberg topic external rule interface_status trigger interface_down term Term_1 when matches-with "$op-status" DOWN
set iceberg topic external rule interface_status trigger interface_down term Term_1 then status color red
set iceberg topic external rule interface_status trigger interface_down term Term_1 then status message "$element-name op state DOWN"
set iceberg topic external rule interface_status trigger interface_down term Term_2 when matches-with "$op-status" UP
set iceberg topic external rule interface_status trigger interface_down term Term_2 then status color green
set iceberg topic external rule interface_status trigger interface_down term Term_2 then status message "$element-name op state DOWN"
set iceberg topic external rule interface_status variable interface-name-variable value ge.*
set iceberg topic external rule interface_status variable interface-name-variable type string
```
```
set iceberg topic device.cpu rule check-system-cpu keys element_name
set iceberg topic device.cpu rule check-system-cpu synopsis "Routing engine CPU analyzer"
set iceberg topic device.cpu rule check-system-cpu description "Collects system RE CPU statistics periodically and notifies anomalies when CPU utilization exceeds threshold"
set iceberg topic device.cpu rule check-system-cpu function subtract description "Subtracts cpu-idle% from 100 to get CPU used percent"
set iceberg topic device.cpu rule check-system-cpu function subtract path system-sensors.py
set iceberg topic device.cpu rule check-system-cpu function subtract method subtract
set iceberg topic device.cpu rule check-system-cpu function subtract argument threshold mandatory
set iceberg topic device.cpu rule check-system-cpu sensor components synopsis "system components open-config sensor definition"
set iceberg topic device.cpu rule check-system-cpu sensor components description "/components open-config sensor to collect telemetry data from network device"
set iceberg topic device.cpu rule check-system-cpu sensor components open-config sensor-name /components/
set iceberg topic device.cpu rule check-system-cpu sensor components open-config frequency 60s
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization formula user-defined-function function-name subtract
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization formula user-defined-function argument threshold "$re-cpu-utilization-oc"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization type integer
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization description "Derives used percentage from idle CPU utilization"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-high-threshold constant value "{{re-cpu-high-threshold}}"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-high-threshold type integer
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-high-threshold description "RE CPU utilization high threshold"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-low-threshold constant value "{{re-cpu-low-threshold}}"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-low-threshold type integer
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-low-threshold description "RE CPU utilization low threshold"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-oc sensor components where "/components/component/properties/property/@name == 'cpu-utilization-idle'"
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-oc sensor components path /components/component/properties/property/state/value
set iceberg topic device.cpu rule check-system-cpu field re-cpu-utilization-oc description "RE CPU idle utilization"
set iceberg topic device.cpu rule check-system-cpu field element_name sensor components where "/components/component/@name =~ /^Routing Engine[{{re-slot-no}}]*$/"
set iceberg topic device.cpu rule check-system-cpu field element_name sensor components path "/components/component/@name"
set iceberg topic device.cpu rule check-system-cpu field element_name description "RE name to monitor"
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization synopsis "Routing engine CPU KPI"
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization description "Sets health based on increase in RE CPU utilization"
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization frequency 60s
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-abnormal when greater-than-or-equal-to "$re-cpu-utilization" "$re-cpu-utilization-high-threshold" time-range 5m
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-abnormal when greater-than-or-equal-to "$re-cpu-utilization" "$re-cpu-utilization-high-threshold" all
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-abnormal then status color red
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-abnormal then status message "$element_name CPU utilization($re-cpu-utilization) exceeds high threshold($re-cpu-utilization-high-threshold)"
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-middle when greater-than-or-equal-to "$re-cpu-utilization" "$re-cpu-utilization-low-threshold" time-range 5m
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-middle when greater-than-or-equal-to "$re-cpu-utilization" "$re-cpu-utilization-low-threshold" all
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-middle then status color yellow
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term is-re-cpu-utilization-middle then status message "$element_name CPU utilization($re-cpu-utilization) in medium range"
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term re-cpu-utilization-normal then status color green
set iceberg topic device.cpu rule check-system-cpu trigger re-cpu-utilization term re-cpu-utilization-normal then status message "$element_name CPU utilization($re-cpu-utilization) is normal"
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-high-threshold value 80
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-high-threshold description "RE CPU utilization high threshold: Utilization increase between metrics, before we report anomaly"
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-high-threshold type int
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-low-threshold value 50
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-low-threshold description "RE CPU utilization low threshold: Utilization increase between metrics, before we report anomaly"
set iceberg topic device.cpu rule check-system-cpu variable re-cpu-low-threshold type int
set iceberg topic device.cpu rule check-system-cpu variable re-slot-no value 0-1
set iceberg topic device.cpu rule check-system-cpu variable re-slot-no description "Routing engine numbers to monitor, regular expression, e.g. '0'"
set iceberg topic device.cpu rule check-system-cpu variable re-slot-no type string
```


# set up Kibana to visualize the data

create Index Pattern
![KibanaIndexPattern](/images/KibanaIndexPattern.png)

Data Dicovery:
![kibanaDiscovery](/images/kibanaDiscovery.png)


# SMTP

To enable sending email , please configure SNMP following https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-16-04

e.g.
```
import smtplib
sender = 'event_service'
receivers = ['']
message = """From: From Event Service
To: To You
Subject: Event Cannot be handled

Event Cannot be handled.
Error Information:
{}
""".format(event)
smtpObj = smtplib.SMTP('localhost')
smtpObj.sendmail(sender, receivers, message)
```
