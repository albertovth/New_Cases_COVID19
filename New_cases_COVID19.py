## This script reads a raw csv file with updated data on daily confirmed new cases of COVID-19.
## Source: "Our Wolrd in Data" (OWID), COVID-19 data Github repository URL: https://github.com/owid/covid-19-data
## The script calculates daily world totals by country, based on the daily data.
## This information is then used to calculate a world trend line, for total and daily cases.
## This result is presented as a line plot, together with country line plots, on log scales.
## A for loop generates plots by region.
## The result can be used to monitor which countries manage to control the pandemic.
## Success in controlling the pandemic implies a dip in the line plot on the y-axis and no progress on the x-axis.


import pandas as pd
import io
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import urllib
import requests
import unicodedata

## Read csv file from source and create data frame

url='http://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_cases.csv'
s=requests.get(url).content
df_daily_cases=pd.read_csv(io.StringIO(s.decode('utf-8')),header=0)
df_daily_cases.set_index('date', inplace=True, drop=True)

## Create data frame for daily totals, as cumulative sum data frame of daily cases

df_total_cases = df_daily_cases.cumsum()

## Change country column names by data frame, to distinguish columns before concatenation

df_daily_cases.columns = [str(col) + '_New' for col in df_daily_cases.columns]
df_total_cases.columns = [str(col) + '_Total' for col in df_total_cases.columns]

## Concatenate data frames into one data frame that includes new cases and totals

df_new_total = pd.concat([df_daily_cases, df_total_cases], axis=1)

## Generate new data frame column, to calculate world trend line,
## by stacking daily cases columns into one,
## and sorting, first by country, then by date

df_trend_li_daily=df_daily_cases
df_trend_lin_daily=df_trend_li_daily.stack()
df_trend_line_daily=df_trend_lin_daily.to_frame()
df_trend_line_daily.reset_index(inplace=True)
df_trend_line_daily.columns=['date','Country_New','New_Cases']
df_trend_line_daily_final = df_trend_line_daily.sort_values(by=['Country_New','date'])

## Generate new data frame column, to calculate world trend line,
## by stacking total cases country columns into one,
## and sorting, first by country, then by date

df_trend_li_total=df_total_cases
df_trend_lin_total=df_trend_li_total.stack()
df_trend_line_total=df_trend_lin_total.to_frame()
df_trend_line_total.reset_index(inplace=True)
df_trend_line_total.columns=['date','Country_Total','Total_Cases']
df_trend_line_total_final= df_trend_line_total.sort_values(by=['Country_Total','date'])

## Concatenate columns for total cases and new cases into one data frame

df_trend_line = pd.concat([df_trend_line_total_final['Total_Cases'], df_trend_line_daily_final['New_Cases']], axis=1, keys=['Total_Cases', 'New_Cases'])

## Define variables for regression model

x = df_trend_line['Total_Cases']
y = df_trend_line['New_Cases']

## Calculate parameters for linear regression model by OLS

x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
results.params
results.tvalues

## Asign variable for t-tests, in case necessary

tt = results.t_test(np.eye(len(results.params)))

## Move results parameters to frame, and set column title as value
results_parameters = results.params.to_frame()
results_parameters.columns=['Value']

## Use statsmodels results.summary, to obtain data to test significance
## of parameters and regression (t-tests and F-test)
print(results.summary())

## Define variables for parameter values, in order to make trend prediction curve
x1=results_parameters.iloc[0]['Value']
beta=results_parameters.iloc[1]['Value']

## Define X values in log scale as list
X= [1,10,100,1000,10000,100000,1000000,10000000]

## Append regression results to Y values as list
Y=[]
for i in X:
    y = x1 + beta * (i)
    Y.append(y)

## Create data frame based on X values and add Y values
df_trend_line_prediction = pd.DataFrame(X)
df_trend_line_prediction.columns = ['Total cases in the world']
df_trend_line_prediction['World Daily Trend']=Y

