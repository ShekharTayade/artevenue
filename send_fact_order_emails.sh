#!/bin/bash
source /home/artevenue/artevenue/artevenueenv/bin/activate
python /home/artevenue/website/manage.py send_factory_order_emails > /home/artevenue/website/fact_order_emails_log

