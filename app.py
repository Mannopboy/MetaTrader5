from backend.models.models import *
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from backend.models.models import *
import pprint

app = Flask(__name__)
app.config.from_object('backend.models.config')
db = db_setup(app)
migrate = Migrate(app, db)


def get_current_user():
    user_result = None
    if "username" in session:
        user_result = User.query.filter(User.name == session['username']).first()
    return user_result


def account_status():
    accounts = Account.query.order_by(Account.id).all()
    if accounts:
        for account in accounts:
            current_time = datetime.now()
            if account.status_time:
                time_difference = current_time - account.status_time
                if time_difference > timedelta(seconds=10) and account.status:
                    account.status = False
                    db.session.commit()
            else:
                account.status = False
                db.session.commit()
    return None


@app.route('/register_symbol', methods=['GET', 'POST'])
def register_symbol():
    if request.method == 'POST':
        name = request.form['name']
        new_symbol = Symbol(name=name)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_symbol.html')


@app.route('/register_server', methods=['GET', 'POST'])
def register_server():
    if request.method == 'POST':
        name = request.form['name']
        new_symbol = Server(name=name)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_server.html')


@app.route('/register_type_filling', methods=['GET', 'POST'])
def register_type_filling():
    if request.method == 'POST':
        name = request.form['name']
        new_symbol = TypeFilling(name=name)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_type_filling.html')


@app.route('/register_type_time', methods=['GET', 'POST'])
def register_type_time():
    if request.method == 'POST':
        name = request.form['name']
        new_symbol = TypeTime(name=name)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_type_time.html')


@app.route('/register_action', methods=['GET', 'POST'])
def register_action():
    if request.method == 'POST':
        name = request.form['name']
        new_symbol = Action(name=name)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_action.html')


@app.route('/register_robot', methods=['GET', 'POST'])
def register_robot():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        strategy = request.form['strategy']
        username = session['username']
        user = User.query.filter_by(username=username).first()
        new_symbol = Robot(name=name, user_id=user.id, strategy=strategy)
        db.session.add(new_symbol)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register_robot.html')


@app.route('/status_account/<int:account_id>', methods=['GET'])
def status_account(account_id):
    account = Account.query.filter_by(id=account_id).first()
    account.status = True
    to_date = datetime.now()
    account.status_time = to_date
    db.session.commit()
    return jsonify({
        'status': True
    })


@app.route('/register_account', methods=['GET', 'POST'])
def register_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter(User.username == username).first()
    robots = Robot.query.filter(Robot.user_id == user.id).order_by(Robot.id).all()

    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        device = request.form['device']
        name = request.form['name']
        selected_robot_id = request.form['robot']

        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            if selected_robot_id == '0':
                print(True)
                new_account = Account(account=account, password=password, user_id=user.id, device=device, name=name)
            else:
                new_account = Account(account=account, password=password, user_id=user.id, device=device, name=name,
                                      robot_id=selected_robot_id)
            db.session.add(new_account)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('register_account.html', robots=robots)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Bunday foydalanuvchi mavjud!', 'error')
            return redirect(url_for('register'))
        new_user = User(username=username, name=name, surname=surname)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        get_user = User.query.filter_by(username=username).first()
        if get_user:
            checked = check_password_hash(get_user.password, password)
            if checked:
                session['username'] = get_user.username
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session['username'] = None
    return redirect(url_for('login'))


@app.route('/link_account')
def link_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter(User.username == username).first()
    if not user:
        return redirect(url_for('login'))
    accounts = Account.query.filter(Account.user_id == user.id, Account.robot_id == None).order_by(Account.id).all()
    return render_template("accounts.html", accounts=accounts)


@app.route('/link_robots')
def link_robots():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter(User.username == username).first()
    if not user:
        return redirect(url_for('login'))
    robots = Robot.query.filter(Robot.user_id == user.id).order_by(Robot.id).all()
    return render_template("robots.html", robots=robots)


@app.route('/robot_accounts/<int:robot_id>')
def robot_accounts(robot_id):
    account_status()
    accounts = Account.query.filter(Account.robot_id == robot_id).order_by(Account.id).all()
    return render_template("robot_accounts.html", accounts=accounts)


@app.route("/trades_history/<int:accountId>", methods=["GET"])
def trades_history(accountId):
    account = Account.query.filter(Account.id == accountId).first()
    url = f'http://192.168.68.{account.device}:5001/'
    response = requests.get(url)
    trades = response.json()['list']
    for trade in trades:
        history_trade = TradeHistory.query.filter(TradeHistory.ticket == trade['ticket']).first()
        if not history_trade and trade['profit'] != 0.0 and trade['price'] != 0.0:
            print(trade['profit'])
            new = TradeHistory(
                price=trade['price'],
                ticket=trade['ticket'],
                volume=trade['volume'],
                commission=trade['commission'],
                profit=trade['profit'],
                symbol=trade['symbol'],
                time=trade['time_msc'],
                comment=trade['comment'],
                account_id=accountId
            )
            db.session.add(new)
            db.session.commit()
    trades = TradeHistory.query.filter(TradeHistory.account_id == accountId).order_by(TradeHistory.id).all()
    return render_template("trades_history.html", trades=trades, balance=response.json()['balance'])


@app.route("/trades/<int:accountId>", methods=["GET"])
def trades(accountId):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter(User.username == username).first()
    if not user:
        return redirect(url_for('login'))
    account_b = Account.query.filter(Account.id == accountId).first()
    account = int(account_b.account)
    password = account_b.password
    server = user.server.name
    request_params = {
        'account': account,
        'password': password,
        'server': server,
    }
    url = f'http://192.168.68.{account_b.device}:5000/account_info'
    response = requests.post(url, json=request_params)
    account_data = response.json()['account']
    url = f'http://192.168.68.{account_b.device}:5000/today_trades'
    response = requests.post(url, json=request_params)
    print(account_data)
    print(response.json()['closed_trades'])
    print(response.json()['trades'])
    return render_template("account.html", account=account_data, trades=response.json()['closed_trades'],
                           open_trades=response.json()['trades'])


@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter(User.username == username).first()
    if not user:
        return redirect(url_for('login'))
    symbols = Symbol.query.order_by(Symbol.id).all()
    if request.method == "POST":
        selected_account_ids = request.form.getlist('selected_accounts')
        for selected_account_id in selected_account_ids:
            account_b = Account.query.filter(Account.id == selected_account_id).first()
            account = int(account_b.account)
            password = account_b.password
            server = user.server.name
            symbol = request.form.get("symbol")
            order_type = request.form.get("order_type")
            lot_size = float(request.form.get("lot_size"))
            tp_price = float(request.form.get("tp_price"))
            sl_price = float(request.form.get("sl_price"))
            request_params = {
                'account': account,
                'password': password,
                'server': server,
                "symbol": symbol,
                "volume": lot_size,
                "order_type": order_type,
                "sl_price": sl_price,
                "tp_price": tp_price,
            }
            url = f'http://192.168.68.{account_b.device}:5000/'
            print(url)
            response = requests.post(url, json=request_params)
            print(response)
    user = User.query.filter(User.username == username).first()
    accounts = Account.query.filter(Account.user_id == user.id).order_by(Account.id).all()
    return render_template("index.html", symbols=symbols, accounts=accounts)


if __name__ == "__main__":
    app.run(debug=True)
