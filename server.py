import random

from flask import Flask, session, request, render_template, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import smtplib, ssl
import os
import data_manager
import datetime
import re
import util
# Required for sending email, can be commented out from line 116


email_password = os.environ.get("EMAIL_PASSWORD")
context = ssl.create_default_context()


app = Flask(__name__)
app.secret_key = "sajtosmakaroni"
app.permanent_session_lifetime = datetime.timedelta(minutes=1)


@app.route("/")
def route_home():
    list_question = data_manager.get_questions()
    return render_template("home.html", list_question=list_question)


@app.route("/list")
def route_list():
    list_questions = data_manager.get_questions()
    return render_template("list.html", list_questions=list_questions)


@app.route("/users")
def users_list():
    users_details = data_manager.get_all_user_details()
    return render_template("users.html", users_details=users_details)


@app.route("/question/<int:question_id>", methods=["POST", "GET"])
def get_display_question(question_id):
    question_data = data_manager.get_question_by_id(question_id)
    answer_data = data_manager.get_answers_by_question_id(question_id)
    comment_question_data = data_manager.get_question_comment(question_id)
    comment_answer_data = data_manager.get_answer_comment()

    if request.method == "GET":
        data_manager.view_counting(question_id)

    elif request.method == 'POST':

        if "submit_answer" in request.form:
            submission_time = datetime.datetime.now()
            vote_number = question_data['view_number']
            message = request.form.get("answer")
            image = "something.jpg"
            data_manager.add_answer(submission_time, vote_number, question_id, message, image)
            return redirect(url_for('get_display_question', question_id=question_id))

        elif "submit_comment" in request.form:
            submission_time = datetime.datetime.now()
            message = request.form["message"]
            data_manager.add_comment_to_question(submission_time, question_id, message)
            return redirect(url_for('get_display_question', question_id=question_id))

        elif "likes" in request.form:
            return redirect(url_for('get_display_question', question_id=question_id))

        elif "submit_answer_comments" in request.form:
            submission_time = datetime.datetime.now()
            answer_query = data_manager.get_answers_by_question_id(question_id)
            question_id = None

            print(answer_query)
            answer_id = answer_query['answer_id']
            print(answer_id)
            edited_count = 0
            message = request.form['message']
            data_manager.add_comment_to_answer(question_id, answer_id, submission_time, message, edited_count)
            return redirect(url_for('get_display_question', question_id=question_id))



    return render_template('displayquestion.html', question_id=question_id, question_data=question_data,
                           answer_data=answer_data, comment_answer_data=comment_answer_data, comment_question_data=comment_question_data)




@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "GET":
        question_data = data_manager.get_question_by_id(question_id)
        return render_template('add_answer.html', question_id=question_id, question_data=question_data)
    elif "answer" in request.form:
        if request.method == "POST":
            question_data = data_manager.get_question_by_id(question_id)
            return render_template('add_answer.html', question_id=question_id, question_data=question_data)
    elif "add_answer" in request.form:
        if request.method == "POST":
            submission_time = str(datetime.datetime.now())
            message = request.form.get('message')
            vote_number = 0
            data_manager.add_answer(submission_time, vote_number, question_id, message, image="")
            return redirect(url_for('get_display_question', question_id=question_id))


@app.route("/question/<int:question_id>/new-comment", methods=["POST", "GET"])
def add_comment_to_question(question_id):
    if request.method == "GET":

        question_data = data_manager.get_question_by_id(question_id)
        return render_template('add_comment_to_question.html', question=question_data, question_id=question_id)
    elif request.method == "POST":
        submission_time = datetime.datetime.now()
        message = request.form.get("comment")
        data_manager.add_comment_to_question(submission_time, int(question_id), message)
        return redirect(url_for('get_display_question', question_id=question_id))



@app.route("/answer/<answer_id>/new-comment", methods=["POST", "GET"])
def comment_to_answer(answer_id):
    if request.method == 'POST':
        question_id = None
        message = request.form['comment_answer']
        submission_time = datetime.datetime.now()
        edited_count = None
        data4 = data_manager.get_answer_id_message_by_answer_id(answer_id)



        data_manager.add_comment_to_answer(question_id, int(answer_id), message, submission_time, edited_count)
        return redirect(url_for('get_display_question', question_id=data4[0][3]))





@app.route("/add_question", methods=["POST", "GET"])
def add_question():
    if request.method == "GET":
        return render_template("add_question.html")

    elif request.method == "POST":
        submission_time = datetime.datetime.now()
        view_number = 0
        vote_number = 0
        title = request.form.get("title")
        message = request.form.get("message")
        image = "something"
        data_manager.add_question(submission_time, title, message, image)
        return redirect(url_for('route_list'))

#TODO query probléma
@app.route('/edit/<int:question_id>', methods=['POST', 'GET'])
def get_question(question_id):
    if request.method == "GET":
        question_data = data_manager.get_question_by_id(question_id)
        return render_template('edit_question.html', question_data=question_data)
    elif request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        data_manager.update_question(title, message, question_id)
        return redirect(url_for('route_list'))


