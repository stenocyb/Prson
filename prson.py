####################
# Author: stenocyb #
# Version: 1.0     #
# Platform: Any    #
####################

# Prson - A simple program which automates OSINT information gathering about a specific person

import os
import re
import time
from selenium import webdriver
import yaml
import argparse

# Constants
PROGRAM_VERSION = 1.0
ASCII_ART = '\n██████╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗\n██╔══██╗██╔══██╗██╔════╝██╔═══██╗████╗  ██║\n██████╔╝██████╔╝███████╗██║   ██║██╔██╗ ██║  v' + str(PROGRAM_VERSION) + '\n██╔═══╝ ██╔══██╗╚════██║██║   ██║██║╚██╗██║  by stenocyb\n██║     ██║  ██║███████║╚██████╔╝██║ ╚████║\n╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝\n'

# Variables
output_directory = os.getcwd() + os.path.sep + 'prson_output'
commands_file = os.getcwd() + os.path.sep + 'commands.txt'
websites_file = os.getcwd() + os.path.sep + 'websites.txt'

ask_questions = False

# Functions

## Checks if a string is an email or not, using regex
def is_email(email: str) -> bool:
    if(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)):
        return True
    else:
        return False
## Checks whether a string is a phone number or not, using regex 
def is_phone_number(phone_number: str) -> bool:
    pattern = re.compile('^[\dA-Z]{3}-[\dA-Z]{3}-[\dA-Z]{4}$', re.IGNORECASE)
    return pattern.match(phone_number) is not None or phone_number.replace('+', '').isnumeric()
 
## Displays a conclusive screen
def display_wrapup(start_time: float):
    print('- Execution time: %s seconds' % (time.time() - start_time))
    print('- Information has been saved to: ' + output_directory)

## Executes a list of commands stored in a file
def execute_commands(input_variable: str, commands_file: str, type: str):
    content = read_commands_file(commands_file, type)

    # Executes commands, replacing $INPUT with 'input' argument (email/phone/username) and $OUTPUT_DIR with output_directory variable
    for command in content:
        print(os.popen(str(command).replace('$INPUT', input_variable).replace('$OUTPUT_DIR', output_directory)).read())

## Fills out a form on a specific website using a browser
def fill_out_form(link: str, field_attribute: str, field_value: str, field_input: str, driver):
    driver.get(url=link)
    form = driver.find_element(field_attribute, field_value)
    form.send_keys(field_input)
    form.submit()

## Opens a new browser tab
def open_new_tab(driver):
    driver.execute_script('window.open('');')
    driver.switch_to.window(driver.window_handles[-1])

## Asks for an answer from a user concerning a yes-no question
def ask_polar_question(question: str) -> bool:
    answer = input(question + ' [Y/n]')

    if answer.lower() == 'n' or answer.lower() == 'no':
        return False
    else:
        return True

## Reads the commands file in YAML format, returns the contained commands sorted by type in a list
def read_commands_file(commands_file: str, type: str) -> list:
    commands = []

    try:
        with open(commands_file, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)

                for command in yaml_data:
                    if command['type'] == type:
                        commands.append(command['command'])
            except yaml.YAMLError as e:
                print('YAML Error: ' + str(e))
        
        return commands
    except FileNotFoundError as e:
        print('Error: Commands file ' + commands_file + ' not found.')
        exit(1)

## Reads the websites file in YAML format, returns its websites sorted by type in a list
def read_websites_file_and_visit(websites_file: str, type: str, input_str: str, web_driver: str) -> list:
    try:
        with open(websites_file, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)

                if web_driver == 'firefox':
                    driver = webdriver.Firefox()
                elif web_driver == 'chrome':
                    driver = webdriver.Chrome()
                elif web_driver == 'edge':
                    driver = webdriver.Edge()

                iteration_counter = 0
                website_counter = 0

                for website in yaml_data:
                    if website['type'] == type:
                        website_counter += 1

                for website in yaml_data:
                    if website['type'] == type:
                        iteration_counter += 1

                        if website['request_type'] == 'POST':
                            # Fills out form, replacing $INPUT in the websites file with the user given input string (email, number or username)
                            fill_out_form(link=website['url'], field_attribute=website['field_attribute'], field_value=website['field_value'], field_input=website['field_input'].replace('$INPUT', input_str), driver=driver)
                            
                            if iteration_counter < website_counter: 
                                time.sleep(250 / 1000) # Wait a quarter of a second before opening tab
                                open_new_tab(driver=driver)
                        elif website['request_type'] == 'GET':
                            # Visits website, replacing $INPUT in url of websites file with the user given input string (email, number or username)
                            driver.get(url=website['url'].replace('$INPUT', input_str))
                            
                            if iteration_counter < website_counter:
                                time.sleep(250 / 1000) # Wait a quarter of a second before opening tab
                                open_new_tab(driver=driver)
                
                # Prompt for browser exit
                input('Press Enter to continue...\n')
                driver.quit()
            except yaml.YAMLError as e:
                print('YAML Error: ' + str(e))
    except FileNotFoundError as e:
        print('Error: Websites file ' + websites_file + ' not found.')
        exit(1)


