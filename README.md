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
Group messages are painted black while private messages are painted purple.

![Private box](/imgs/PrivateBox.PNG?raw=true)

If you'd like to send a private message, you can switch to the private chat option and set the user (queue) you'd like to send the message to.
It'll pop an error if you try to send a message without having set the user first.
It works by setting the exchange as "" while publishing the message to a routing key, that's why having to set a user first is mandatory.