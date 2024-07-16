# Introduction

Welcome to this _termination character demonstration_, a playground to learn about serial communication and ways to mark the end of messages exchanged between computers and serial devices like an Arduino or instruments like an oscilloscope. In these demos, the _Client_ is your computer and the _Server_ is the external device. **Note:** it is recommended that you make your terminal wide enough to give all widgets some breathing room.

Play around for a bit! Some suggestions:

1. Start with the **Basic** demo: the server will autoreply if a complete message is received.
2. Try to send a message, with or without manually adding termination characters. Which characters are expected by the Server?
3. Set the termination characters in the _Write Termination Characters_ field. Send some more messages. What happens?
4. Try to read messages. Are you required to specify read termination characters?
5. What happens if you do?
6. Try the **Advanced** demo. Here, you can operate both client and server. Play around with various settings for the termination characters.