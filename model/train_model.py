import pandas as pd 
import pickle

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.ensemble import RandomForestRegressor

# /load data 
data = pd.read_csv('data/model.csv')
# feature and target 
x = data[['prev_day_sales', 'avg_last_3_days', 'day', 'item']]
y= data['quantity']

# preprocessing 
num_data = ['prev_day_sales', 'avg_last_3_days']
cat_data = ['day', 'item']

preprocessor = ColumnTransformer([
      ('num',StandardScaler(),num_data),
      ('cat',OneHotEncoder(),cat_data)
])

# concept of the pipe line 
pipe = Pipeline([
    ('preprocessing', preprocessor),
    ('regression', RandomForestRegressor(n_estimators=100))
])
# train the model 
pipe.fit(x,y)
pickle.dump(pipe,open('model/model.pkl','wb'))
print('model trained succesfully !')




