import os
from flask import Flask, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Boolean, Column, ForeignKey, DateTime, or_, and_, desc, func, ARRAY, JSON
import MetaTrader5 as mt5
from sqlalchemy import *

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'your_secret_key_here'

# Ma'lumotlar bazasi sozlamalari
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123')
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_NAME = os.getenv('DB_NAME', 'database_mt5')
database_path = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_path

# SQLAlchemy obyekti
db = SQLAlchemy(app)


# Foydalanuvchi modelini yaratish
class User(db.Model):
    id = Column(Integer, primary_key=True)
    server_name = Column(String)
    account = Column(String)
    password = Column(String)
    admin = True


with app.app_context():
    db.create_all()


@app.route('/main')
def main():
    server_name = "Exess-MT5Trial"
    password = "Shokh_01212005"
    account = "241068515"
    admin = True
    add = User(server_name=server_name, account=account, password=password, admin=admin)
    db.session.add(add)
    db.session.commit()
    return render_template('index.html')


# Flask marshruti
@app.route("/", methods=["GET", "POST"])
def index():
    # MT5 ga ulanish
    if not mt5.initialize():
        flash(f"MT5 ga ulanishda xato: {mt5.last_error()}", "error")
        return render_template("index.html", symbols=[])

    # Valyuta juftliklari ro'yxati
    symbols = ["EURUSDm", "XAUUSDm", "GBPUSDm", "DXYm"]

    if request.method == "POST":
        try:
            # Foydalanuvchi ma'lumotlarini olish
            account = int(request.form.get("account"))
            password = request.form.get("password")
            server = request.form.get("server")
            symbol = request.form.get("symbol")
            order_type = request.form.get("order_type")
            lot_size = float(request.form.get("lot_size"))
            tp_price = float(request.form.get("tp_price"))
            sl_price = float(request.form.get("sl_price"))

            # Hisobga ulanish
            if not mt5.login(account, password, server=server):
                flash(f"Hisobga ulanishda xato: {mt5.last_error()}", "error")
                mt5.shutdown()
                return render_template("index.html", symbols=symbols)

            # Valyuta juftligini faollashtirish
            if not mt5.symbol_select(symbol, True):
                flash(f"{symbol} faollashtirilmadi. Xato: {mt5.last_error()}", "error")
                mt5.shutdown()
                return render_template("index.html", symbols=symbols)

            # Narxni olish va savdo buyurtmasini sozlash
            price = mt5.symbol_info_tick(symbol).ask if order_type == "BUY" else mt5.symbol_info_tick(symbol).bid
            order_type_mt5 = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL

            request_params = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type_mt5,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 234000,
                "comment": "Flask orqali savdo",
                "type_filling": mt5.ORDER_FILLING_IOC,
                "type_time": mt5.ORDER_TIME_GTC,
            }

            # Savdo buyurtmasini yuborish
            result = mt5.order_send(request_params)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                flash(f"Xatolik: {result.retcode}, {result.comment}", "error")
            else:
                flash(f"Buyurtma muvaffaqiyatli yuborildi: {order_type}, Narx: {price}, TP: {tp_price}, SL: {sl_price}",
                      "success")

        except Exception as e:
            flash(f"Xato yuz berdi: {str(e)}", "error")
        finally:
            mt5.shutdown()

    return render_template("index.html", symbols=symbols)


if __name__ == "__main__":
    app.run(debug=True)
