# Telegram bot for investing 📊 🏭

This project is a telegram bot who send message to a users when detects variations on the stocks. 
For this, users must register with the bot through the commands enabled directly from the telegram application.
It is aimed at users who wish to invest in the stock market and want to receive notifications on their cell phone.

# How to use

First create a telegram bot using the bot father on telegram. It give you a token for the json file. Then run the bot, send the \start command, and add the companies you want to monitor.

# Commands availables 📉

* \start -> register user
* \add + "company" -> add company to the current user. Example: \add apple
* \rem + "company" -> same for add, but remove
* \update -> refresh list of company and their status
* \help -> send commands availables

# Pre requisites 📋

The project use SQLAlchemy with sqlite and python 3.7.3. For more details, see requirements.txt.

# To do 🚀

* The bot only returns the daily technical parameters. It cannot be configured directly by the user (but yes, editing from db).
* Add more functionalities.
* Translate to english the bot (only spanish version for now).
* Make more documentation.

# Versión 📌

Versión 1.0

# Author ✒

* Javier Carugno
* Electronic engineering student at National Technological University, Argentina
* javiercarugno@gmail.com
