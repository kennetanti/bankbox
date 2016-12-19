import db
import bitcoin
import random
from datetime import datetime
from flask import request

def send_transaction(from_addr, to_addr, amount):
    fee = 777
    pubfrom = bitcoin.pubtoaddr(bitcoin.privtopub(from_addr))
    change_wallet = generate_wallet()
    h = bitcoin.history(from_addr)
    input_amt = 0
    for hh in h:
        if 'spend' not in hh.keys():
            input_amt += hh["value"]
    outs = [{'value': amount, 'address': to_addr}]
    left = input_amt - amount - fee
    change_wallet.balance = left
    tx = mksend(h,outs,change_addr,fee)
    tx2 = sign(tx,0,from_addr)
    tx3 = sign(tx2,1,from_addr)
    return pushtx(tx3)

def generate_wallet():
    privkey = bitcoin.sha256(''.join(random.choice("1234567890-=qwertyuiop[]asdfghjklzxcvbnm,./!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKLZXCVBNM<>?") for _ in range(64)))
    pubkey = bitcoin.privtopub(privkey)
    pubaddr = bitcoin.pubtoaddr(pubkey)
    key= db.Wallet(privkey, pubaddr)
    db.db.session.add(key)
    return key

def new_deposit(user):
    wallet = generate_wallet()
    bk = db.BitKey(user, wallet.privkey, wallet.pubkey)
    ledger_entry = db.Ledger(user, 0, wallet.pubkey)
    db.db.session.add(bk)
    db.db.session.add(ledger_entry)
    db.db.session.commit()
    return {"address": pubaddr}

def check_deposit(myuser):
    bk = db.BitKey.query.filter_by(pubkey=requests.args.get("pub")).first()
    if bk.user != myuser:
        return {"error": "access violation"}
    history = bitcoin.history(bk.pubkey)
    if len(history) > 0:
        value = history[0]['value']
        if not bk.finished:
            myuser.balance += value
            ledger = db.Ledger.query.filter_by(reason=bk.pubkey).first()
            ledger.time_final = datetime.utcnow()
            ledger.ending_balance = myuser.balance
            ledger.amount = value
            ledger.success = True
            bk.finished = True
            wallet = db.Wallet.query.filter_by(pubkey=bk.pubkey).first()
            wallet.balance += value
            #send_transaction(bk.privkey, MASTER_ADDR, value)
            db.db.session.commit()
        return {"value": value}
    return {"value": "no"}

def withdraw(user):
    amount = request.args.get("amount")
    sendto = request.args.get("pub_out")
    if user.balance > amount:
        user.balance -= amount
        ledger = db.Ledger(user, -1*amount, sendto)
        ledger.ending_balance = user.balance
        ledger.success = True
        ledger.time_final = datetime.utcnow()
        source_wallet = db.Wallet.query.filter(db.Wallet.balance > amount+1000).first()
        source_wallet.balance = 0
        send_transaction(source_wallet.privkey, sendto, amount)
        db.db.session.add(ledger)
        db.db.session.commit()
        #send_transaction(MASTER_PRIVKEY, sendto, amount)
        return {"amount": amount, "sent_to": sendto}
    return {"error": "insufficient funds"}
