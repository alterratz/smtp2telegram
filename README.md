# smtp2telegram
a little SMTP to telegram gateway which uses a telegram bot to send messages

I use it to forward HAProxy messages (which supports smtp alerts) to telegram but it can be used for any purpose. It can be started manually or as a systemd service (which uses screen to start the application). Most likely you'll have to adjust the user account under which it is is running as well as some file locations
