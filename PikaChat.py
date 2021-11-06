import pika, os, threading
import time, json, datetime
from dateutil import parser

json_data = {}
user_name = "Andriy"
queue_name = "Andriy"
exchange_name = "sisdis"
stopConsuming = False

# Read the key from a txt
file = open('amqpKey.txt', 'r')
amqpKey = file.readline()
file.close()

url = os.environ.get('CLOUDAMQP_URL', str(amqpKey))
params = pika.URLParameters(url)

def consume():
    
    def callback():
        if stopConsuming:
            print("Stopping consumption")
            channelConsumer.stop_consuming()
            connectionConsumer.close()
        else:
            connectionConsumer.call_later(1, callback)  
            
    connectionConsumer = pika.BlockingConnection(params)
    connectionConsumer.call_later(1, callback)  
    channelConsumer = connectionConsumer.channel() # start a channel
    channelConsumer.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channelConsumer.queue_declare(queue=queue_name) # Declare a queue
    channelConsumer.queue_bind(queue=queue_name, exchange=exchange_name)
    
    def on_message(channel, method, properties, body):
        #print ('Messages in queue now %d' % res.method.message_count)
        #print("\nMessage: ")
        #print("\t%r: " % method)
        #print("\t%r: " % properties)
        
        data = json.loads(body)
        date = parser.parse(data['timestamp'])
        print("[" + str(date) + "] <" + data['user'] + "> " + data['message'])
        
    
    channelConsumer.basic_consume(queue_name, on_message, auto_ack=True)
    
    channelConsumer.start_consuming()

def publish():
    global stopConsuming
    
    connectionPublisher = pika.BlockingConnection(params)
    channelPublisher = connectionPublisher.channel() # start a channel
    channelPublisher.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    while not stopConsuming:
        try:
            try:
                message = input("Type anything to send a message: ")
                
                json_data["user"] = user_name
                json_data["timestamp"] = str(datetime.datetime.now().replace(microsecond=0).isoformat())
                json_data["message"] = message
                
                channelPublisher.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(json_data))
                #channelPublisher.basic_publish(exchange=exchange_name, routing_key='', body=message)
                #channelPublisher.basic_publish(exchange=exchange_name, properties=properties , routing_key='', body=message)
            except EOFError:
                stopConsuming = True
                print("Ending the program")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing")


consumerThread = threading.Thread(target=consume)
publisherThread = threading.Thread(target=publish)

consumerThread.start()
publisherThread.start()