## Print prediction
print('Global Trend Line Prediction:')
print(df_trend_line_prediction)

## Create date and time variable
date_time=datetime.datetime.now()

## Plot data from Nordic countries, World and trend curve as lines
## Names below can be changed manually, to visualize other countries
ax = plt.gca()

df_new_total.plot(kind='line',x='World_Total',y='World_New',color='darkmagenta',ax=ax, logx=True,logy=True)
df_new_total.plot(kind='line',x='Denmark_Total',y='Denmark_New', color='black', ax=ax, logx=True,logy=True)
df_new_total.plot(kind='line',x='Norway_Total',y='Norway_New', color='red', ax=ax, logx=True,logy=True)
df_new_total.plot(kind='line',x='Sweden_Total',y='Sweden_New', color='yellow', ax=ax, logx=True,logy=True)
df_new_total.plot(kind='line',x='Finland_Total',y='Finland_New', color='cyan', ax=a, logx=True,logy=True)
df_new_total.plot(kind='line',x='Iceland_Total',y='Iceland_New', color='navy', ax=ax, logx=True,logy=True)
df_trend_line_prediction.plot(kind='line',x='Total cases in the world',y='World Daily Trend', color='lime', ax=ax, logx=True,logy=True, title='Nordic Countries')

plt.show()
plt.savefig('/Users/user/Desktop/nordic_countries_'+str(date_time)+'.png')
plt.clf()

## Create list for matplotlib color names corresponding to each country in the world,
## with as little color repetition as possible
## This step was done with another script

color_names= ['palevioletred', 'crimson', 'burlywood', 'lightyellow', 'slateblue', 'salmon', 'black', 'gold', 'mediumslateblue', 'seagreen', 'navy', 'snow', 'darkslategrey', 'm', 'lightsalmon', 'royalblue', 'mediumseagreen', 'darkblue', 'tomato', 'pink', 'brown', 'cornflowerblue', 'olivedrab', 'yellow', 'lightslategrey', 'darkcyan', 'lightgray', 'darkolivegreen', 'slategrey', 'c', 'mintcream', 'mediumorchid', 'turquoise', 'w', 'red', 'olive', 'lightskyblue', 'peachpuff', 'plum', 'cornsilk', 'blue', 'gray', 'teal', 'mediumvioletred', 'lightgreen', 'firebrick', 'seashell', 'lawngreen', 'mediumspringgreen', 'palegoldenrod', 'tan', 'palegreen', 'green', 'darkorchid', 'g', 'lightcoral', 'darkorange', 'aquamarine', 'fuchsia', 'k', 'lime', 'cyan', 'lightslategray', 'darkmagenta', 'navy', 'orange', 'darkgreen', 'linen', 'darkseagreen', 'rosybrown', 'silver', 'magenta', 'lavender', 'aliceblue', 'darkgoldenrod', 'indianred', 'darkkhaki', 'bisque', 'slategray', 'limegreen', 'khaki', 'mediumturquoise', 'ivory', 'skyblue', 'b', 'darkgrey', 'peru', 'sandybrown', 'gray', 'paleturquoise', 'maroon', 'mediumblue', 'forestgreen', 'deepskyblue', 'gainsboro', 'oldlace', 'blanchedalmond', 'sienna', 'lightblue', 'darkturquoise', 'chartreuse', 'coral', 'lightgoldenrodyellow', 'green', 'thistle', 'lightcyan', 'beige', 'orangered', 'mediumpurple', 'aqua', 'goldenrod', 'darkred', 'mediumaquamarine', 'azure', 'darksalmon', 'darkviolet', 'hotpink', 'chocolate', 'lightsteelblue', 'red', 'moccasin', 'yellowgreen', 'purple', 'papayawhip', 'indigo', 'dimgray', 'darkslategray', 'midnightblue', 'r', 'honeydew', 'cadetblue', 'lightgrey', 'greenyellow', 'orchid', 'black', 'y', 'rebeccapurple', 'lemonchiffon', 'mistyrose', 'violet', 'wheat', 'steelblue', 'dimgrey', 'powderblue', 'lightseagreen', 'saddlebrown', 'deeppink', 'darkgray', 'grey', 'lavenderblush', 'springgreen', 'blueviolet', 'darkslateblue', 'lightpink', 'dodgerblue', 'blue', 'palevioletred', 'crimson', 'burlywood', 'lightyellow', 'slateblue', 'salmon', 'black', 'gold', 'mediumslateblue', 'seagreen', 'navy', 'snow', 'darkslategrey', 'm', 'lightsalmon', 'royalblue', 'mediumseagreen', 'darkblue', 'tomato', 'pink', 'brown']