## Looks up an email address
def lookup_email(email: str, only_commands: bool, only_websites: bool, browser: str):
    if ask_questions:
        if not only_websites:
            if ask_polar_question('Do you want to execute system commands in order to perform an OSINT lookup of the provided email address?'):
                execute_commands(email, commands_file, 'email')

                if not only_commands:
                    if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                        read_websites_file_and_visit(websites_file, 'email', email, browser)
        else:
            if not only_commands:
                if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                    read_websites_file_and_visit(websites_file, 'email', email, browser)
            else:
                print('Error: Conflicting command line options, -w and -c can not be used together.')
                exit(1)
    else:
        if only_commands:
            execute_commands(email, commands_file, 'email')
        elif only_websites:
            read_websites_file_and_visit(websites_file, 'email', email, browser)
        elif not only_commands and not only_websites:
            execute_commands(email, commands_file, 'email')
            read_websites_file_and_visit(websites_file, 'email', email, browser)
        else:
            print('Error: Conflicting command line options, -w and -c can not be used together.')
            exit(1)

## Looks up a telephone number
def lookup_phone_number(number: str, only_commands: bool, only_websites: bool, browser: str):
    if ask_questions:
        if not only_websites:
            if ask_polar_question('Do you want to execute system commands in order to perform an OSINT lookup of the provided telephone number?'):
                execute_commands(number, commands_file, 'phone')

                if not only_commands:
                    if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                        read_websites_file_and_visit(websites_file, 'phone', number, browser)
        else:
            if not only_commands:
                if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                    read_websites_file_and_visit(websites_file, 'phone', number, browser)
            else:
                print('Error: Conflicting command line options, -w and -c can not be used together.')
                exit(1)
    else:
        if only_commands:
            execute_commands(number, commands_file, 'phone')
        elif only_websites:
            read_websites_file_and_visit(websites_file, 'phone', number, browser)
        elif not only_commands and not only_websites:
            execute_commands(number, commands_file, 'phone')
            read_websites_file_and_visit(websites_file, 'phone', number, browser)
        else:
            print('Error: Conflicting command line options, -w and -c can not be used together.')
            exit(1)

## Looks up a username
def lookup_username(username: str, only_commands: bool, only_websites: bool, browser: str):
    if ask_questions:
        if not only_websites:
            if ask_polar_question('Do you want to execute system commands in order to perform an OSINT lookup of the provided username?'):
                execute_commands(username, commands_file, 'username')
                
                if not only_commands:
                    if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                        read_websites_file_and_visit(websites_file, 'username', username, browser)
        else:
            if not only_commands:
                if ask_polar_question('Do you want to start your browser in order to perform online information gathering?'):
                        read_websites_file_and_visit(websites_file, 'username', username, browser)
            else:
                print('Error: Conflicting command line options, -w and -c can not be used together.')
                exit(1)
    else:
        if only_commands:
            execute_commands(username, commands_file, 'username')
        elif only_websites:
            read_websites_file_and_visit(websites_file, 'username', username, browser)
        elif not only_commands and not only_websites:
            execute_commands(username, commands_file, 'username')
            read_websites_file_and_visit(websites_file, 'username', username, browser)
        else:
            print('Error: Conflicting command line options, -w and -c can not be used together.')
            exit(1)

# Main method
def main():
    global ask_questions, output_directory, commands_file, websites_file

    try:
        start_time = time.time()
        print(ASCII_ART)

        # Parse command line arguments
        parser = argparse.ArgumentParser(description='A simple program which automates OSINT information gathering about a specific person')

        parser.add_argument('input', help='Either email address, telephone number or username')
        parser.add_argument('-o', '--output', help='Specify an output directory') 
        parser.add_argument('-cf', '--commands-file', help='Specify a commands file')
        parser.add_argument('-wf', '--websites-file', help='Specify a websites file')
        parser.add_argument('-b', '--browser', help='Indicate the browser to use for a website lookup (firefox, chrome, edge)')
        parser.add_argument('-e', '--email', action='store_true', help='Force input to be handled as an email address') # Note: action='store_true' makes the switch optional
        parser.add_argument('-n', '--number', action='store_true', help='Force input string to be processed as a telephone number')
        parser.add_argument('-u', '--username', action='store_true', help='Force input string to be treated as username')
        parser.add_argument('-q', '--question', action='store_true', help='Asks questions before doing any major task')
        parser.add_argument('-c', '--commands', action='store_true', help='Only execute commands, do not visit websites')
        parser.add_argument('-w', '--websites', action='store_true', help='Only visit OSINT websites, do not execute commands')

        # Change help text formatter of argparse to align help text because of long argument names
        parser.formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=54)

        args = parser.parse_args()

        # Check if output directory, commands or websites file has been indicated
        if args.output:
            output_directory = args.output  

        if args.commands_file:
            commands_file = args.commands_file

        if args.websites_file:
            websites_file = args.websites_file  

        # Create output directory if not existing
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)

        # Check if should ask questions
        if args.question:
            ask_questions = True

        # Check which browser to use for website lookups
        if args.browser:
            browser = args.browser
        else:
            browser = "firefox"

        # Evaluate whether input string should be forced to be treated as certain type
        if args.email or args.number or args.username:
            if args.email:
                lookup_email(args.input, args.commands, args.websites, browser)
            elif args.number:
                lookup_phone_number(args.input, args.commands, args.websites, browser)
            else:
                lookup_username(args.input, args.commands, args.websites, browser)
        # Evaluate automatically type of input string and act accordingly
        else: 
            if is_email(args.input):
                lookup_email(args.input, args.commands, args.websites, browser)
            elif is_phone_number(args.input):
                lookup_phone_number(args.input, args.commands, args.websites, browser)
            else:
                lookup_username(args.input, args.commands, args.websites, browser)

        # Display information wrapup
        display_wrapup(start_time)
    except KeyboardInterrupt as e:
        exit(0)

if __name__ == '__main__':
    main()