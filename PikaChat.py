import pika, os, threading
import time, json, datetime
from dateutil import parser
import PySimpleGUI as sg

text = ""
stopConsuming = False

# Read the key from a txt
file = open('key.txt', 'r')
amqpKey = file.readline()
file.close()

url = os.environ.get('CLOUDAMQP_URL', str(amqpKey))
params = pika.URLParameters(url)

def consume(outBox):
    def callback():
        if stopConsuming:
            channelConsumer.stop_consuming()
            connectionConsumer.close()
        else:
            connectionConsumer.call_later(1, callback)
            
    connectionConsumer = pika.BlockingConnection(params)
    connectionConsumer.call_later(1, callback)  
    channelConsumer = connectionConsumer.channel() # start a channel
    channelConsumer.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channelConsumer.queue_declare(queue=user_name) # Declare a queue
    channelConsumer.queue_bind(queue=user_name, exchange=exchange_name)
    
    def on_message(channel, method, properties, body):
        global text
        #print ('Messages in queue now %d' % res.method.message_count)
        #print("\nMessage: ")
        #print("\t%r: " % method)
        #print("\t%r: " % properties)
        
        data = json.loads(body)
        date = parser.parse(data['timestamp'])
        text += "[" + str(date) + "] <" + data['user'] + "> " + data['message'] + '\n'
        
        outBox.update(disabled = False)
        outBox.update(text)
        outBox.update(disabled = True)
        #print(text)
        
    
    channelConsumer.basic_consume(user_name, on_message, auto_ack=True)
    
    channelConsumer.start_consuming()

def publish(message):
    #global stopConsuming
    
    connectionPublisher = pika.BlockingConnection(params)
    channelPublisher = connectionPublisher.channel() # start a channel
    channelPublisher.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    #while not stopConsuming:
    #try:
        #try:
    message = input("Type anything to send a message: ")
    
    json_data["user"] = user_name
    json_data["timestamp"] = str(datetime.datetime.now().replace(microsecond=0).isoformat())
    json_data["message"] = message
    
    #channelPublisher.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(json_data))
    channelPublisher.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(json_data))


json_data = {}
user_name = ""
queue_name = ""
exchange_name = ""

#stopConsuming = False

# Username and group name UI
layout = [
            [sg.Text('Username', size=(8)), sg.In(key='USER')],
            [sg.Text('Group', size=(8), key='T1'), sg.In(key='GROUP')],
            [sg.Button('Ok'), sg.Button('Exit')]
         ]

window = sg.Window('PikaChat', layout)
while True:
    event, values = window.read()
    
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    elif event == 'Ok':
        user_name = values['USER']
        text = values['GROUP']
        
        if user_name == '':
            sg.popup_error("Username can't be empty!")
        elif text == '':
            sg.popup_error("Group name can't be empty!")
        else:
            exchange_name = text
            break
        
text = ""
window.close()

# To hide a section
def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0,0)))

# Chat box UI
section = [
           [sg.Text('User', size=(8)), sg.In(key='USER'),
            sg.Button('Set')]
          ]
layout = [
            [sg.Radio('Group chat', "RADIO1", default=True, enable_events=True, key='R1'),
             sg.Radio('Private chat', "RADIO1", enable_events=True, key='R2'),
             collapse(section, 'sec', False)],
            [sg.Multiline(size=(80, 20), key='OUT', disabled = True)],
            [sg.Input(size=(80), do_not_clear=False, key='IN'),
             sg.Button('Send', visible=False, bind_return_key=True)]
         ]


window = sg.Window('PikaChat', layout, default_element_size=(30, 2))

isGroupChat = False
outBox = window['OUT']

consumerThread = threading.Thread(target=consume, kwargs={'outBox':outBox})
publisherThread = threading.Thread(target=publish)

consumerThread.start()
#publisherThread.start()

while True:
    event, value = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        stopConsuming = True
        break
    #elif event == 'Send':
        
        """text += value['IN']+'\n'
        
        outBox.update(disabled = False)
        outBox.update(text)
        outBox.update(disabled = True)"""
    elif event == 'Set':
        queue_name = value['USER']

    
    if value['R2'] == True:
        isGroupChat = True
        window['sec'].update(visible=isGroupChat)
    else:
        isGroupChat = False
        window['sec'].update(visible=isGroupChat)

window.close()

"""consumerThread = threading.Thread(target=consume)
publisherThread = threading.Thread(target=publish)

consumerThread.start()
publisherThread.start()"""