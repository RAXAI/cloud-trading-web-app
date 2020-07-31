import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import mean, stdev
import random
import numpy as np 
import boto3
import sys
import json
from datetime import datetime
import socket
import time
import os
import paramiko
import io
import base64


'''
#example
window = 50
s = 10000
r = 5
v = 20
name = 'BABA'
'''

'''
Purpose of this script is to activate the ec2 instance 
and pass the values entered from the website to the ec2 instacnce 
to process.

'''
def runec2(window,s,r,v,name):
	executable ='python backend.py {} {} {} {} {}'.format(window,s,r,v,name)
	retries = 10
	retry_delay=2
	retry_count = 0
	ec2 = boto3.resource('ec2',region_name="us-east-1")
	ec2_id = 'xxxxxxxx'
	instance = ec2.Instance(id=ec2_id)
	instance.wait_until_running()
	'''
	while retry_count <= retries:
		  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		  result = sock.connect_ex((instance.public_ip_address,22))
		  if result == 0:
		  	print("Instance is UP & accessible on port 22, the IP address is:  " + str(instance.public_ip_address))
		  	break
		  else:
		  	print('instance is still down retrying ...')
		  	time.sleep(retry_delay)'''

	k = paramiko.RSAKey.from_private_key_file('xxxxxxxxx.pem')
	c = paramiko.SSHClient()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print('Connecting to shell using ssh')
	c.connect(hostname = instance.public_dns_name,username='ec2-user',pkey=k)

	print('executing commands')

	stdin,stdout,stderr = c.exec_command('source env/bin/activate ; {}'.format(executable))
	exit_status = stdout.channel.recv_exit_status()
	if exit_status == 0:
		print("Script Finished")
	else:
		print("Error", exit_status)

	#python3 backend.py {0} {1} {2} {3} {4} """.format(window,s,r,v,name), get_pty=True)


	instance.stop()

	# EC2 instance finished processing

	# We now retrieve the results from the s3 bucket
	s3 = boto3.client('s3')

	obj = s3.get_object(Bucket='xxxxxxx', Key=name+'data.json')

	data = json.loads(obj['Body'].read())

	df_dict = data['data']

	df = pd.DataFrame.from_dict(df_dict)

	df.index = df['Date']

	df2 = df.drop(columns=['Date'])


	df2.index = pd.to_datetime(df2.index)

	# converting out dataframe table into html format

	html_table = df2.to_html(classes='table table-dark table-hover')
	
	totalprofitloss = str(data['totalprofitloss'])
	averagevar99 = str(data['averagevar99'])
	averagevar95 = str(data['averagevar95'])
	
	



	last_signal = data['last_signal']
	last_signal_date = datetime.strptime(data['last_signal_date'],"%Y-%m-%d %H:%M:%S")
	last_signal_close_price = data['last_signal_close_price']

	# plotting our data, then encoding the graph as a base64 url.
	plt.figure(figsize=[10,5])
	plt.grid(True)
	plt.plot(df2.index, df2['Adj Close'],label='Adjusted Close Price')
	plt.plot(df2.index, df2['moving_average'],label='Moving Average,'+' '+str(window)+' '+'days')
	plt.xticks(rotation='vertical')
	plt.axvline(x=last_signal_date, color='r', linestyle='-', label= 'Position: '+last_signal+' Date: '+str(last_signal_date))
	plt.axhline(y=last_signal_close_price,color='k', linestyle='-', label= 'Closing Price: '+str(last_signal_close_price))
	plt.legend(loc=2)
	plt.title(name)
	img = io.BytesIO()
	plt.savefig(img, format='png')
	img.seek(0)
	plot_url = base64.b64encode(img.getvalue()).decode()
	
	return (plot_url , html_table, totalprofitloss, averagevar99, averagevar95)




