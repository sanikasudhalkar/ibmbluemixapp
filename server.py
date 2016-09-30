import os
from flask import Flask, render_template, session, request
import json
import swiftclient


app = Flask(__name__)

global container_name
container_name = 'quiz1'

@app.before_first_request
def initialize():
    if 'VCAP_SERVICES' in os.environ:
        cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['Object-Storage'][0]
        objectstorage_creds = cloudant_service['credentials']
        if objectstorage_creds:
            auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
            password = objectstorage_creds['password']  # password
            project_id = objectstorage_creds['projectId']  # project id
            user_id = objectstorage_creds['userId']  # user id
            region_name = objectstorage_creds['region']  # region name

        # get DB credentials
        cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['cleardb'][0]
        db_creds = cloudant_service['credentials']
        if db_creds:
            host = db_creds['hostname']
            port = db_creds['port']
            username = db_creds['username']
            password = db_creds['password']
    else:
        auth_url = 'https://identity.open.softlayer.com/v3'  # authorization URL
        password = 'mvY^E1f7LehBKXl)'  # password
        project_id = 'cd717d0e921146299e44976a1717b945'  # project id
        user_id = 'a8674bd913fa4ad7955b662e6917c4f8'  # user id
        region_name = 'dallas'  # region name

    global conn
    conn = swiftclient.Connection(key=password,
                              authurl=auth_url,
                              auth_version='3',
                              os_options={"project_id": project_id,
                                          "user_id": user_id,
                                          "region_name": region_name})

    container_name = 'quiz1'
    conn.put_container(container_name)


@app.route('/')
def index():
    return render_template('template.html')


@app.route('/upload-file/')
def upload_file():
    file_name = 'myfile1'
    with open(file_name, 'r') as content_file:
        if  os.stat(file_name).st_size < 1024:
            content = content_file.read()
            conn.put_object(container_name, file_name, contents=content)

        else:
            return "file exceeded 1mb"
    # File name for testing
    file_name = 'myfile2'

    with open(file_name, 'r') as content_file:
        content = content_file.read()
        conn.put_object(container_name, file_name, contents=content)

    return render_template('uploaded.html')


@app.route('/select-first-line', methods=['POST'])
def select_first_line(): #CAN BE USED TO DOWNLOAD FILES AS WELL!!!!!
    filename = request.form['files']
    try:
        file = conn.get_object(container_name, filename)
        with open('tempfile.txt', 'w') as temp:
            temp.write(file[1])

        with open('tempfile.txt', 'r') as temp:
            return temp.readline()
      #  for line in temp:
        # print line
    except:
        return 'Not in cloud'

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(port), debug=True)
