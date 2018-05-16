# coding=utf-8

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


client = MongoClient('localhost', 27017)
db = client.imdb
movies_db = db.movies

n_movies = movies_db.find().count()
n_movies_without_budget = movies_db.find({'budget': None}).count()
n_movies_without_gross = movies_db.find({'usa_gross': None}).count()
n_movies_without_world_gross = movies_db.find({'worldwide_gross': None}).count()
n_movies_with_budget_and_gross = movies_db.find({'$and': [{'budget': {'$ne': None}}, {'usa_gross': {'$ne': None}}]}).count()

print('Total: ' + str(n_movies))
print('Movies with budget: ' + str(n_movies - n_movies_without_budget))
print('Movies with gross: ' + str(n_movies - n_movies_without_gross))
print('Movies with worldwide gross: ' + str(n_movies - n_movies_without_world_gross))
print('Movies with budget and gross: ' + str(n_movies_with_budget_and_gross))

df = pd.Series(data=[n_movies, n_movies_without_budget, n_movies_without_gross, n_movies_without_world_gross, n_movies_with_budget_and_gross],
	index=['N of movies', 'N without budget', 'N without gross', 'Nwithout world gross', 'N with budget and gross'])

# plt.bar(np.arange(5), df)
# plt.xticks(np.arange(5), df.keys(), rotation=30)
# plt.show('hold')

# 1846 movies with budget and gross --> 230 movies per year --> 4 movies premiere per week

movies = movies_db.find({'$and': [{'budget': {'$ne': None}}, {'usa_gross': {'$ne': None}}]})

movies_df = pd.DataFrame(list(movies))
movies_df.to_csv('test.csv', encoding='utf-8', sep='\t', index=False)
# convert to utf-8
movies_df['title'] = [x for x in movies_df['title'].values]
print(movies_df['title'][5])


print(movies_df.iloc[0, :])




