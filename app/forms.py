from wtforms import Form, StringField, SelectField
class DrugSearchForm(Form):
    choices = [('Name', 'Name'),
               ('Classification', 'Classification')]
    select = SelectField('', choices=choices)
    search = StringField('', render_kw={"placeholder": "Enter Search Terms"})