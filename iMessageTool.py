import sqlite3
import os.path
import datetime
import time
import sys
from prettytable import PrettyTable
import textwrap
from os.path import expanduser

HOME = expanduser("~")
PATH = HOME + "/Library/Messages/"
CONTACTS_PATH = PATH + "contacts.db"
MESSAGE_PATH = PATH + "chat.db"

def main():
    print("\nThe iMessage Tool is launching.\n")
    run = True
    while run:
        command = input("\nEnter the number of the option you would like:\n1. Create a Contact\n2. Use an Existing Contact\n3. Delete an Existing Contact\n\nEnter 'Exit' or 'exit' if you would like to end the program.\n\n")
        if command=='1':
            run = False
            name = input("\nEnter the name of the contact you would like to enter.\n")
            phone_number = input("Enter the phone number of the contact you would like to enter.\n")
            create_contact(name, phone_number)
        elif command=='2':
            run = False
            name = input("\nEnter the name of the contact whose messages you would like to access.\n")
            run = existing_contact(name)
        elif command=='3':
            run = False
            name = input("\nEnter the name of the contact who you would like to delete.\n")
            delete_contact(name)
        elif command=='Exit' or command=='exit':
            sys.exit("\nThe iMessage Tool is exiting.\n")
        else:
            print("\nInvalid command entered. Please try again. Only enter the number of the command you would like.\n")

def existing_contact(name):
    phone_number = retrieve_contact(name)
    run = True
    while run:
        command = input("\nYou are using the following contact: {} - {}.\n\nEnter the number of the option you would like:\n1. Retrieve Messages in the Command Line\n2. Export Messages to another Service\n\nEnter 'Return' or 'return' if you would like to create a contact, use another existing contact, or delete a contact.\nEnter 'Exit' or 'exit' if you would like to end the program.\n\n".format(name, phone_number))
        if command=='1':
            run = False
            handle_id = retrieve_handle(phone_number)
            retrieve_texts(name, handle_id)
        elif command=='2':
            run = True
            print("Export options are currently unavailable. Please try again.")
        elif command=='Return' or command=='return':
            return True
        elif command=='Exit' or command=='exit':
            sys.exit("\nThe iMessage Tool is exiting.\n")
        else:
            print("\nInvalid command entered. Please try again. Only enter the number of the command you would like.\n")

def retrieve_texts(name, handle_id):
    run = True
    while run:
        command = input("\nYou have chosen retrieve Messages for {} in the command line.\n\nEnter the number of the option you would like:\n1. Retrieve all Messages\n2. Retrieve Messages from a Specific Date\n3. Retrieve Messages from a Date Range\n\nEnter 'Return' or 'return' if you would like to Export Messages to another Service\nEnter 'Exit' or 'exit' if you would like to end the program.\n\n".format(name))
        if command=='1':
            run = False
            retrieve_all_texts(name, handle_id)
        elif command == '2':
            run = False
            date = input("\nPlease enter the date of the Messages you would like to retrieve in the following format (MM/DD/YYYY).\n")
            retrieve_texts_by_date(name, handle_id, date)
        elif command == '3':
            run = False
            date1 = input("\nPlease enter the start date of the date range for the Messages you would like to retrieve in the following format (MM/DD/YYYY).\n")
            date2 = input("\nPlease enter the end date of the date range for the Messages you would like to retrieve in the following format (MM/DD/YYYY).\n")
            retrieve_texts_by_date_range(name, handle_id, date1, date2)
        elif command=='Return' or command=='return':
            return True
        elif command=='Exit' or command=='exit':
            sys.exit("\nThe iMessage Tool is exiting.\n")
        else:
            print("\nInvalid command entered. Please try again. Only enter the number of the command you would like.\n")

def retrieve_all_texts(name, handle_id):
    conn = sqlite3.connect(MESSAGE_PATH)
    c = conn.cursor()
    params = (handle_id,)
    c.execute("select is_from_me, text, date from message where handle_id=?", params)
    pretty_print_texts(c.fetchall(), name)

