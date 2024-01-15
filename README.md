# Prson
![Program Version: 1.0](https://img.shields.io/badge/Program%20Version-1.0-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-purple)
![Supported: Emails, Phone Numbers & Usernames](https://img.shields.io/badge/Supported-Emails%2C%20Phone%20Numbers%20%26%20Usernames-darkgreen?color=0795C0)

A simple command line tool which automates OSINT information gathering about a specific email address, telephone number or username

## Usage
**You need to have Python3 installed.**
<br/><br/>

General syntax: `python prson.py <email/telephone number/username>`

Use `python prson.py -h` to display an extensive help screen

## Features
- Regroup OSINT system tools by information type and start them if they are in the same type category as the users input
- Regroup websites by information type and visit them in a browser window if they are in the same type category as the users input. Supports automatic filling out of form fields.

## Configuration
The configuration files are in YAML format.

### Commands File
*See example file commands.txt in main project directory*

To add a command to the commands file, use this syntax:

```
- command: <command>
  type: <email/phone/username>
```
  
### Websites File
*See example file websites.txt in main project directory*

To add a website to the websites file, use the following syntax:
#### Websites with a form to fill out and submit
```
- url: <website_link>
  type: <email/phone/username>
  request_type: POST
  field_attribute: <attribute>
  field_value: <value>
  field_input: <input_string>
```
Where:
- field_attribute represents an HTML attribute
- field_value represents the value of the specified attribute
- field_input represents the text that should be filled in to the HTML component (e.x: search bar). You can insert $INPUT into the field_input value which will later be replaced by the users input string.

#### Websites without a form to fill out
```
- url: <website_link>
  type: <email/phone/username>
  request_type: GET
```
Where:
- url can contain $INPUT, which will be replaced by the users input. (e.x: https://google.com/search?q=$INPUT)
- type is the information type processed by the website
