## PikaChat

A simple chat for CloudAMQP made with Pika

## Message JSON

It sends and receives the following JSON and it won't show the message if it's missing any of the keys.
```
{
  user: "Andriy";
  timestamp: "2021-10-26T10:57:12";
  message: "Hello world!";
  source: "group" or "user"
}
```

## Screenshots
### Info screen

![Info screen](/imgs/Info.PNG?raw=true)

That's the input screen for the CloudAMQP URL, username and group name to join.

* You can manually input the URL or insert a .txt file with it inside
* The username acts as the consumer's queue name
* The group name acts as the consumer's exchange name

It'll also throw a popup error if it fails to connect to the provided URL, or if any of the boxes are empty.

### Chat box

![Chat box](/imgs/ChatBox.PNG?raw=true)

That's what the chat box looks like, it'll load the chat log on start and you send messages by typing at the bottom and pressing Enter.

It uses the source key in the JSON to paint the messages.
* Group messages are painted black 
* Private messages are painted purple. 

![Private box](/imgs/PrivateBox.PNG?raw=true)

If you'd like to send a private message, you can switch to the private chat option and set the user (queue) you'd like to send the message to.

It'll pop an error if you try to send a message without having set the user first.

It works by setting the exchange as "" while publishing the message to a routing key, that's why having to set a user first is mandatory.

### Message log
The message log will be named as username_exchangename.log and it'll look something like the following:
```
[
    {
        "user": "Andriy",
        "timestamp": "2021-11-07T16:25:51",
        "message": "Test message",
        "source": "group"
    },
    {
        "user": "Andriy",
        "timestamp": "2021-11-07T16:35:09",
        "message": "Private message",
        "source": "private"
    }
]
```

Currently it only saves received messages, so it won't log private messages you've sent, only ones that you've received.

Since it doesn't takes the CloudAMQP URL in consideration, it could end up saving chats from exchanges with the same name in the same log archive.