@app.route("/delete/<int:question_id>", methods=['POST', 'GET'])
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for('route_list'))


@app.route("/answer/<int:answer_id>/delete", methods=["GET"])
def delete_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.delete_answer_by_id(answer_id)

    return redirect(url_for('get_display_question', question_id=question_id))


@app.route("/answer/<int:answer_id>/edit", methods=['POST', 'GET'])
def edit_answer(answer_id):
    if request.method == "GET":
        answers = data_manager.get_answers_by_answer_id(answer_id)
        return render_template('edit_answer.html', answers=answers)

    elif request.method == "POST":
        message = request.form['edit_answer']
        data_manager.update_answer(message, answer_id)
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        return redirect(url_for('get_display_question', question_id=question_id))


@app.route("/question/<int:question_id>/vote-up", methods=["POST", "GET"])
def vote_up(question_id):
    data_manager.update_up_vote(question_id)
    return redirect(url_for('get_display_question', question_id=question_id))


@app.route("/question/<int:question_id>/vote-down", methods=["POST", "GET"])
def vote_down(question_id):
    data_manager.update_down_vote(question_id)
    return redirect(url_for('get_display_question', question_id=question_id))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form.get('username')
        email = request.form.get('email')
        original_password = request.form.get('password')

        isUsernameTaken = data_manager.get_user_by_username(request.form.get('username'))
        isEmailTaken = data_manager.get_user_by_email(request.form.get('email'))
        usernameRegex = re.compile(r'[A-Za-z0-9]+')
        emailRegex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

        if isUsernameTaken:
            flash('this username is already in use')
            return render_template('register.html')

        elif isEmailTaken:
            flash('this email is already in use')
            return render_template('register.html')

        elif not request.form.get("username") or not request.form.get("email") or not request.form.get("password"):
            flash('Fill out the registration form properly!')
            return render_template('register.html')

        elif not re.fullmatch(emailRegex, email):
            flash('Invalid email address!')
            return render_template('register.html')

        elif not re.match(usernameRegex, username):
            flash('Username must contain only characters and numbers!')
            return render_template('register.html')

        elif len(username) <= 2:
            flash('Username must be at least 2 characters long!')
            return render_template('register.html')

        elif len(original_password) <= 6:
            flash('Password must be at least 6 characters long!')
            return render_template('register.html')

        else:
            # Handle registration, adding to DB
            encrypted_password = util.hash_password(original_password)
            register_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_manager.add_user(username, email, encrypted_password, register_date)
            flash('Registration successful!')
            return redirect(url_for('route_home'))

    elif request.method == 'POST':
        # Form is empty
        flash('Please fill out the form!')
        return render_template('register.html')

    else:
        return render_template('register.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        account = data_manager.get_user_by_email(email)
        print(account)

        if account:
            encrypted_password = data_manager.get_user_encrypted_password(email)
            session.permanent = True
            userdata = data_manager.get_username_by(email)
            for username in userdata[0].values():
                pass
            session['username'] = username

            userid = data_manager.get_user_id_by(email)
            for id in userid[0].values():
                pass
            session['id'] = id
            print(id)
            # If account exists in users table in out database
            if util.verify_password(password, encrypted_password):
                print("Passwords match")
                # Create session data, we can access this data in other routes
                # Redirect to home page
                return redirect(url_for('route_home'))
            elif 'user' in session:
                return redirect(url_for('route_home'))

            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
                return redirect(url_for('userlogin'))
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
            return redirect(url_for('userlogin'))

    return render_template('login.html')


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user(user_id):
    if 'username' in session:
        userdata = data_manager.get_user_by_userid(session['id'])
        return render_template('profile.html', userdata=userdata)
    else:
        return render_template('profile.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    user = session['username']
    flash(f'Goodbye {user}')
    session.pop("username", None)
    return redirect(url_for('route_home'))


@app.route("/search", methods=['POST', 'GET'])
def search():
    search_phrase = request.args.get('search-phrase')

    if search_phrase:
        question = data_manager.get_question_by_search(search_phrase)
        q_id = data_manager.get_question_answer_by_search_phrase(search_phrase)

        helplist = []
        for item in range(0, len(q_id)):
            for index in q_id[item].values():
                helplist.append(index)

        another_list = []
        for j in helplist:
            another_list.append(data_manager.get_question_if_answer_contains(j))

        final_list = []
        for j in another_list:
            for k in j:
                final_list.append(list((k.values())))

        if question or final_list:
            question_final = list(question)
            help_list = []
            for i in range(0, len(question_final)):
                help_list.append((list(question_final[i].values())))
            question_final = help_list
            final_list = final_list
        else:
            question_final = ""
            final_list = ""
    else:
        question_final = ""
        final_list = ""

    return render_template('home.html', list_searched_items=question_final, list_searched_answer=final_list, searched_phrase=search_phrase)


if __name__ == "__main__":
    app.run(
        debug=True
    )
