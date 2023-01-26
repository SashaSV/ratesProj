from rates import create_app
from flask import request
from rates.model import db, Currancy, Currancy_rates, currancysSchema, ratesSchema
from rates.api import fillTableCurr, get_rate_history, get_external_history_rate
from datetime import datetime

app = create_app()
app.app_context().push()

@app.route('/api/currency/history')
def get_rate_history_rest():
    c_code = request.args.get('code')
    d_from = request.args.get('date_from')

    ratesByfilter = get_rate_history(c_code, d_from)

    return ratesByfilter

@app.route('/allcurrancy')
def get_all_currancy():

    allCurancys = Currancy.query.all()
    return currancysSchema.dump(allCurancys)

# Вернуть все курсы валют за все время
@app.route('/')
@app.route('/allrates')
def get_all_rates():
    if not Currancy.query.first():
        fillTableCurr()

    if not Currancy_rates.query.filter(Currancy_rates.date < datetime.today().date()).first():
        get_external_history_rate(30)

    allRates = Currancy_rates.query.all()
    return ratesSchema.dump(allRates)

# Вернуть все историю курсов валют по фильтру
@app.route('/api/currency/history')
def get_rate_hystory_rest():
    c_code = request.args.get('code')
    d_from = request.args.get('date_from')

    ratesByfilter = get_rate_history(c_code, d_from)

    return ratesByfilter

if __name__ == '__main__':
    db.init_app(app)
    #api.register_blueprint(blp)
    app.run(debug=True)




#import marshmallow as ma
#from flask_smorest import Api, Blueprint, abort
#from flask.views import MethodView


# app.config["API_TITLE"] = "Currancy rates API"
# app.config["API_VERSION"] = "v1"
# app.config["OPENAPI_VERSION"] = "2.1.1"

# api = Api(app)
# blp = Blueprint("rates", "rates", url_prefix="/api", description="Operations on rates")
#
#
# class CurancySchema(ma.Schema):
#     id = ma.fields.Int(dump_only=True)
#     code = ma.fields.String()
#     name = ma.fields.String()
# class CurancyQueryArgsSchema(ma.Schema):
#     code = ma.fields.String()
#     data = ma.fields.String()

# # Вернуть все валюты, по которым сохраняется курс
# @blp.route("/")
# class CurancyAll(MethodView):
#     @blp.response(200, CurancySchema(many=True))
#     def get(self):
#         """List all currency"""
#         return Currancy.query.all()
# @blp.route("/currency/history")
# class RatesHystory(MethodView):
#     #@blp.arguments(CurancyQueryArgsSchema, location="query")
#     @blp.response(200, CurancySchema(many=True))
#     def get(self, c_code, d_from):
#         """Get rates history currency"""
#         return get_rate_hystory(c_code, d_from)