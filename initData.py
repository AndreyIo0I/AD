import time
from pathlib import Path
import subprocess
import os
import pandas as pd
from sqlalchemy import create_engine
from progress.bar import IncrementalBar

script_start_time = time.time()

if Path('./COVID-19').exists():
	subprocess.run(['git', 'pull'], cwd='COVID-19')
else:
	subprocess.run(['git', 'clone', 'https://github.com/CSSEGISandData/COVID-19'])

engine = create_engine('mysql+pymysql://root:1234@localhost:3306')
engine.execute('CREATE DATABASE IF NOT EXISTS covid')
engine.execute('USE covid')

engine.execute('DROP TABLE IF EXISTS csse_covid_19_daily_reports')
engine.execute('DROP TABLE IF EXISTS csse_covid_19_daily_reports_us')


def create_table(csvs_path):
	create_table_time = time.time()

	csv_files = []
	for file in os.listdir(csvs_path):
		if Path(file).suffix == '.csv':
			csv_files.append(file)

	bar = IncrementalBar(csvs_path.split('/')[-1], max=len(csv_files))
	big_dataframe = pd.DataFrame()
	for file in csv_files:
		if Path(file).suffix == '.csv':
			df = pd.read_csv(csvs_path + '/' + file)
			big_dataframe = pd.concat([big_dataframe, df], ignore_index=True)
			bar.next()

	print('\nto db...')
	big_dataframe.to_sql(csvs_path.split('/')[-1], con=engine, method='multi', chunksize=3000)  # if_exists не заработал
	print('create table time: ', time.time() - create_table_time)
	return


create_table('./COVID-19/csse_covid_19_data/csse_covid_19_daily_reports')
create_table('./COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us')
print('script exec time: ', time.time() - script_start_time)
