
import pandas as pd
from get_labels import make_request_url, get_data
import matplotlib.pyplot as plt

# Part A
query = make_request_url()
records = get_data(query)

df_AZ = pd.DataFrame.from_records(records)

partA = df_AZ[['year', 'drug_name', 'n_ingredients']].groupby('year').agg(
    {
        'n_ingredients':['mean'],
        'drug_name':[lambda x: ','.join(set(x))]
    }
)
partA.columns.droplevel(1)
partA.columns = ['avg_number_of_ingredients', 'drug_names']
partA.reset_index(inplace=True)
print(partA.head())

# simple data visualisation
partA.plot(kind='bar', x='year', y='avg_number_of_ingredients')
plt.xlabel('year')
plt.ylabel('Average Number of Ingredients')
plt.savefig('partA.png')


# Part B
query = make_request_url(MANUFACTURER='ALL')
records = get_data(query)

df_all = pd.DataFrame.from_records(records)

partB = df_all[['year', 'route', 'n_ingredients']].groupby(['year', 'route']).agg(
    {
        'n_ingredients':['mean']
    }
)
partB.columns.droplevel(1)
partB.columns = ['avg_number_of_ingredients']
partB.reset_index(inplace=True)
print(partB.head())

partB.plot(kind='bar', x='year', y='avg_number_of_ingredients')
plt.xlabel('year')
plt.ylabel('Average Number of Ingredients')
plt.savefig('partB_year.png')

partB.plot(kind='bar', x='route', y='avg_number_of_ingredients')
plt.xlabel('route')
plt.ylabel('Average Number of Ingredients')
plt.savefig('partB_route.png')
