from flask import request
import db

def create_account():
    if request.method != "POST":
        return {}
    new_user = db.User(request.form.get("username"), request.form.get("email"), request.form.get("password"))
    db.db.session.add(new_user)
    db.db.session.commit()
    return {"message": "User created successfully.",
            "username": request.form.get("username")}
