import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import mean, stdev
import random
import numpy as np 
import sys
import json
from datetime import datetime
import time
import os
import io
import base64
import http.client
from ast import literal_eval



'''
#example
window = 50
s = 10000
r = 5
v = 20
name = 'BABA'
'''

'''
This code activates lambda function via the endpoint I provided.
'''


def runlambda(window,s,r,v,name):
	#place parameters into dictionary
	dic = {"window": window,"s": s,"r": r,"v": v,"name": name}
	c = http.client.HTTPSConnection("x39cjtdr7a.execute-api.us-east-1.amazonaws.com")
	#put into json format for the lambda function
	json_ob = json.dumps(dic)
	
	
	c.request("POST","/alpha/lambdabackend",json_ob)
	
	response = c.getresponse()
	#reading byte stream from lambda function and converting to dictionary
	data=response.read()
	byte_str = data
	dict_str = byte_str.decode("UTF-8")
	mydata = literal_eval(dict_str)
	
	
	#access the data and convert from dic to Dataframe

	df_dict = mydata['data']

	df = pd.DataFrame.from_dict(df_dict)
	df.index = df['Date']

	df2 = df.drop(columns=['Date'])

	
	df2.index = pd.to_datetime(df2.index)
	
	
	#html_table = df2.to_html(classes='table table-dark table-hover')
	html_table = mydata['html_table']
	totalprofitloss = str(mydata['totalprofitloss'])
	averagevar99 = str(mydata['averagevar99'])
	averagevar95 = str(mydata['averagevar95'])	
	

	last_signal = mydata['last_signal']
	last_signal_date = datetime.strptime(mydata['last_signal_date'],"%Y-%m-%d %H:%M:%S")
	last_signal_close_price = mydata['last_signal_close_price']

	#creating plot then then converting to url
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
















