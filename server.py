import flask
from flask import request
import random
import os
id_length = 35
forms = []
blocklist_file = "blocked.txt"
blocked_ips = set()
def getFormFromId(id):
    for item in forms:
        if item[0] == id:
            return item
    return None
def make_id(avoid, idlen):
    while True:
        new_id = "".join(str(random.randint(0, 9)) for _ in range(idlen))
        if new_id not in avoid:
            print('Using ID: ' + new_id)
            return new_id
        else:
            print('Not using ID: ' + new_id)
def get_client_ip():
    # Works behind Codespaces, Snap, Cloudflare, Nginx, etc.
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr

def load_blocklist():
    if not os.path.exists(blocklist_file):
        return

    with open(blocklist_file, "r") as f:
        for line in f:
            ip = line.strip()
            if ip:
                blocked_ips.add(ip)

def save_blocklist():
    with open(blocklist_file, "w") as f:
        for ip in blocked_ips:
            f.write(ip + "\n")
def saveToDictionary(title, msg, questions, id=None):
    usedIds = []
    for entry in forms:
        usedIds.append(entry[0])
        print('Max Forms: ' + str(10**id_length))
        print('Current Forms: ' + str(len(usedIds)))
    if len(usedIds) >= 10**id_length:
        print('TOO MANY FORMS!')
        return 'ERROR! Cannot make ID: Too many forms'
    if id == None:
        id = make_id(usedIds, id_length)
        print('ID: ' + id)
    dictLine = [id, title, msg]
    for k in questions:
        dictLine.append(k)
    forms.append(dictLine)
    return id
def load():
    try:
        with open('forms.txt', 'r') as file:
            try:
                for rawLine in file:
                    line = rawLine.strip('\n')
                    if line != '' and line != None and line != ',':
                        forms.append(line.split(','))
                    else:
                        print('Line appears to be blank.')
            except:
                print('File appears malformed!')
                raise OSError 
    except OSError:
        print('CANNOT LOAD! Trying to (re)create file')
        with open('forms.txt', 'w') as file:
            file.close()
        print('File (re)created. Retrying load...')
        load()

def save():
    with open('forms.txt', 'w') as file:
        for form in forms:
            line = ",".join(form)
            file.write(line + "\n")
load()
print(f'Successfully loaded: {forms}')
app = flask.Flask(__name__)
@app.before_request
def block_sensitive_paths():
    ip = get_client_ip()
    p = request.path

    # Already blocked
    if ip in blocked_ips:
        print(f'Blocked {ip} from accessing website due to ip being present on blocklist.')
        flask.abort(403, 'You are on our blocklist.')

    forbidden = (
        p.startswith("/.") or
        "/.git" in p or
        p.startswith("/.ssh") or
        p.startswith("/.aws")
    )

    if forbidden:
        print(f"Blocking IP: {ip} for path: {p}")
        blocked_ips.add(ip)
        save_blocklist()
        flask.abort(403, 'You have been blocked for attempting to access sensitive routes.')
@app.route('/')
def index():
    return flask.render_template('home.html')
@app.route('/create/<form_name>')
def create_form(form_name):
    msg = flask.request.args.get('msg')
    questions = flask.request.args.get('q')
    if msg == None or questions == None or form_name == None:
        print('400 when creating.')
        return '400 Bad Request'
    if ',' in questions:
        questions = questions.split(',')
    print(f'Saving {form_name} to internal dictionary')
    id = saveToDictionary(form_name, msg, questions)
    if 'ERROR' in id.upper():
        error = id
        print('Error saving! Error: ' + error)
        return f'Sorry, there was a error. Please try again later, we are working our hardest to fix it.</br>DEVELOPER INFO:</br>Error while creating. In saveToDictionary(): {error}'
    print('Updating file...')
    save()
    return f'Form ID: {id}'
from flask import render_template, request

@app.route("/form/<id>")
def form(id):
    form = getFormFromId(id)
    form_name = form[1]
    msg = form[2]
    q = form[3:]

    return render_template("form.html",
                           form_name=form_name,
                           msg=msg,
                           q=q,
                           id=id)
@app.route("/answer/<id>/<int:question_answered>")
def answer(id, question_answered):
    answer = request.args.get("answer", "")
    print(f"Form {id} — Q{question_answered} answered: {answer}")
    return f"SUBMITTING...<script>location.replace('{flask.url_for('form', id=id)}')</script>"
@app.route('/blocked')
def view_forms():
    return list(blocked_ips)
if __name__ == '__main__':
    load_blocklist()
    app.run(host='0.0.0.0')