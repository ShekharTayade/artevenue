#!/bin/bash
source /home/artevenue/artevenue/artevenueenv/bin/activate
/home/artevenue/artevenue/artevenueenv/bin/python /home/artevenue/website/manage.py send_customer_review_emails > /home/artevenue/website/send_customer_review_emails_log
