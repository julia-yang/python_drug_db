from flask import Flask, render_template, request, url_for, flash, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy 
from flask_bootstrap import Bootstrap
from forms import DrugSearchForm
from classification_map  import CLASSIFICATION_MAPPINGS

import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# secret_url = os.environ.get('SECRET_URL')
secret_url = "sqlite:///fda.db"
app = Flask(__name__)
Bootstrap(app)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = secret_url
engine = sqlalchemy.create_engine(secret_url)

csv_cols = [
    'PRODUCT ID',
    'PRODUCT TYPE NAME',
    'PROPRIETARY NAME',
    'PROPRIETARY NAME SUFFIX',
    'NON-PROPRIETARY NAME',
    'DOSAGE FORM NAME',
    'ROUTE NAME',
    'LABELER NAME',
    'SUBSTANCE NAME',
    'PHARMACEUTICAL CLASSES',
    'DEA SCHEDULE'
]

db = SQLAlchemy(app)
class DrugProduct(db.Model):
    __tablename__ = "drug_product"
    __table_args__ = {'extend_existing': True}
    product_id = db.Column('PRODUCT ID', db.Text, primary_key=True)
    product_type_name = db.Column('PRODUCT TYPE NAME', db.Text)
    proprietary_name = db.Column('PROPRIETARY NAME', db.Text)
    proprietary_name_suffix = db.Column('PROPRIETARY NAME SUFFIX', db.Text)
    non_proprietary_name = db.Column('NON-PROPRIETARY NAME', db.Text)
    dosage_form = db.Column('DOSAGE FORM NAME', db.Text)
    route = db.Column('ROUTE NAME', db.Text)
    labeler = db.Column('LABELER NAME', db.Text)
    substance = db.Column('SUBSTANCE NAME', db.Text)
    pharm_classes = db.Column('PHARMACEUTICAL CLASSES', db.Text)          #comma-separated strings
    dea_schedule = db.Column('DEA SCHEDULE', db.Text)

    
df = pd.read_csv('drug_products.csv', usecols=csv_cols, encoding = 'unicode_escape')[csv_cols]
df.to_sql('drug_product', con=engine, if_exists='replace', index=False)


admin = Admin(app, name='Drug Database Admin Page', template_mode='bootstrap3')
admin.add_view(ModelView(DrugProduct, db.session))
search_query = ''

@app.route('/', methods=('GET', 'POST'))
def main():
    search = DrugSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    if request.method == 'GET':
        table=df.head(15)
    return render_template('index.html', form=search, table=table.to_html(classes='data'), title='U.S. Drug Product Database')

@app.route('/search') 
def search_results(search):
    select_query = search.data['select']
    search_query = search.data['search']
    if search_query == '':
        results = db.session.query(DrugProduct).limit(15).all()
        results_desc = "Displaying top 15 results (" + str(db.session.query(DrugProduct).count()) + " found)"
    else:
        if select_query == 'Name':
            search_query=f'%{search_query}%'
            results = db.session.query(DrugProduct).filter(DrugProduct.proprietary_name.ilike(search_query) 
                                                        | DrugProduct.non_proprietary_name.ilike(search_query))
        elif select_query == 'Clinical Category':
            classes = CLASSIFICATION_MAPPINGS.get(search_query.lower())
            if classes:
                results = db.session.query(DrugProduct).filter(sqlalchemy.or_(*[DrugProduct.pharm_classes.ilike(f'%{c}%') for c in classes]))
            else:
                results = None  
        if not results:
            results_desc = "No results found."
            return render_template('index.html', form=search, results_desc=results_desc, title='Drug Information Database')
        else:
            results_desc = str(results.count()) + ' found'
            result_df = pd.read_sql(sql=results.statement, con=engine)
            return render_template('index.html', form=search, results_desc=results_desc, table=result_df.to_html(classes='data'), title='Drug Information Database')
if __name__ == '__main__':
    app.run(debug=True)	

