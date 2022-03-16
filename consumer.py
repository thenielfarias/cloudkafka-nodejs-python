import sys
import os

from confluent_kafka import Consumer, KafkaException, KafkaError

from dotenv import load_dotenv
load_dotenv()

def createConsumer():

    topics = [f'{os.getenv("CLOUDKARAFKA_TOPIC_PREFIX")}default']

    conf = {
        'bootstrap.servers': os.getenv('CLOUDKARAFKA_BROKERS'),
        'group.id': 'cloudkarafka-consumer-py',
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'},
        'security.protocol': 'SASL_SSL',
	'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': os.getenv('CLOUDKARAFKA_USERNAME'),
        'sasl.password': os.getenv('CLOUDKARAFKA_PASSWORD')
    }

    c = Consumer(conf)
    c.subscribe(topics)
    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                print(msg.value())

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    c.close()

createConsumer()