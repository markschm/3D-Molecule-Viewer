from flask import Flask, jsonify, render_template, send_from_directory, request
# from backend.mol_sql import Database
# from backend import mol_display

# open connection to database
# db = Database()
# db.create_tables()

# mol_display.radius = db.radius()
# mol_display.element_name = db.element_name()
# mol_display.gradients = db.radial_gradients()


app = Flask(__name__)


# load home
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/molecule_list', methods=['GET'])
def molecule_list():
    return jsonify(db.fetch_molecules())

@app.route('/element_list', methods=['GET'])
def element_list():
    return jsonify(db.fetch_elements())




# this one will need to be setup once I have front end not sure how files are sent
# with flask and stuff
@app.route('/upload', methods=['POST'])
def upload():
    return jsonify({'message': 'file uploaded successfully'})
    

@app.route('/elements', methods=['PUT'])
def add_element():
    data = request.get_json()

    print()

@app.route('/elements', methods=['DELETE'])
def remove_element():
    return '', 204

@app.route('/molecule', methods=['POST'])
def view_molecule():

    # replace with adding svg string returned from db in the future
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200"><circle cx="150" cy="100" r="80" /></svg>'
    return render_template('molecule.html', svg_content=svg_content)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)