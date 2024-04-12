import sqlite3
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify, send_file
import os
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from pymatgen.io.vasp.outputs import Poscar
import crystal_toolkit.components as ctc
import sqlite3
from dash import dcc, html

app = Flask(__name__)
# server = Flask(__name__)
server = app 
# Initialize Dash app within Flask app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets)

# Connect to SQLite database
conn = sqlite3.connect('perov21.db')
cur = conn.cursor() 
# Function to fetch data from the database
def get_dopants():
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Dopant FROM FormEnData")
    dopants = cursor.fetchall()
    conn.close()
    return [dopant[0] for dopant in dopants]


def get_host_material(material=None):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    if material:
        cursor.execute("SELECT DISTINCT hostmaterial FROM hostmaterial WHERE hostmaterial = ?", (material,))
    else:
        cursor.execute("SELECT DISTINCT hostmaterial FROM hostmaterial")
    hostmaterials = cursor.fetchall()
    conn.close()
    return [hostmaterial[0] for hostmaterial in hostmaterials]


def get_specific_element(hostmaterial):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT Element FROM {hostmaterial}")
    specificelements = cursor.fetchall()
    conn.close()
    return [specificelement[0] for specificelement in specificelements]


def get_elements():
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Element FROM bandgapfull")
    elements = cursor.fetchall()
    conn.close()
    return [element[0] for element in elements]


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/vasp_download', methods=['GET', 'POST'])
def formation_energy():
    dopants = get_vaspfile()

    if request.method == 'POST':
        file_name_selected = request.form.get('option')  # Ensure to retrieve the selected option
        return render_template('formation_energy.html', dopants=dopants,
                               option=file_name_selected)
    return render_template('formation_energy.html', dopants=dopants)


def get_vaspfile():
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Filename FROM Vasp_new")
    vaspfiles = cursor.fetchall()
    conn.close()
    return [vaspfile[0] for vaspfile in vaspfiles]


@app.route('/vasp', methods=['GET'])
def vasp():
    dopants = get_vaspfile()
    dopant = request.args.get('dopant')
    print(dopant)
    if dopant in dopants:
        file_name = dopant + ".vasp"
        directory = os.path.join(app.root_path, 'data/vasp_files')  # Specify the directory where files are stored
        try:
            return send_from_directory(directory, file_name, as_attachment=True)
        except FileNotFoundError:
            return "File not found", 404
        # return send_file(file_name, as_attachment=True)
    else:
        return "Option not found"


