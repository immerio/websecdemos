## Web Security Demos

A web application with several vulnerabilities for demonstration purposes.
Included vulnerabilities:
-  Broken authentication
- Broken session management
- Injection
- Security Misconfiguration
- Cross Site Scripting

[![websecdemos](static/img/readme_header.png)](https://github.com/immerio/websecdemos)

## Setup

### Docker
> docker-compose up -d

or 

> docker run -d --rm -p 127.0.0.1:5000:5000 websecdemos

Then browse to http://localhost:5000

### Local setup

With Python3 and Pip installed:

> pip install -r requirements.txt
> python demos.py

Then browse to http://localhost:5000

## Usage
Go to http://localhost:5000/selection and choose one of the demos included. 
There is a short help text for each demo at http://localhost:5000/help