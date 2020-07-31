import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import mean, stdev
import random
import numpy as np 
import boto3
import sys
import json


'''
examples of parameters which could be used 
window = 50
s = 10000
r = 5
v = 20
name = 'AAPL'
'''
def process(window,s,r,v,name):

	s3 = boto3.client('s3')
	
	#enter s3 bucket name 
	obj = s3.get_object(Bucket='', Key=name+'.csv')


	df = pd.read_csv(obj['Body'],index_col='Date',parse_dates=True,dayfirst=True) 
	
	# 1. Moving Average
	# calculating moving average for given window size
	# Add this as a column to our original dataframe 
	df_ma = df['Adj Close'].rolling(window=window,min_periods=1).mean()
	df['moving_average']=df_ma

	# Calculating buy and sell signals after v days

	def signal(x):
		if (x['Adj Close'] - x['moving_average'])>= 0:
			return 'Positive'
		else:
		    return 'Negative'

	df['Sign'] = df.apply(signal, axis=1)

	signs = df['Sign'].tolist()

	signal = [0]

	for x in range(1,len(signs)):
		if x <= v:
			signal.append(0)
		elif signs[x] == signs[x-1]:
	  		signal.append(0)
		elif signs[x]=='Negative':
	  		signal.append('Buy')
		else:
			signal.append('Sell')

	df = df.assign(Signal = signal)

	#calculating profit/loss at sell signals
	#keep count of the total accumulated profit/loss value
	# assuming the buying strategy of buying 2000 shares at buy sell signal 
	# and selling 1000 shreas at sell signals
	bought_price = 0
	accumulated = 0
	shares_owned = 0
	profit_loss = []
	profit_loss_acc = []


	signal = df['Signal'].tolist()
	adj = df['Adj Close'].tolist()


	for x in range(len(signal)):
		if signal[x] == 'Buy':
			bought_price = adj[x]
			shares_owned+=2000
			profit_loss.append(0)
			profit_loss_acc.append(accumulated)
		elif signal[x]== 'Sell':
			pl = (adj[x]*1000)-(bought_price*1000)
			profit_loss.append(pl)
			accumulated += pl
			profit_loss_acc.append(accumulated)
			shares_owned -=1000
		else:
			profit_loss.append(0)
			profit_loss_acc.append(accumulated)

	df = df.assign( Profitloss = profit_loss)
	df = df.assign(ProfitlossAcc = profit_loss_acc)

	# calculating the value at risk
	#check var use to calculate mean and std 
	check_var = []
	var = []

	for x in range(1,v):
		var_value = ((adj[x]-adj[x-1])/adj[x-1])
		var.append(var_value)
		check_var.append(var_value)

	#calculate mean and standard deviation of return series using
	

	var_mean = mean(var)
	var_std = stdev(var)
	

	# monte carlo simulations of length s
	return_series = [random.gauss(var_mean,var_std) for _ in range(s) ]

	#sorting list largest to smallest
	return_series.sort()
	return_series.reverse()

	

	#calculating the 95 and 99th percentilee

	var_95 = np.quantile(return_series,0.05) 
	var_99 = np.quantile(return_series,0.01)




	# Calculate the value at risk using the 95th and 99th percentile for every buy/sell signal 
	value_at_risk_95=[]
	value_at_risk_99=[]
	
	# created two lists where var values appended to calculate the average var for 95th and 99th percentile
	average99 = []
	average95 = []


	for x in range(len(signal)):
		if signal[x] == 'Buy':
			value95= 1000*-1*var_95*adj[x]
			value99=1000*-1*var_99*adj[x]
			value_at_risk_95.append(value95)
			value_at_risk_99.append(value99)
			average99.append(value99)
			average95.append(value95)
		elif signal[x] == 'Sell':
			value95= 1000*var_95*adj[x]
			value99=1000*var_99*adj[x]
			value_at_risk_95.append(value95)
			value_at_risk_99.append(value99)
			average99.append(value99)
			average95.append(value95)
		else:
			value_at_risk_95.append(0)
			value_at_risk_99.append(0)

	# calculating the average value at risk for each trading strategg at 95th and 99th percentile

	averagevar99 = mean(average99)
	averagevar95 = mean(average95)

	#appending the new columns to our data frame 
	df = df.assign(Var95 = value_at_risk_95)
	df = df.assign(Var99 = value_at_risk_99)

	#Detemining the last buy/sell signal, with the close price and date which this occured.
	dates = df.index.to_list()
	last_signal = ''
	last_signal_date = ''
	last_signal_close_price = 0
	signal.reverse()
	dates.reverse()
	adj.reverse()

	for x in range(len(dates)):
		if signal[x]=='Buy' or signal[x]=='Sell':
			last_signal = signal[x]
			last_signal_close_price = adj[x]
			last_signal_date = dates[x]
			break
		else:
			continue
		
	print(last_signal)
	print(last_signal_date)
	print(last_signal_close_price)

	df2 = df.drop(columns=['Open','High','Low','Close','Volume'])



	# create dictionary hosting all data which needs to be sent back to s3 bucket
	returnable = {}
	df2.index = df2.index.astype(str)
	df2['Date']=df2.index
	df_dict = df2.to_dict('list')

	returnable['data'] = df_dict
	returnable['averagevar99'] = averagevar99
	returnable['averagevar95'] = averagevar95
	returnable['totalprofitloss'] = df2.ProfitlossAcc.tolist()[-1]
	returnable['last_signal_date'] = str(last_signal_date)
	returnable['last_signal'] = last_signal
	returnable['last_signal_close_price'] = last_signal_close_price
	
	
	data_json = json.dumps(returnable)
	s3.put_object(Bucket='randy9821',Key=name+'data'+'.json', Body=data_json)
	return returnable



''''
uncomment to run
process(10,10,10,10,'BABA')
'''


