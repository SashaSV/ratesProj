from rates import db, marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema

# Таблица с валютами, по которым необходимо хранить курсы
class Currancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True)
    name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    number = db.Column(db.Integer)

    def __init__(self, code, name, country, number):
        self.code = code
        self.name = name
        self.country = country
        self.number = number

    def __repr__(self):
        return '%r' % self.code

# Таблица с курсами валют на дату
class CurrancySchema(SQLAlchemySchema):
    class Meta:
        model = Currancy

    id = marshmallow.auto_field()
    code = marshmallow.auto_field()
    name = marshmallow.auto_field()
    country = marshmallow.auto_field()
    number = marshmallow.auto_field()

currancySchema = CurrancySchema()
currancysSchema = CurrancySchema(many=True)

# Таблица с курсами валют на дату
class Currancy_rates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_curr = db.Column(db.Integer, db.ForeignKey('currancy.id'), nullable=True) # код курса валют по Currancy
    #id_curr = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL(15,4)) # курс валют
    date = db.Column(db.Date) # дата курса валют
    curr = db.relationship('Currancy', backref='currancy', lazy=True)

    def __init__(self, id_curr, rate, date):
        self.id_curr = id_curr
        self.rate = rate
        self.date = date

    def __repr__(self):
        return 'Date {0}, Rate {1}, {2}'.format(self.date, str(self.rate), self.id_curr)

class Currancy_ratesSchema(SQLAlchemySchema):
    class Meta:
        model = Currancy_rates

    id = marshmallow.auto_field()
    rate = marshmallow.auto_field()
    date = marshmallow.auto_field()
    curr = marshmallow.HyperlinkRelated("curr_detail")
    curr = marshmallow.Nested(CurrancySchema)

ratesSchema = Currancy_ratesSchema(many=True)