def retrieve_texts_by_date(name, handle_id, date):
    time_offset = -time.timezone
    month = int(date.split('/')[0])
    day = int(date.split('/')[1])
    year = int(date.split('/')[2])
    dt = datetime.datetime(year, month, day, 0, 0, 0)
    tmp = datetime.datetime(2001,1,1,0,0)
    timestamp_b = int((dt-tmp).total_seconds()) - time_offset 
    timestamp_e = timestamp_b + 86400

    conn = sqlite3.connect(MESSAGE_PATH)
    c = conn.cursor()
    params = (handle_id, timestamp_b, timestamp_e)
    c.execute("select is_from_me, text, date from message where handle_id=? and date between ? and ?", params)
    pretty_print_texts(c.fetchall(), name)

def retrieve_texts_by_date_range(name, handle_id, date1, date2):
    time_offset = -time.timezone

    month1 = int(date1.split('/')[0])
    day1 = int(date1.split('/')[1])
    year1 = int(date1.split('/')[2])

    month2 = int(date2.split('/')[0])
    day2 = int(date2.split('/')[1])
    year2 = int(date2.split('/')[2])

    dt1 = datetime.datetime(year1, month1, day1, 0, 0, 0)
    dt2 = datetime.datetime(year2, month2, day2, 23, 59, 59)
    tmp = datetime.datetime(2001,1,1,0,0)
    timestamp_b = int((dt1-tmp).total_seconds()) - time_offset
    timestamp_e = int((dt2-tmp).total_seconds()) - time_offset

    conn = sqlite3.connect(MESSAGE_PATH)
    c = conn.cursor()
    params = (handle_id, timestamp_b, timestamp_e)
    c.execute("select is_from_me, text, date from message where handle_id=? and date between ? and ?", params)
    pretty_print_texts(c.fetchall(), name)

def pretty_print_texts(texts, name):
    messages = PrettyTable()
    messages.field_names = ['Date', 'Sender', 'Message']
    for text in texts:
        if text[0]:
            sender = "Me"
        else:
            sender = name
        date = time_stamp_conversion(text[2])
        message = textwrap.fill(text=text[1], width=50)
        messages.add_row([date, sender, message])
    print(messages)

def time_stamp_conversion(timestamp):
    timezone_offset = -time.timezone
    timestamp = timestamp + timezone_offset

    daylight_savings = time.localtime().tm_isdst
    if daylight_savings:
        daylight_offset = 3600
        timestamp = timestamp + daylight_offset

    d = datetime.datetime.strptime("01-01-2001", "%m-%d-%Y")
    date = (d + datetime.timedelta(seconds=timestamp)).strftime("%b %d, %Y %H:%M:%S")
    return date 

def retrieve_handle(phone):
    phone = "+1" + str(phone)
    conn = sqlite3.connect(MESSAGE_PATH)
    c = conn.cursor()
    params = (phone, 'iMessage')
    c.execute("select rowid from handle where id=? and service=?", params)
    return c.fetchone()[0]

def create_contact(name, phone_number):
    conn = sqlite3.connect(CONTACTS_PATH)
    c = conn.cursor()
    c.execute("create table if not exists Contacts (name text not null unique, number text not null unique)")

    try:
        params = (name, phone_number)
        c.execute("insert into Contacts values (?, ?);", params)
        conn.commit()
        print("{} has been entered into the Contacts database with the number: {}".format(name, phone_number))
    except sqlite3.IntegrityError:
        print("\nName({}) OR Phone Number({}) already exists in the Contacts database".format(name, phone_number))

def retrieve_contact(name):
    conn = sqlite3.connect(CONTACTS_PATH)
    c = conn.cursor()
    params = (name,)
    c.execute("select number from Contacts where name=?", params)
    result = c.fetchone()
    if result is None:
        sys.exit("{} was not found in the Contacts database.".format(name))
    return result[0]

def delete_contact(name):
    retrieve_contact(name)
    conn = sqlite3.connect(CONTACTS_PATH)
    c = conn.cursor()
    params = (name,)
    c.execute("delete from Contacts where name=?", params)
    conn.commit()
    print("{} has been deleted from the Contacts database".format(name))

if __name__=="__main__":
    main()
