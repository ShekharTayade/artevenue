#!/bin/bash
source /home/artevenue/artevenue/artevenueenv/bin/activate
python /home/artevenue/website/manage.py send_customer_order_emails > /home/artevenue/website/cust_order_emails_log

