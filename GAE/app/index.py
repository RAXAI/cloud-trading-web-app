import os
import logging
from flask import Flask, render_template,request
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import mean, stdev
import random
import numpy as np 
import boto3
import sys
from datetime import datetime
import socket
import time
import os
import paramiko
from ec2 import runec2
from activatelambda import runlambda
import io
import base64
from threading import Thread

app = Flask(__name__)

def timer():
	ec2 = boto3.resource('ec2',region_name="us-east-1")
	ec2_id = 'i-0a5d085a982249ce8'
	instance = ec2.Instance(id=ec2_id)
	print("starting instance " + ec2_id)
	instance.start()
	time.sleep(60*60)
	instance.stop()
	print('done')


def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(),
'templates/'+tname) ): #No such file
		return render_template('index.htm')
	return render_template(tname,**values)

@app.route('/plot')
def build_plot():
	df = pd.read_csv('BABA.csv')
	html = df.to_html(classes='table table-dark table-hover')
    

	return doRender('test.htm',{'df':html})
	


@app.route('/trade.htm')
def rec2():
	ec2 = boto3.resource('ec2',region_name="us-east-1")
	ec2_id = 'i-0a5d085a982249ce8'
	instance = ec2.Instance(id=ec2_id)
	print("starting instance " + ec2_id)
	instance.start()
	return doRender('trade.htm')


# Defines a POST supporting calculate route
@app.route('/calculate', methods=['POST'])
def calculateHandler():
	if request.method == 'POST':
		window = int(request.form.get('ma'))
		s	= int(request.form.get('mc'))
		r = int(request.form.get('resources'))
		v = int(request.form.get('var'))
		name = request.form.get('comp')
		service = request.form.get('service')
		if window <=0 or s <=0 or r<=0 or v<=0:
			return doRender('trade.htm',{'note': 'Please specify a number for each group!'})
		else:
			if service == 'ec2':
				plot_url,html_table, totalprofitloss, averagevar99,averagevar95 =  runec2(window,s,r,v,name)
				#json_object = json.dumps(json_helper)
				#data ={'dat':{'labour': lP,'conservative':cP}}
				return doRender('output.htm',{'plot_url':plot_url,'df':html_table,'profitloss':totalprofitloss,'var99':averagevar99,'var95':averagevar95})
			else:
				plot_url,html_table, totalprofitloss, averagevar99,averagevar95 =  runlambda(window,s,r,v,name)
				return doRender('output.htm',{'plot_url':plot_url,'df':html_table,'profitloss':totalprofitloss,'var99':averagevar99,'var95':averagevar95})
			
	return 'Should not ever get here'


# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def mainPage(path):
	background_thread = Thread(target=timer)
	background_thread.start()
	return doRender(path)


@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
	logging.exception('ERROR!')
	return """
	An error occurred: <pre>{}</pre>
	""".format(e), 500




if __name__ == '__main__':
	# Entry point for running on the local machine
	# On GAE, endpoints (e.g. /) would be called.
	# Called as: gunicorn -b :$PORT index:app,
	# host is localhost; port is 8080; this file is index (.py)
	app.run(host='127.0.0.1', port=8080, debug=True)
