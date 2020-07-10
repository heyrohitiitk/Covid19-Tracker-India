# Covid19-Tracker-India

## The Message Content will look like this in your gmail
![Gmail Page](https://i.ibb.co/hCSLwSS/mail-page.jpg)

## Features
- Get quick notification on gmail.
   -  New Corona Cases happening in india.
   -  Corona Stats related to state you want.
   -  How many cases increased from previous day?.
   -  A donut graph for quick visualisation.
- Get corona status of any state you want.
- You can also see a beautiful bar chart of total cases per state.
- The source of data is Official Government Site ([check here](https://mohfw.gov.in/)).
- It is ROBUST.
   -  On script failure or any other error you get information.
   -  You have log file [check 'test.log'] to see more details about error.

## Installation
- Python 3.x is needed
- Generate a password for third party apps through google account
- Install dependencies by running,
```bash
    pip install prettytable
    pip install beautifulsoup4
    pip install requests
    pip install pandas
    pip install matplotlib
 ```
 
## How to Run the script?
- Just clone this repository
- you get a folder with name CoronaVirus
- Inside this folder make some changes
  -  open credentials.py file 
  -  put your gmail password generated for third part app
  -  put your gmail id on which you want notifications
- Now open command prompt in the same directory
- Run the following command
```bash
    python main.py --state "Delhi"
```
- you can replace Delhi with any other state
- When the script executes successfully you will get mail in your inbox
