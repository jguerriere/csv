from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import csv
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dog'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Data cleaning and processing logic
def standardize_name(name):
    nickname_map = {
        'Bob': 'Robert', 'Bobby': 'Robert',
        'Bill': 'William', 'Billy': 'William',
        'Jim': 'James', 'Jimmy': 'James',
        'Joe': 'Joseph', 'Joey': 'Joseph',
        'Tom': 'Thomas', 'Tommy': 'Thomas',
        'Dave': 'David', 'Davy': 'David',
        'Mike': 'Michael', 'Mikey': 'Michael',
        'Nick': 'Nicholas', 'Nicky': 'Nicholas',
        'Steve': 'Steven', 'Stevie': 'Steven',
        'Rick': 'Richard', 'Ricky': 'Richard',
        'Tony': 'Anthony',
        'Ken': 'Kenneth', 'Kenny': 'Kenneth',
        'Sam': 'Samuel', 'Sammy': 'Samuel',
        'Tim': 'Timothy', 'Timmy': 'Timothy',
        'Pat': 'Patrick', 'Patty': 'Patrick',
        'Chris': 'Christopher', 'Chrissy': 'Christopher',
        'Alex': 'Alexander', 'Alexandra': 'Alexandra',
        'Liz': 'Elizabeth', 'Lizzie': 'Elizabeth',
        'Matt': 'Matthew', 'Matty': 'Matthew',
        'Greg': 'Gregory', 'Gregg': 'Gregory',
        'Dan': 'Daniel', 'Danny': 'Daniel',
        'Sue': 'Susan', 'Susie': 'Susan',
        'Meg': 'Margaret', 'Maggie': 'Margaret',
        'Jack': 'John',
        'Ted': 'Theodore', 'Teddy': 'Theodore',
        'Ron': 'Ronald', 'Ronnie': 'Ronald',
        'Andy': 'Andrew', 'Drew': 'Andrew',
        'Frank': 'Franklin', 'Frankie': 'Franklin',
        'Ray': 'Raymond', 'Raymie': 'Raymond',
        'Phil': 'Philip'
    }
    # Convert name to proper case before attempting to standardize it
    proper_name = name.capitalize()
    return nickname_map.get(proper_name, proper_name)

def proper_case_name(name):
    if name.lower().startswith('mc'):
        return 'Mc' + name[2:].capitalize()
    elif name.lower().startswith('mac'):
        return 'Mac' + name[3:].capitalize()
    else:
        parts = re.split("(-|')", name)
        return ''.join([part.capitalize() if part not in ["-", "'"] else part for part in parts])

def format_phone_number(phone_number):
    cleaned_number = re.sub(r"\D", "", phone_number)
    return f"{cleaned_number[:3]}-{cleaned_number[3:6]}-{cleaned_number[6:]}" if len(cleaned_number) == 10 else phone_number

def process_record(record):
    record['First Name'] = proper_case_name(standardize_name(record['First Name']))
    record['Last Name'] = proper_case_name(record['Last Name'])
    record['Email'] = record['Email'].lower()
    record['Phone'] = format_phone_number(record['Phone'])
    return record

def remove_duplicates(records):
    unique_records = {}
    for record in records:
        email_key = record['Email'].lower()
        if email_key not in unique_records:
            unique_records[email_key] = record
        else:
            # Assuming the later record is more complete or updated
            unique_records[email_key] = process_record(record)
    return list(unique_records.values())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash('No selected file or file type not allowed')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        with open(input_path, newline='') as f:
            records = list(csv.DictReader(f))
        processed_records = remove_duplicates([process_record(record) for record in records])

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"processed_{filename}")
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=processed_records[0].keys())
            writer.writeheader()
            writer.writerows(processed_records)

        return send_file(output_path, as_attachment=True)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
