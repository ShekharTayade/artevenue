#!/bin/bash
source /home/artevenue/artevenue/artevenueenv/bin/activate
python /home/artevenue/website/manage.py send_carts_with_order_without_payment > /home/artevenue/website/send_carts_log

