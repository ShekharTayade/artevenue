#!/bin/bash
source /home/artevenue/artevenue/artevenueenv/bin/activate
/home/artevenue/artevenue/artevenueenv/bin/python /home/artevenue/website/manage.py send_order_status_communication > /home/artevenue/website/order_status_communication_log