#important Imports
'''
If you do not have either of this, please feel free to 
perform a pip install [module] in you local machine via terminal!!
'''
##____THis Code is ErrorLess_____##
import numpy as np 
import pandas as pd 
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import hashlib
import sqlite3 

#setup and Engineering
df = pd.read_csv('https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv')
cont_df = df[(df["CountryName"]=="United Kingdom") & (df['RegionCode'].isna())]
cont_df = cont_df.drop(['CountryName', 'CountryCode', 'RegionName', 'RegionCode'], axis=1).set_index('Date').fillna(method='ffill')
uk_df = cont_df[["ConfirmedCases", "ConfirmedDeaths"]]
uk_df.index = pd.to_datetime(uk_df.index, format="%Y%m%d")
uk_df = uk_df.sort_index()
uk_df.to_csv("uk_data.csv")

#the whole dataframe
# cont_df = pd.read_csv('Cases.csv',low_memory=False)
#uk Datarame
uk_df = pd.read_csv('uk_data.csv')
#Engineer a feature.
uk_df['InfectionRate'] = uk_df['ConfirmedCases'].diff()
uk_df['Recovered'] = uk_df['ConfirmedCases'] - uk_df['ConfirmedDeaths']
uk_df['RecoveryRate'] = uk_df['Recovered'].diff()

#infection rate dataframe
infect_rate = pd.read_csv('Infectionrate.csv')

#set up the UI
PAGE_CONFIG = {"page_title":"StColab.io","page_icon":":smiley:","layout":"centered"}
st.set_page_config(**PAGE_CONFIG)
# Security
#passlib,hashlib,bcrypt,scrypt
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data


