import csv
import pandas as pd
from dotenv import load_dotenv
import os
import boto3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_bootstrap import Bootstrap
from forms import DrugSearchForm
from classification_map import CLASSIFICATION_MAPPINGS

load_dotenv()

# initialize drug_product table
csv_cols = [
    'PRODUCT ID',
    'PRODUCT NDC',
    'PRODUCT TYPE NAME',
    'PROPRIETARY NAME',
    'PROPRIETARY NAME SUFFIX',
    'NON-PROPRIETARY NAME',
    'DOSAGE FORM NAME',
    'ROUTE NAME',
    'START MARKETING DATE',
    'END MARKETING DATE',
    'MARKETING CATEGORY NAME',
    'APPLICATION NUMBER',
    'LABELER NAME',
    'SUBSTANCE NAME',
    'ACTIVE NUMERATOR STRENGTH',
    'ACTIVE INGREDIENT UNIT',
    'PHARMACEUTICAL CLASSES',
    'DEA SCHEDULE'
]

s3 = boto3.client(
    's3', 
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')) 

csv_obj = s3.get_object(Bucket="python-drug-db", Key="Drugs_product.csv")
df = pd.read_csv(csv_obj.get("Body"), names=csv_cols, encoding='unicode_escape', header=0)

app = Flask(__name__)
Bootstrap(app)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

@app.route('/', methods=('GET', 'POST'))
def main():
    search = DrugSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    if request.method == 'GET':
        return render_template('index.html', form=search, table=df.head(15).to_html(classes='data'), title='U.S. Drug Product Database')
 
@app.route('/search') 
def search_results(search):
    select_query = search.data['select']
    search_query = search.data['search']
    
    if search_query == '':
        results = df.head(15)
        results_desc = f"Displaying top 15 results ({len(df)} found)"
    else:
        if select_query == 'Name':
            search_query = search_query.lower()
            results = df[
                df['PROPRIETARY NAME'].str.lower().str.contains(search_query, na=False) |
                df['NON-PROPRIETARY NAME'].str.lower().str.contains(search_query, na=False)
            ]
        elif select_query == 'Clinical Category':
            classes = CLASSIFICATION_MAPPINGS.get(search_query.lower())
            if classes:
                mask = pd.Series(False, index=df.index)
                for c in classes:
                    mask |= df['PHARMACEUTICAL CLASSES'].str.contains(c, case=False, na=False)
                results = df[mask]
            else:
                results = pd.DataFrame()
        
        if len(results) == 0:
            results_desc = "No results found."
            return render_template('index.html', form=search, results_desc=results_desc, title='Drug Information Database')
        else:
            results_desc = f"{len(results)} found"
            return render_template('index.html', form=search, results_desc=results_desc, table=results.to_html(classes='data'), title='Drug Information Database')

if __name__ == '__main__':
    app.run(debug=True)	