country= ['Afghanistan', 'Algeria', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Cook Islands', 'Costa Rica', "Cote d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Democratic Republic of Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'French Polynesia', 'Gabon', 'Gambia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Italy', 'Jamaica', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Republic of Congo', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines', 'Saint Lucia', 'Samoa', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Tuvalu', 'Uganda', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Vanuatu', 'Venezuela', 'Vietnam', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe']

## Create data frame for countries and colors
df_farger = pd.DataFrame()
df_farger['Country'] = country
df_farger['Color']= color_names

## Create regional country lists
Europe = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Iceland', 'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']

Africa = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cape Verde', 'Cameroon', 'Central African Republic', 'Chad',"Cote d'Ivoire",'Democratic Republic of Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Western Sahara', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe']

Americas = ['Antigua and Barbuda', 'Argentina', 'Bahamas', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Grenada', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines', 'Saint Lucia', 'Suriname', 'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela']

Arabia = ['Algeria', 'Bahrain', 'Djibouti', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 'Libya', 'Mauritania', 'Morocco', 'Oman', 'Palestine', 'Qatar', 'Saudi Arabia', 'Somalia', 'Sudan', 'Syria', 'Tunisia', 'United Arab Emirates', 'Yemen']

Eurasia = ['Armenia', 'Belarus', 'Kazakhstan', 'Kyrgyzstan', 'Russia']

East_Asia = ['Brunei', 'Cambodia', 'China', 'Indonesia', 'Laos', 'Malaysia', 'Myanmar', 'Philippines', 'Singapore', 'South Korea', 'Taiwan', 'Thailand', 'Vietnam']

South_Asia = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka']

Pacific_Islands = ['Australia', 'New Caledonia', 'Papua New Guinea', 'New Zealand', 'Fiji']

## Define list tuples for region and region title
region_list = [(Europe, 'Europe'), (Africa, 'Africa'), (Americas, 'Americas'), (Arabia,'Arabia'), (Eurasia,'Eurasia'),(East_Asia,'East Asia'),(South_Asia,'South Asia'),(Pacific_Islands, 'Pacific Islands')]

## Loop through list titles and titles in region list, creating plots for each country in region
for list_titles, titles in region_list:
    ax=plt.gca()
    for i in list_titles:
        a=str(i)
        b=str(df_farger.loc[df_farger['Country'] == a,'Color'].iloc[0])
        urllib.parse.quote("'" + b + "'")
        unicodedata.normalize('NFKD',b).encode('ascii', 'ignore')
        df_new_total.plot(kind='line',x=str(str(i)+'_Total'),y=str(str(i)+'_New'),color=b,ax=ax,logx=True, logy=True)
    df_trend_line_prediction.plot(kind='line',x='Total cases in the world',y='World Daily Trend', color='lime', ax=ax, logx=True,logy=True,figsize = (10,7),title=str(titles))
    ax.legend(loc=(1.01, 0.01), ncol=2)
    plt.tight_layout()
    plt.savefig('/Users/user/Desktop/'+str(titles)+'_'+str(date_time)+'.png')
    plt.clf()
