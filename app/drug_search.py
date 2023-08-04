from flask import Flask, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy 
from flask_bootstrap import Bootstrap

import pandas as pd

secret_url = 'mysql+pymysql://admin:testeradmin@database-2.clwep7hsnc47.us-east-1.rds.amazonaws.com:3306/drugdb'
app = Flask(__name__)
Bootstrap(app)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config['SECRET_KEY'] = '8555486146236c44c97d1f5b1d9f90ae384edb39c9208148'
app.config['SQLALCHEMY_DATABASE_URI'] = secret_url
engine = sqlalchemy.create_engine(secret_url)

csv_cols = [
    'PRODUCT ID',
    'PRODUCT TYPE NAME',
    'PROPRIETARY NAME',
    'NON-PROPRIETARY NAME',
    'PROPRIETARY NAME SUFFIX',
    'DOSAGE FORM NAME',
    'ROUTE NAME',
    'LABELER NAME',
    'SUBSTANCE NAME',
    'PHARMACEUTICAL CLASSES',
    'DEA SCHEDULE'
]

db_cols = [
    'product_id',
    'product_type_name',
    'proprietary_name',
    'proprietary_name_suffix',
    'non_proprietary_name',
    'dosage_form',         # comma-separated strings
    'route',
    'labeler',
    'substance',
    'pharm_classes',             # comma-separated strings
    'dea_schedule'
]

db = SQLAlchemy(app)
class DrugProduct(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_type_name = db.Column(db.Text)
    proprietary_name = db.Column(db.Text)
    proprietary_name_suffix = db.Column(db.Text)
    non_proprietary_name = db.Column(db.Text)
    dosage_form = db.Column(db.Text)
    route = db.Column(db.Text)
    labeler = db.Column(db.Text)
    substance = db.Column(db.Text)
    pharm_classes = db.Column(db.Text)          #comma-separated strings
    dea_schedule = db.Column(db.Text)

    
df = pd.read_csv('C:/Users/JD/Desktop/Drug_Lookup/app/drug_products.csv', usecols=csv_cols)[csv_cols]
df.columns=db_cols
df.to_sql('drug_product', con=engine, if_exists='replace', index=False)


admin = Admin(app, name='Drug Database Admin Page', template_mode='bootstrap3')
admin.add_view(ModelView(DrugProduct, db.session))
search_query = ''

@app.route('/', methods=('GET', 'POST'))
def home():
    #drug_products = db.session.query(DrugProduct).all()

    if request.method == 'POST':
        search_query = request.form['search_query']
        search_query += search_query
        print(search_query)
        table= df.loc[(df['proprietary_name'].contains(search_query)) | df['non_proprietary_name'.contains(search_query)]]
    else:
        table=df.head(15)
    return render_template('home.html', header=csv_cols, table=table.to_html(classes='data', header=False), title='Drug Information Database')

if __name__ == '__main__':
    app.run(debug=True)	

