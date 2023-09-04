from flask import Flask, jsonify, render_template, send_from_directory, request
from backend.mol_sql import Database
from backend import mol_display
from io import TextIOWrapper

# open connection to database
db = Database()
db.create_tables()

mol_display.radius = db.radius()
mol_display.element_name = db.element_name()
mol_display.gradients = db.radial_gradients()


app = Flask(__name__)

# ##################################################################################
# ENDPOINT DEFINITIONS
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/molecule_list', methods=['GET'])
def molecule_list():
    return jsonify(db.fetch_molecules())


@app.route('/element_list', methods=['GET'])
def element_list():
    return jsonify(db.fetch_elements())


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file selected'})

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'message': 'Invalid file uploaded'})
    
    text_file_obj = TextIOWrapper(file)
    name = request.form.get('name')

    if db.molecule_exists(name):
        return jsonify({'message': 'Molecule with this name already exists'}), 409
    
    elif db.add_molecule(name, text_file_obj):
        molecule = db.fetch_molecule(name)

        return jsonify({
            'message': 'File uploaded successfully',
            'molecule': molecule}), 201

    return jsonify({'message': 'Invalid file uploaded'}), 500
    

@app.route('/elements', methods=['PUT'])
def add_element():
    element = request.get_json()['element']

    # TODO: check how colors are received here
    # in mol_sql they can't have the # before hexadecimal value
    replaced = db.force_add_element((
        element['number'],
        element['code'],
        element['name'],
        element['color1'][1:],
        element['color2'][1:],
        element['color3'][1:],
        element['radius']
    ))

    # element already exists in database
    if replaced:
        return '', 200

    return '', 201


@app.route('/elements/<element_name>', methods=['DELETE'])
def remove_element(element_name):

    db.delete_element(element_name)

    mol_display.radius = db.radius()
    mol_display.element_name = db.element_name()
    mol_display.gradients = db.radial_gradients()

    return '', 204


@app.route('/molecule/<molecule_name>', methods=['GET'])
def v_molecule(molecule_name):

    if not db.molecule_exists(molecule_name):
        return not_found_error("error")

    mol = db.load_mol(molecule_name)
    mol.sort()
    svg = mol.svg()

    return render_template('molecule.html', svg_content=svg)


# TODO: setup better structure for 404.html
# leave a link back to the main page from there
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# ##################################################################################
# START SERVER
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)