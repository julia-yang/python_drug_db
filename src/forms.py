from wtforms import Form, StringField, SelectField
class DrugSearchForm(Form):
    choices = [('Name', 'Name'),
               ('Clinical Category', 'Clinical Category')]
    select = SelectField('', choices=choices)
    search = StringField('', render_kw={"placeholder": "Enter Search Terms"})