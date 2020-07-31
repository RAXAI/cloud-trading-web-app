# cloud-trading-web-app
Design and development of Python Flask web application for financial Value at Risk (VaR) calculation for various trading dataset and deployed in Multi-Cloud (Google App Engine, AWS EC2, AWS lambda, S3).

The web application can be found on this link: https://stag-trade.ew.r.appspot.com/

The backend scripts for the generation of trading signals for EC2 and Lambda function can be found in the Lambda and EC2 folders respectively

In GAE it contains the flask app. There is index.py which is a python script which defines all the routing and transfer of data for the website. There is also ec2.py and activatelambda.py, these scripts activate and pass data to the Lambda function and EC2 for processing.

Also in GAE you will find the HTML pages and CSS scripts used for the website.
