# import pandas as pd
# import pickle

# with open('model/model.pkl', 'rb') as f:
#     model = pickle.load(f)

# def predict_demand(prev_day_sales, avg_last_3_days, day, item):
    
#     data = pd.DataFrame([{
#         'prev_day_sales': prev_day_sales,
#         'avg_last_3_days': avg_last_3_days,
#         'day': day,
#         'item': item
#     }])
    
#     prediction = model.predict(data)
#     return round(prediction[0], 2)



