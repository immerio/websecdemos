from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, flash
import json

app = Blueprint('paramtamp', __name__)


@app.route('/paramtamp')
def login_page():
    if session.get('paramtamploggedin') != "True":
        return render_template('login.html', page='paramtamp')
    else:
        return render_template('param_tampering_profile.html', 
                          username=session['param_user'],
                          firstname=session['param_firstname'],
                          lastname=session['param_lastname'],
                          is_admin=session['param_is_admin'])

@app.route('/paramtamp', methods=['POST'])
def login():
    # Get credentials from form
    username = request.form['username']
    password = request.form['password']
	
    if 'user' in username.lower() and 'user' in password.lower():
        session['paramtamploggedin'] = "True"
        session['param_user'] = username
        session['param_firstname'] = "Normal"
        session['param_lastname'] = "User"
        session['param_is_admin'] = False  # Default to non-admin
        return redirect(url_for('paramtamp.profile'))
    else:
        return render_template('login.html', page='paramtamp', incorrect=True)

@app.route('/paramtamp/profile')
def profile():
    if session.get('paramtamploggedin') != "True":
        return redirect(url_for('paramtamp.login_page'))
    
    return render_template('param_tampering_profile.html', 
                          username=session['param_user'],
                          firstname=session['param_firstname'],
                          lastname=session['param_lastname'],
                          is_admin=session['param_is_admin'])

@app.route('/paramtamp/update_profile', methods=['POST'])
def update_profile():
    if session.get('paramtamploggedin') != "True":
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    # Vulnerable implementation - directly accepts all data from request JSON
    data = request.get_json()
    
    # Update session data
    if 'firstname' in data:
        session['param_firstname'] = data['firstname']
    if 'lastname' in data:
        session['param_lastname'] = data['lastname']
    
    # VULNERABLE: This allows parameter tampering to set admin privileges
    # Default to current admin status if not specified
    if 'is_admin' in data:
        session['param_is_admin'] = data['is_admin']
    elif 'isadmin' in data:
        session['param_is_admin'] = data['isadmin']
    elif 'isAdmin' in data:
        session['param_is_admin'] = data['isAdmin']
    elif 'admin' in data:
        session['param_is_admin'] = data['admin']
    
    # Return the updated user data to be saved in localStorage by the client
    response_data = {
        "status": "success",
        "user_data": {
            "firstname": session['param_firstname'],
            "lastname": session['param_lastname'],
            "is_admin": session['param_is_admin']
        }
    }
    
    return jsonify(response_data)

@app.route('/paramtamp/admin')
def admin_panel():
    if session.get('paramtamploggedin') != "True":
        return redirect(url_for('paramtamp.login_page'))
    
    # Check if user is admin
    if not session.get('param_is_admin', False):
        flash("Access denied: Admin privileges required")
        return redirect(url_for('paramtamp.profile'))

    
    return render_template('param_tampering_admin.html', 
                          username=session['param_user'],
                          firstname=session['param_firstname'],
                          lastname=session['param_lastname']                          
                          )

