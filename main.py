import pandas as pd
from flask import Flask, render_template, request
import pickle
from flask_cors import CORS,cross_origin
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from sklearn.compose import ColumnTransformer

app = Flask(__name__)
data = pd.read_csv('Cleaned_Car_data.csv')
model=pickle.load(open('LinearRegressionModel.pkl','rb'))

@app.route('/')
def home():
    companies = sorted(data['company'].unique())
    car_models = sorted(data['name'].unique())
    year = sorted(data['year'].unique(), reverse=True)
    fuel_type = data['fuel_type'].unique()

    companies.insert(0,'Select Company')


    # company= request.args.get('company') 
    # car_model=request.args.get('car_models')
    # years=request.args.get('year')
    # fuel_types =request.args.get('fuel_type')
    # driven=request.form.get('kilo_driven')

    
    # # prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
    # #                           data=np.array([car_model,company,years,driven,fuel_types]).reshape(1, 5)))

    # if company is None:
    #     output=None
    # else:
    #     prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
    #                           data=np.array([car_model,company,years,driven,fuel_types]).reshape(1, 5)))
    #     output=round(prediction[0],2)
    #     # print(output)



    # print(model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'])))

     



    return render_template('index.html' , companies=companies, car_models=car_models, year=year, fuel_type=fuel_type)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    company=request.form.get('company')

    car_model=request.form.get('car_models')
    year=request.form.get('year')
    fuel_type=request.form.get('fuel_type')
    driven=request.form.get('kilo_driven')

    
    prediction=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                              data=np.array([car_model,company,year,driven,fuel_type]).reshape(1, 5)))
    print(prediction)
    return str(np.round(prediction[0],2))


    if __name__ == '__main__':
        app.run(debug=True)