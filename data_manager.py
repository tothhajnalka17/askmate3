from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_questions(cursor):
    cursor.execute("SELECT * FROM question ORDER BY view_number DESC")
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, id):
    query = (f'SELECT * FROM question WHERE id={id}')
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_answer(cursor, submission_time, vote_number, question_id, message, image):
    cursor.execute("""
    INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
    VALUES(%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s);
                       """,
                   {
                       'submission_time': submission_time,
                       'vote_number': vote_number,
                       'question_id': question_id,
                       'message': message,
                       'image': image})


@database_common.connection_handler
def add_comment_to_question(cursor, submission_time, question_id, message):
    cursor.execute("""
                INSERT INTO comment (submission_time, question_id, message)
                VALUES(%(submission_time)s, %(question_id)s, %(message)s);
                    """,
                   {
                       'submission_time': submission_time,
                       'question_id': question_id,
                       'message': message})


@database_common.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute(f"SELECT * FROM answer WHERE question_id = '{question_id}' ORDER BY id ASC")
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_answer_id(cursor, answer_id):
    cursor.execute(f"SELECT * FROM answer WHERE id = '{answer_id}'")
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor, submission_time, title, message, image):
    cursor.execute("""
                        INSERT INTO comment (submission_time, title, image) 
    VALUES(%(submission_time)s, %(title)s, %(image)s);
                       """,
                   {
                       'submission_time': submission_time,
                       'title': title,
                       'message': message,
                       'image': image})




