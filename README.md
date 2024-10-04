# Termination character demo

Welcome to this _termination character demonstration_, a playground to learn about serial communication and ways to mark the end of messages exchanged between computers and serial devices like an Arduino, or instruments like an oscilloscope. In these demos, the _Client_ is your computer and the _Server_ is the external device. **Note:** it is recommended that you make your terminal wide enough to give all widgets some breathing room.

![screenshot of basic demo](https://raw.githubusercontent.com/NatuurkundePracticumAmsterdam/termchar-demo/refs/heads/main/docs/screenshots/screenshot-basic.png)

Play around for a bit! Some suggestions:

1. Start with the **Basic** demo: the server will autoreply if a complete message is received.
2. Try to send a message, with or without manually adding termination characters. Which characters are expected by the Server?
3. Set the termination characters in the _Write Termination Characters_ field of the client. Send some more messages. What happens?
4. Try to read messages. Are you required to specify read termination characters?
5. What happens if you do? Collect at least two replies and try to read them one by one.
6. Finally, you can try the **Advanced** demo. Here, you operate both client and server. Play around with various settings for the termination characters and read timeouts. What happens when you try to read, but there is no message yet received?
7. In the advanced demo, buffers have a finite size. If you try to overflow them, what happens?


## Details

The **basic** and **advanced** tabs are quite similar, but while the latter tab lets the user change everything, the former lets the user only change the client settings. The server settings mimic an Arduino running [bespoke VISA-compliant firmware](https://github.com/davidfokkema/arduino-visa-firmware). Commands sent to the Arduino should be terminated using a line feed, `\n`, while commands received from the device will be terminated by a carriage return followed by a line feed, `\r\n`. The basic demo will send a response back to the client each time a message is correctly received.


### The interface

The _Input Buffer_ is where commands you send end up before they are explicitly read by a device. They usually have a finite amount of space. The colour of the horizontal bar will indicate the amount of space that is left while the colour of the buffer _contents_ will indicate the presence of the correct termination characters. If the end of a message cannot be determined, the message is shown in red. If the end of the message is missing, the contents are tinted orange. On the other hand, if the message is correctly terminated, it will be displayed in a green colour while the termination characters themselves will be a blueish colour. You can type the termination characters explicitly at the end of each message, or you can set them once in the _Write Termination Characters_ widget. If you do that, each time you send a message the termination characters are added to the end automatically. Click the _Read_ button to read messages from the input buffer. If the _Read Termination Characters_ are not set correctly the application may keep waiting or display some gibberish at the end of each message. The _Application Log_ records all messages that are sent and received. The _Timeout_ on the advanced tab lets the user set read timeouts. If they are set to 0 the device will not stop reading before a complete message is received. If the timeout is set to _n_, the read will abort if there is no complete message received after _n_ seconds.


### Background

Computers and digital devices often need to communicate with each other. Over the course of many years, a plethora of communication standards and protocols have been developed. They usually involve exchanging some sort of messages. While reading and writing it is important to mark the end of a message so that the device will know when to stop reading and start processing. In many protocols this is usually done with one or two special characters, the so-called _termination characters_.

In simple protocols where short messages are exchanged the termination characters are usually one form of _end-of-line-characters_. Such characters were introduced in the early days of (electronic) typewriters, where a _carriage return_ would mean _return to the beginning of the line_ and a _line feed_ would mean _move to the next line_. A typewriter has a handle which you can use to move the carriage back to the start of the line and, simultaneously, feed the paper to move to the next line. Such control characters survive to this day to mark the end of lines in text files on computers. A carriage return is usually denoted `\r` in languages like C and Python, and a line feed is similarly denoted as `\n`. DOS-derived operating systems like Windows use a carriage return + line feed `\r\n` as a line ending, while Unix-derived operating systems like macOS and Linux only use line feed `\n` for line endings. To this day, this can confuse users when they exchange text files between different OSes.
