import pika, os, threading, json, datetime, copy
from dateutil import parser
import PySimpleGUI as sg

def printToMultiline(multiline, json_data):
    #print(json_data)
    date = parser.parse(json_data['timestamp'])
    
    # [yyyy-mm-dd hh:mm:ss] <user_name> message
    text = "[" + str(date) + "] <" + json_data['user'] + "> " + json_data['message']
    
    # Multiline is disabled to prevent user from writing in it
    multiline.update(disabled = False)
    multiline.update(text, text_color_for_value=chooseColor(json_data['source']), append = True)
    multiline.update(disabled = True)

# Paints the message purple if it's private
def chooseColor(source):
    if source == 'private':
        return 'purple'
    else:
        return 'black'

def consume():
    # Pooling every 1 sec to see if consumer needs closing
    def callback():
        if stopConsuming:
            channelConsumer.stop_consuming()
            connectionConsumer.close()
            print("Consumer closed")
        else:
            connectionConsumer.call_later(1, callback)
            
    connectionConsumer = pika.BlockingConnection(params)
    connectionConsumer.call_later(1, callback)  
    channelConsumer = connectionConsumer.channel() # start a channel
    channelConsumer.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channelConsumer.queue_declare(queue=user_name) # Declare a queue
    channelConsumer.queue_bind(queue=user_name, exchange=exchange_name)
    
    def on_message(channel, method, properties, body):

        printToMultiline(outBox, json.loads(body))
         
    
    channelConsumer.basic_consume(user_name, on_message, auto_ack=True)
    
    channelConsumer.start_consuming()

# Read the key from a txt
file = open('key.txt', 'r')
amqpKey = file.readline()
file.close()

url = os.environ.get('CLOUDAMQP_URL', str(amqpKey))
params = pika.URLParameters(url)

json_list = []
json_data = {}
user_name = ""
queue_name = ""
exchange_name = ""
close_program = False
stopConsuming = False
firstTimeSetup = True

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
        close_program = True
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
        
window.close()

# To hide a section
def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0,0)))

# Section that's gonna be hidden
section = [
           [sg.Text('User', size=(8)), sg.In(key='USER'),
            sg.Button('Set')]
          ]
# Chat UI
layout = [
            [sg.Radio('Group chat', "RADIO1", default=True, enable_events=True, key='R1'),
             sg.Radio('Private chat', "RADIO1", enable_events=True, key='R2'),
             collapse(section, 'sec', False)],
            [sg.Multiline(size=(80, 20), key='OUT', disabled = True)],
            [sg.Input(size=(80), do_not_clear=False, key='IN'),
             sg.Button('Send', visible=False, bind_return_key=True)]
         ]

# If user cancelled/closed last window, ends the program
if close_program == False:
    window = sg.Window('PikaChat', layout, default_element_size=(30, 2))
    
    isGroupChat = True
    isUserSet = False
    outBox = window['OUT']
    
    consumerThread = threading.Thread(target=consume)
    
    connectionPublisher = pika.BlockingConnection(params)
    channelPublisher = connectionPublisher.channel() # start a channel
    channelPublisher.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    
    consumerThread.start()
    
    while True:
        event, value = window.read()
        
        if firstTimeSetup == True:
            # Reads the chat log
            with open('chatLog.log', 'r') as f:
                json_list = json.load(f)
                
            # Loads and prints json to box
            for item in json_list:
                json_data['user'] = item['user']
                json_data['timestamp'] = item['timestamp']
                json_data['message'] = item['message']
                json_data['source'] = item['source']
                
                printToMultiline(outBox, json_data)
            
            window.Refresh()
            firstTimeSetup = False
    
        # Stops consuming if user closed the chat
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            stopConsuming = True
            break
        # Send message
        elif event == 'Send':
            if isGroupChat == False and isUserSet == True or isGroupChat == True:
                message = value['IN']+'\n'
                
                json_data["user"] = user_name
                json_data["timestamp"] = str(datetime.datetime.now().replace(microsecond=0).isoformat())
                json_data["message"] = message
                
                # Group message
                if isGroupChat == True:
                    json_data["source"] = 'group'
                    channelPublisher.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(json_data))
                # Private message
                else:
                    json_data["source"] = 'private'
                    channelPublisher.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(json_data))
                    
                # Appends the json to the list
                json_list.append(copy.deepcopy(json_data))
                
            else:
                sg.popup_error("User can't be empty!")
        # Direct message
        elif event == 'Set':
            queue_name = value['USER']
            if queue_name == '':
                isUserSet = False
                sg.popup_error("User can't be empty!")
            else:
                isUserSet = True
                sg.popup("User set!")
    
        if value['R2'] == True:
            isGroupChat = False
            window['sec'].update(visible=not isGroupChat)
        else:
            isGroupChat = True
            window['sec'].update(visible=not isGroupChat)
    
    window.close()

# Writes the log

with open('chatLog.log', 'w') as f:
    json.dump(json_list, f, indent=4)
    
print("Closing program")