@database_common.connection_handler
def get_question_id(cursor, id):
    cursor.execute("""
    SELECT * FROM question WHERE id = %(id)s;
                           """,
                   {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def update_question(cursor, title, message, id):
    cursor.execute("""
            UPDATE question
            SET title = %(title)s,
            message = %(message)s
            WHERE id = %(id)s;
            """,
                   {
                       'title': title,
                       'message': message,
                       'id': id, })


@database_common.connection_handler
def update_answer(cursor, message, answer_id):
    cursor.execute("""
            UPDATE answer
            SET message = %(message)s
            WHERE id = %(id)s;
            """,
                   {
                       'message': message,
                       'id': answer_id, })


@database_common.connection_handler
def delete_question(cursor, question_id):
    cursor.execute(f"DELETE FROM question WHERE id = {question_id}")


@database_common.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute(f"SELECT question_id FROM answer where id = {answer_id}")
    for answer in cursor.fetchall():
        return (answer['question_id'])


@database_common.connection_handler
def delete_answer_by_id(cursor, answer_id):
    cursor.execute(f"DELETE CASCADE FROM answer WHERE id = {answer_id}")


@database_common.connection_handler
def search_question(cursor, text):
    cursor.execute(f"SELECT * FROM question WHERE {text} IN question")
    return cursor.fetchall()


@database_common.connection_handler
def add_comment_to_answer(cursor, question_id, answer_id, message, submission_time, edited_count):
    cursor.execute("""
    INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count) 
    VALUES(%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s);
                       """,
                   {
                       'question_id': question_id,
                       'answer_id': answer_id,
                       'message': message,
                       'submission_time': submission_time,
                       'edited_count': edited_count})


@database_common.connection_handler
def view_counting(cursor, question_id):
    cursor.execute("""
            UPDATE question
            SET view_number = (view_number+1)
            WHERE id = %(id)s;
            """,
                   {
                       'id': question_id, })


@database_common.connection_handler
def update_up_vote(cursor, question_id):
    cursor.execute("""
            UPDATE question
            SET vote_number = (vote_number+1)
            WHERE id = %(id)s;
            """,
                   {
                       'id': question_id, })

@database_common.connection_handler
def answer_comment_like(cursor, question_id):
    cursor.execute("""
            UPDATE comment
            SET vote_number = (vote_number+1)
            WHERE id = %(id)s;
            """,
                   {
                       'id': question_id, })

@database_common.connection_handler
def update_down_vote(cursor, question_id):
    cursor.execute("""
            UPDATE question
            SET vote_number = (vote_number-1)
            WHERE id = %(id)s;
            """,
                   {
                       'id': question_id, })


@database_common.connection_handler
def get_question_comment(cursor, question_id):
    cursor.execute("""
                SELECT * FROM comment
                WHERE question_id = %(id)s ORDER BY submission_time DESC;
    """,
                   {
                       'id': question_id
                   })
    return cursor.fetchall()

@database_common.connection_handler
def get_answer_id_by_question_id(cursor, question_id):
    cursor.execute(f"SELECT id FROM answer WHERE question_id = '{question_id}'")
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comment(cursor):
    cursor.execute(f"SELECT message, submission_time FROM comment WHERE answer_id != 0 ")
    return cursor.fetchall()

@database_common.connection_handler
def get_answers(cursor):
    cursor.execute("SELECT * FROM comment")
    return cursor.fetchall()

@database_common.connection_handler
def get_question_by_search(cursor, search_phrase):
    cursor.execute("""
    SELECT * FROM question WHERE title LIKE %(search_phrase)s OR message LIKE %(search_phrase)s;
                       """,
                   {'search_phrase': '%{}%'.format(search_phrase)})
    return cursor.fetchall()


@database_common.connection_handler
def get_question_answer_by_search_phrase(cursor, search_phrase):
    cursor.execute("""
    SELECT answer.question_id FROM answer WHERE answer.message LIKE %(search_phrase)s;
                       """,
                   {'search_phrase': '%{}%'.format(search_phrase)})
    return cursor.fetchall()


@database_common.connection_handler
def get_question_if_answer_contains(cursor, id):
    cursor.execute("""
    SELECT * FROM question WHERE id = %(id)s;
                       """,
                   {'id': int(id)})
    question_if_answer_contains = cursor.fetchall()

    return question_if_answer_contains


@database_common.connection_handler
def get_answer_id_message_by_answer_id(cursor, id):
    cursor.execute("""SELECT
            *
                FROM answer
                WHERE id = %(id)s;
                           """,
                   {'id': id})
    answer_id_message = cursor.fetchall()
    helplist = []
    for element in range(0, len(answer_id_message)):
        helplist.append(answer_id_message[element])

    final_list = []
    for j in range(len(helplist)):
        final_list.append(list(helplist[j].values()))

    return final_list


@database_common.connection_handler
def add_user(cursor, username, email, encrypted_password, register_date):
    cursor.execute("""
    INSERT INTO users (username, email, encrypted_password, register_date) 
    VALUES (%(username)s, %(email)s, %(encrypted_password)s, %(register_date)s);
    """,
    {
        'username': username,
        'email': email,
        'encrypted_password': encrypted_password,
        'register_date': register_date
     })


@database_common.connection_handler
def get_user_by_email(cursor, email):
    cursor.execute("""
    SELECT * FROM users WHERE email = %(email)s;
                           """,
                   {'email': email})
    return cursor.fetchall()


@database_common.connection_handler
def get_user_by_username(cursor, username):
    cursor.execute("""
    SELECT * FROM users WHERE username = %(username)s;
                           """,
                   {'username': username})
    return cursor.fetchall()


@database_common.connection_handler
def get_user_by_userid(cursor, id):
    cursor.execute("""
    SELECT * FROM users WHERE id = %(id)s;
                           """,
                   {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def get_user_encrypted_password(cursor, email):
    cursor.execute("""
    SELECT encrypted_password FROM users WHERE email = %(email)s;
                           """,
                   {'email': email})
    query = cursor.fetchall()
    result = query[0]['encrypted_password']
    return result

@database_common.connection_handler
def get_all_user_details(cursor):
    cursor.execute("""  SELECT
                            *
                        FROM
                            users""")
    return cursor.fetchall()


@database_common.connection_handler
def get_username_by(cursor, email):
    cursor.execute("""
        SELECT username FROM users WHERE email = %(email)s;
                               """,
                   {'email': email})
    return cursor.fetchall()

@database_common.connection_handler
def get_user_id_by(cursor, email):
    cursor.execute("""
        SELECT id FROM users WHERE email = %(email)s;
                               """,
                   {'email': email})
    return cursor.fetchall()


@database_common.connection_handler
def update_comment(cursor, id, message, edited_count, submission_time):
    cursor.execute("""
                UPDATE comment
                SET message = %(message)s,
                edited_count = %(edited_count)s,
                submission_time = %(submission_time)s
                WHERE id = %(id)s;
                """,
                   {
                       'message': message,
                       'id': id,
                       'edited_count': edited_count,
                       'submission_time': submission_time})


@database_common.connection_handler
def get_comment(cursor, comment_id):
    cursor.execute("""
                SELECT * FROM comment
                WHERE id = %(id)s;""",
                   {
                       'id': comment_id
                   })
    return cursor.fetchone()
