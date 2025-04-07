from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import String, Integer, Column, ForeignKey, BigInteger, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

db = SQLAlchemy()


def db_setup(app):
    app.config.from_object('backend.models.config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String)
    username = Column(String)
    deviation = Column(Integer)
    admin = True
    server_id = Column(Integer, ForeignKey('server.id'))
    accounts = relationship('Account', backref="user", order_by="Account.id")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "username": self.username,
            "deviation": self.deviation,
            "admin": self.admin,
            "server_id": self.server_id,
            "accounts": [account.convert_json() for account in self.accounts] if entire else None
        }


class Server(db.Model):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship('User', backref="server", order_by="User.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "users": [user.convert_json(entire) for user in self.users] if entire else None
        }


class Action(db.Model):
    __tablename__ = "action"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    trades = relationship('Trade', backref="action", order_by="Trade.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "trades": [trade.convert_json() for trade in self.trades] if entire else None
        }


class TypeTime(db.Model):
    __tablename__ = "type_time"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    trades = relationship('Trade', backref="type_time", order_by="Trade.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "trades": [trade.convert_json() for trade in self.trades] if entire else None
        }


class TypeFilling(db.Model):
    __tablename__ = "type_filling"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    trades = relationship('Trade', backref="type_filling", order_by="Trade.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "trades": [trade.convert_json() for trade in self.trades] if entire else None
        }


class Symbol(db.Model):
    __tablename__ = "symbol"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    trades = relationship('Trade', backref="symbol", order_by="Trade.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "trades": [trade.convert_json() for trade in self.trades] if entire else None
        }


class Account(db.Model):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    account = Column(String)
    password = Column(String)
    device = Column(Integer)
    name = Column(String)
    status = Column(Boolean, default=False)
    status_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    robot_id = Column(Integer, ForeignKey('robot.id'))
    trades = relationship('Trade', backref="account", order_by="Trade.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "account": self.account,
            "password": self.password,
            "user_id": self.user_id,
            "trades": [trade.convert_json() for trade in self.trades] if entire else None
        }


class Robot(db.Model):
    __tablename__ = "robot"
    id = Column(Integer, primary_key=True)
    strategy = Column(String)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))

    def convert_json(self):
        return {
            "id": self.id,
            "strategy": self.strategy,
            "status": self.status,
            "name": self.name,
            "user_id": self.user_id,
        }


class Trade(db.Model):
    __tablename__ = "trade"
    id = Column(Integer, primary_key=True)
    order_type = Column(String)
    lot_size = Column(Integer)
    tp_price = Column(Integer)
    sl_price = Column(Integer)
    price = Column(BigInteger)
    type = Column(String)
    magic = Column(Integer)
    symbol_id = Column(Integer, ForeignKey('symbol.id'))
    action_id = Column(Integer, ForeignKey('action.id'))
    type_filling_id = Column(Integer, ForeignKey('type_filling.id'))
    type_time_id = Column(Integer, ForeignKey('type_time.id'))
    account_id = Column(Integer, ForeignKey('account.id'))

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "order_type": self.order_type,
            "lot_size": self.lot_size,
            "tp_price": self.tp_price,
            "sl_price": self.sl_price,
            "price": self.price,
            "type": self.type,
            "magic": self.magic,
            "symbol_id": self.symbol_id,
            "action_id": self.action_id,
            "type_filling_id": self.type_filling_id,
            "type_time_id": self.type_time_id,
            "account_id": self.account_id,
        }


class TradeHistory(db.Model):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    ticket = Column(Integer)
    volume = Column(Float)
    commission = Column(Float)
    profit = Column(Float)
    symbol = Column(String)
    time = Column(DateTime)
    comment = Column(String)
    account_id = Column(Integer, ForeignKey('account.id'))

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "order_type": self.order_type,
            "lot_size": self.lot_size,
            "tp_price": self.tp_price,
            "sl_price": self.sl_price,
            "price": self.price,
            "type": self.type,
            "magic": self.magic,
            "symbol_id": self.symbol_id,
            "action_id": self.action_id,
            "type_filling_id": self.type_filling_id,
            "type_time_id": self.type_time_id,
            "account_id": self.account_id,
        }