def get_formation_energy(dopant, model):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    if model == 'GPR':
        cursor.execute("SELECT `Formation Energy GPR` FROM FormEnData WHERE Dopant = ?", (dopant,))
    elif model == 'RFR':
        cursor.execute("SELECT `Formation Energy RFR` FROM FormEnData WHERE Dopant = ?", (dopant,))
    elif model == 'NN':
        cursor.execute("SELECT `Formation Energy NN` FROM FormEnData WHERE Dopant = ?", (dopant,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "No data available for the selected dopant and model"


def dft_formation(selected_element, host_material):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    print(host_material)
    query = f"SELECT `formation energy (eV)`, `charge transition (+/0) (eV)` FROM {host_material} WHERE Element = ?"
    cursor.execute(query, (selected_element,))
    result = cursor.fetchone()
    conn.close()
    if result:
        formation_energy, charge_transition = result
        return (formation_energy, charge_transition)
    else:
        return "No data available for the selected element"


def get_host_material_energy(dopant, model):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    print(dopant,model)
    if model == 'GPR':
        cursor.execute("SELECT `GPR` FROM formationfull WHERE Dopant = ?", (dopant,))
    elif model == 'RFR':
        cursor.execute("SELECT `RFR` FROM formationfull WHERE Dopant = ?", (dopant,))
    elif model == 'NN':
        cursor.execute("SELECT `NN` FROM formationfull WHERE Dopant = ?", (dopant,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "No data available for the selected dopant and model"


@app.route('/bandgap', methods=['GET', 'POST'])
def bandgap():
    elements = get_elements()
    model_options = ['GPR', 'NN', 'RFR']
    if request.method == 'POST':
        selected_element = request.form['element']
        selected_model = request.form['model']
        bandgap_value = get_bandgap(selected_element, selected_model)
        return render_template('bandgap.html', elements=elements, model_options=model_options,
                               selected_element=selected_element, selected_model=selected_model,
                               bandgap_value=bandgap_value)
    return render_template('bandgap.html', elements=elements, model_options=model_options)


def get_bandgap(element, model):
    conn = sqlite3.connect('perov21.db')
    cursor = conn.cursor()
    if model == 'GPR':
        cursor.execute("SELECT `GPR` FROM bandgapfull WHERE Element = ?", (element,))
    elif model == 'NN':
        cursor.execute("SELECT `NN` FROM bandgapfull WHERE Element = ?", (element,))
    elif model == 'RFR':
        cursor.execute("SELECT `RFR` FROM bandgapfull WHERE Element = ?", (element,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "No data available for the selected element and model"


@app.route('/host_material', methods=['GET', 'POST'])
def host_material():
    hostmaterials = get_host_material()
    model_options = ['GPR', 'RFR'] # Options for the model dropdown menu
    selected_material= 'CsSnI3'
    dopants = get_specific_element(selected_material)
    # print(dopants)

    if request.method == 'POST':
        print("120")
        # selected_material = request.form['hostmaterial']
        # print(selected_material)
        selected_dopant = request.form['dopant']
        selected_model = request.form['model']

        print(selected_dopant)
        formation_energy_value = get_host_material_energy(selected_dopant, selected_model)  
        print("Selected material:", selected_model)

        print("line 170", formation_energy_value)
        return render_template('host_material.html',  dopants=dopants,
                               model_options=model_options,
                               hostmaterial=selected_material,
                               selected_dopant=selected_dopant,
                               hostmaterials=hostmaterials,
                               formation_energy_value=formation_energy_value)
    return render_template('host_material.html', hostmaterial=selected_material,model_options=model_options,dopants=dopants,hostmaterials=hostmaterials)



# Inside the material_specific route
@app.route('/material_specific', methods=['GET', 'POST'])
def material_specific():
    hostmaterials = get_host_material()
    selected_material = 'CsSnI3'
    dopants = get_specific_element(selected_material)
    model_options = ['GPR', 'NN', 'RFR']

    if request.method == 'POST':
        selected_material = request.form['hostmaterial']
        selected_dopant = request.form['dopant']
        result = dft_formation(selected_dopant, selected_material)
        formation_energy_value = result[0]
        charge_transition = result[1]
        return render_template('material_specific.html', dopants=dopants,
                               model_options=model_options,
                               selected_dopant=selected_dopant,
                               selected_material=selected_material,
                               formation_energy_value=formation_energy_value,
                               charge_transition=charge_transition,
                               hostmaterials=hostmaterials)
    
    # Get the HTML content of the Dash app
    dash_content = dash_app.index()

    return render_template('material_specific.html', dopants=dopants,
                           model_options=model_options,
                           selected_material=selected_material,
                           hostmaterials=hostmaterials,
                           dash_content=dash_content)

@app.route('/new_page', methods=['GET', 'POST'])
def new_page():
    hostmaterials = get_host_material()
    # Options for the model dropdown menu

    if request.method == 'POST':
        selected_material = request.form['hostmaterial']

        print("Selected material:", selected_material)

        # print("line 170", selected_material)
        return redirect(url_for('material_specific', materialselect=selected_material))
    return render_template('new_page.html', hostmaterials=hostmaterials)


@app.route('/new_page_con/<materialselect>', methods=['GET', 'POST'])
def new_page_con(materialselect):
    if request.method == 'POST':
        selected_material = request.form['hostmaterial']
        return redirect(url_for('material_specific', materialselect=selected_material))
    else:
        # Get specific elements based on the selected host material
        specificelements = get_specific_element(materialselect)
        # Fetch the corresponding formation energy for the first element (assuming one element is selected)
        formation_energy_value = dft_formation(specificelements[0],
                                               materialselect)  # Pass the selected element and material
        return render_template('new_page_con.html', specificelements=specificelements, selected_material=materialselect,
                               formation_energy_value=formation_energy_value)

# Define function to fetch available options from the database
def get_element_options():
    cur.execute("SELECT DISTINCT filename FROM Vasp_new")
    options = cur.fetchall()
    return [{'label': filename[0], 'value': filename[0]} for filename in options]

# Define directory containing .vasp files
vasp_dir = "data/vasp_files"

# Get list of all .vasp files in the directory
file_paths = {}
for file in os.listdir(vasp_dir):
    if file.endswith(".vasp"):
        file_name = os.path.splitext(file)[0]  # Remove file extension
        file_paths[file_name] = os.path.join(vasp_dir, file)





# Define layout of the Dash app
dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        3D- Structure view 
    '''),
    html.Div([
        html.H1("Model Structure"),
        html.Label("Select Dopant:"),
        dcc.Dropdown(
            id="structure-dropdown",
            options=get_element_options(),
            value=list(file_paths.keys())[0] if file_paths else None
        ),
        html.Div(id="structure-layout"),
        dcc.Interval(id="interval-component", interval=5000, n_intervals=0)
    ])
])

# Define callback function for the Dash app
@dash_app.callback(
    Output("structure-layout", "children"),
    [Input("structure-dropdown", "value"),
     Input("interval-component", "n_intervals")]
)
def update_layout(selected_option, _):
    if selected_option in file_paths:
        structure = Poscar.from_file(file_paths[selected_option]).structure
        structure_component = ctc.StructureMoleculeComponent(structure, id="my_structure")
        return structure_component.layout()
    else:
        return html.Div("Error: Selected option not found in file paths")


# Define a route for Flask to render the Dash app
@server.route('/dashboard/')
def dashboard():
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=False, host="0.0.0.0")