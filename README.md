![](https://github.com//digital-land/cpos-prototype/workflows/cpos-prototype/badge.svg)

CPOs Prototype
==============

This prototype displays CPO data.

Requirements

- [Python 3](https://www.python.org/)
- [Node](https://nodejs.org/en/) and [Npm](https://www.npmjs.com/)
- [Gulp](https://gulpjs.com/)

Getting Started
===============

Install Flask and python dependencies

    pipenv install or pip install -r requirements.txt

Install front end build tool (gulp)

    npm install && gulp scss

Run the app

    flask run
    

Create db and run initial migration

    createdb cpo
    flask db upgrade


To upload data, there is a form at /upload which you can use
to upload the four three required csv files

 - compulsory-purchase-order.csv
 - compulsory-purchase-order-status.csv
 - compulsory-purchase-order-investigation.csv
 
 They'll need to be downloaded from google docs first as a zip file and
 the zipfile can be uploaded directly to the app.
 
 
 #### Setup for Auth0
 
 Add the following environment variables to .env (which is git ignored)
 
    AUTH0_CLIENT_ID=[get from settings]
    AUTH0_CLIENT_SECRET=[get from settings]
    AUTH0_DOMAIN=[get from settings]
    AUTH0_CALLBACK_URL=http://localhost:5000/auth/callback
    AUTHENTICATION_ON=True
    
The last setting allows toggle authentication on/off