def main():
	st.title("🦠 Covid-19 Data Explorer For UK's Infection Rate.")
	st.subheader("The dashboard will visualize the Covid-19 Situation in The UK")


	menu = ["Home","DataFrame", "Visualize","About", "Login","SignUp"]
	#If one chooces to proceed with the Home Button --->
	choice = st.sidebar.selectbox('Menu',menu)
	if choice == 'Home':
		st.subheader("Welcome Dear Reader):-")
		st.subheader("Let's Visualize:")
		st.markdown("This User Interface is meant to bring to you the current Covid-19 Status in the UK.\
		 Feel free to navigate through all the sections of this web application.\
		  You can also upload you Covid-19 data for your country and visualize it. We're all yours.")
		st.markdown("To view more, please proceed to the Visualize section under the dropdown menu. It's Fantastic")
		st.sidebar.title("Visualization Selector")
		st.sidebar.markdown("Select the Charts/Plots accordingly:")
	#If interested to see the Dataframe ---->
	elif choice == 'DataFrame':
		st.subheader('There are two dataframes here. The main one and a subset based on UK.')
		st.write('Choose one to continue with the following section:')
		a = st.radio('Choose whole or Subset to continue:',['whole','subset'],1)
		if a == "whole":
			st.write('Input the Date index number you want to view the Whole Covid-19 Dataset')
			st.markdown("**FROM**")
			start_date = st.number_input('Start date')
			st.markdown("**TO**")
			end_date = st.number_input('End date')
			st.dataframe(cont_df.iloc[int(start_date):int(end_date)].style.highlight_max(axis=0))
		else:
			st.write('Input the Date index number you want to view the UK Covid-19 Dataset')
			st.markdown("**FROM**")
			start_date = st.number_input('Start date')
			st.markdown("**TO**")
			end_date = st.number_input('End date')
			st.dataframe(uk_df.iloc[int(start_date):int(end_date)].style.highlight_max(axis=0))
	#if choice made is to see visualizations --->
	elif choice == 'Visualize':
		a = st.radio('Please choose on of the following',['Pie','Bar','Line', 'Map1','Map2','Map3'],2)
		if a == 'Pie':
			st.title("Selected days with Highest Number of Cases")
			top_n = pd.DataFrame({'values':uk_df.ConfirmedCases.nlargest(5),\
				'names':uk_df.ConfirmedCases.nlargest(5).index}).reset_index(drop=True)
			# top_n['names'] = [i.strftime("%b-%d") for i in top_n.names]
			fig = px.pie(top_n, values='values',names=['Nov-06','Nov-07','Nov-05','Nov-04','Nov-03'],\
				title='Days with Highest ConfirmedCases Cases',\
				hole=0.2)
			st.plotly_chart(fig)
			st.button('Voila, there we go! Seems that the three consecutive days of November 5,6 and 7 \
				actually recorded the Highest confirmed cases.')
		if a == 'Bar':
			st.title("Bar Charts of Cases,Deaths and Recoveries")	
			fig = go.Figure(data=[
			go.Bar(name='Confirmed Cases', x=uk_df.index, y=uk_df['ConfirmedCases']),
			go.Bar(name='Deaths', x=uk_df.index, y=uk_df['ConfirmedDeaths']),
			go.Bar(name='Recoveries', x=uk_df.index, y=uk_df['Recovered'])
			])
			st.plotly_chart(fig)

			st.write('Equally, the bar graph could easily depict the death Rate.')
		if a == 'Line':
			fig = go.Figure()
			for col in uk_df[['ConfirmedCases', 'ConfirmedDeaths']]:
				fig.add_trace(go.Scatter(x=uk_df.index, y=uk_df[col], name=col))
			
			fig.update_layout(title="Case & Death Count in UK")
			st.plotly_chart(fig)
		if  a == 'Map1':
			# cases_08_01 = cont_df.loc['2020-08-01'].to_frame('Case Count').reset_index()
			# cases_08_01.to_csv('cases_08_01')
			data = pd.read_csv('cases_08_01.csv')
			fig = px.choropleth(data,
                   locations='CountryCode', color='Case Count')
			fig.update_layout(title="Map Visualization at August 1")
			st.plotly_chart(fig)
		if a == 'Map2':
			# log_cases_08_01 = cont_df.loc['2020-08-01'].apply(lambda x: np.log10(x)).to_frame('Case Count (log)').reset_index()
			# log_cases_08_01.to_csv('log_cases_08_01.csv')
			data = pd.read_csv('log_cases_08_01.csv')
			fig = px.choropleth(data,
                   locations='CountryCode', color='Case Count (log)')
			fig.update_layout(title="Log Map Visualization at August 1")
			st.plotly_chart(fig)
		if a == 'Map3':
			# infect_rate_08 = infect_rate.loc['2020-08-01'].to_frame('Infection Rate').reset_index()
			# infect_rate_08.to_csv('infect_rate_08.csv')
			data = pd.read_csv('infect_rate_08.csv')
			fig = px.choropleth(data,
                   locations='CountryCode',
                   color='Infection Rate')
			# fig.update_layout(title='Infection Rate Map at August 1')
			st.plotly_chart(fig)
	#if choice made is to Login for more user or admin priviledges --->
	elif choice == "Login":
		st.subheader("Login Section")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:

				st.success("Logged In as {}".format(username))

				task = st.selectbox("Task",["Add Post","Data","Analytics","Profiles"])
				if task == "Add Post":
					st.subheader("Add Your Post")
				elif task == "Data":
					st.subheader("The link to download the sourcefiles and data is at :")
					st.markdown("1. [Link to the dataset]('https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv')")
					st.markdown("2. [Data Preprocessing source file](https://colab.research.google.com/drive/1vWwsDKJXKR-UWHFkkaIER-ZfdM4axM52#scrollTo=AZAuEO6lfEC_)")
					st.markdown("3. [Clustering source file]('https://colab.research.google.com/drive/1UncLBvWPe6SBQqRqCv0eWbSjHlw95IR4')")
					st.markdown("$\mathcal{Check}$")
					st.markdown("$\pi$ is a number,but $\mu$ is a Statistic.")
					st.markdown("$\mathcal{Everything\quad Counts!}$")
				elif task == "Analytics":
					st.subheader("Analytics")
				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_all_users()
					clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
					st.dataframe(clean_db)
			else:
				st.warning("Incorrect Username/Password")
	#if choice made is to Create a new account/sign-up --->
	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")


	#if choice made is to view all about this Covid-UI ----->
	else :
		st.markdown('Coronavirus disease (COVID-19) is an infectious disease caused by \
			a newly discovered coronavirus. Most people infected with the COVID-19 virus \
			will experience mild to moderate respiratory illness and recover \
			without requiring special treatment.')

	select = st.sidebar.selectbox("Select", ['Infection Rate','Recovery Rate'],key='1')
	if not st.sidebar.checkbox("Hide",False, key='2'):
		if select == 'Infection Rate':
			fig = go.Figure()
			for col in uk_df[['InfectionRate']]:
			    fig.add_trace(go.Scatter(x=uk_df.index, y=uk_df[col], name=col))
    
			fig.update_layout(title="Infection Rate in UK")
			st.plotly_chart(fig)
		if select == 'Recovery Rate':
			fig = go.Figure()
			for col in uk_df[['RecoveryRate']]:
				fig.add_trace(go.Scatter(x=uk_df.index, y=uk_df[col], name=col))
			fig.update_layout(title="Recovery Rate in UK")
			st.plotly_chart(fig)



	select1 = st.sidebar.selectbox('Select', ['Confirmed', 'Deaths','Recovered'], key='3')
	if not st.sidebar.checkbox("Hide", True, key='4'):
		if select1 == 'Confirmed':
			fig = px.line(uk_df, x=uk_df.index, y=uk_df.ConfirmedCases)
			fig.update_layout(title='Confirmed Cases')
			st.plotly_chart(fig)
		elif select1 == 'Recovered':
			fig = px.line(uk_df, x=uk_df.index, y=uk_df.Recovered)
			fig.update_layout(title='Death Cases')
			st.plotly_chart(fig)
		else:
			fig = px.line(uk_df, x=uk_df.index, y=uk_df.ConfirmedDeaths)
			fig.update_layout(title='Recovered Cases')
			st.plotly_chart(fig)



if __name__ == '__main__':
	main()
    
