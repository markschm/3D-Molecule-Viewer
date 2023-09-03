from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO, TextIOWrapper
from mol_sql import Database
import mol_display
import urllib
import sys
import re
import json

# TODO: anything marked todo in here is super quick and awful changes
# i added to get this working off the school server. need to go back and make changes
# to be fair tho should've worked either way so I guess i did smthing wrong previously

# open connection to database
db = Database()
db.create_tables()


mol_display.radius = db.radius()
mol_display.element_name = db.element_name()
mol_display.gradients = db.radial_gradients()


# list of paths
PUBLIC_FILES = ["/index.html", "/style.css", "/script.js", "/molecule.html"]
RESOURCES_PATHS = ["/molecule_data", "/elements_data"]
POST_PATHS = ["/upload", "/molecule", "/remove_element", "/add_element"]


class HTTPRequestHandler(BaseHTTPRequestHandler):

    # process a get request to the root site path
    # or send a 404 response if another site path was requested
    def do_GET(self):

        # if a public file is requested
        if self.path in PUBLIC_FILES: # if user visits root path
            self.send_response(200) # ok

            extension = self.path.split(".")[-1]
            if extension == "css":
                self.send_header("Content-Type", "text/css")
        
            elif extension == "js":
                self.send_header("Content-Type", "text/javascript")

            else:
                self.send_header("Content-Type", "text/html")


            # read file 
            fp = open(f"frontend{self.path}") # remove leading '/' from file path
            page = fp.read()
            fp.close()

            self.send_header("Content-length", len(page))
            self.end_headers()
            self.wfile.write(bytes(page, "utf-8"))


        # data for molecule or element lists requested
        elif self.path in RESOURCES_PATHS:
            self.send_response(200)

            if self.path == "/molecule_data":
                data = json.dumps(db.fetch_molecules())

            elif self.path == "/elements_data":
                data = json.dumps(db.fetch_elements())


            self.send_header("Content-length", len(data))
            self.end_headers()

            # use jsondumps in write instead of above to reduce having it called in two spots
            self.wfile.write(bytes(data, "utf-8"))


        # if invalid site path
        else: 
            self.send_response(404)
            self.end_headers()

            self.wfile.write(bytes("404: not found", "utf-8"))


    # process a post request which takes a .sdf file from the form and x, y, z axes rotations
    # and then creates an molecule object to parse the data a display the svg of the molecule 
    def do_POST(self):

        if self.path in POST_PATHS:
            status = 200
            length = int(self.headers.get("Content-length"))

            form_data = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))

            # upload sdf file to server
            if self.path == "/upload":
                # TODO: below area isn't working i'm getting completely different
                # response format compared to on school server, so look into this
                # in the future
                name_area = form_data[list(form_data.keys())[0]][0]

                # get name of molecule passed in
                # if no name return bad exit status
                name_pattern = re.compile(r'(?<=mol_name")(?:\s*)(.*?)(?:\s*)(?=--)')
                name = name_pattern.search(name_area).group().strip()

                # if molecule name was inputted
                if len(name) > 0:
                    # shorten line later make it a 2 liner
                    text_file_obj = TextIOWrapper(BytesIO(name_area.encode("utf-8")))

                    if db.molecule_exists(name):
                        response = "Molecule With That Name Already Exists."
                        status = 400

                    elif db.add_molecule(name, text_file_obj):
                        response = name
                    
                    else:
                        response = "Error. Invalid SDF."
                        status = 400


                else:
                    response = "Error. No Molecule Name."
                    status = 400


            # add element
            elif self.path == "/add_element":
                input_fields = 7

                fields = 0
                e = ["" for _ in range(input_fields)]

                for key, value in form_data.items():
                    e[fields] = value[0]
                    fields += 1

                # not all input fields full
                if fields < input_fields:
                    response = "Error. Incomplete Form Input Fields."
                    status = 400

                # e = [element_no, element_code, element_name, color1, color2, color3, radius]
                else:
                    # use [1:] to skip # as its already in the svg
                    if db.force_add_element((int(e[0]), e[1], e[2], e[3][1:], e[4][1:], e[5][1:], int(e[6]))):
                        response = "Replaced"
                    
                    else:
                        response = e[2]

                    mol_display.radius = db.radius()
                    mol_display.element_name = db.element_name()
                    mol_display.gradients = db.radial_gradients()


            # remove element
            elif self.path == "/remove_element":
                # if element was selected before button press
                if 'element_name' in form_data:
                    name = form_data['element_name'][0]

                    db.delete_element(name)
                    response = name

                    mol_display.radius = db.radius()
                    mol_display.element_name = db.element_name()
                    mol_display.gradients = db.radial_gradients()

                else:
                    response = "Error. No Element Selected"
                    status = 400


            # view molecule
            elif self.path == "/molecule":

                # TODO: made change here look into doing it better way
                if len(form_data) > 0:
                    # parse name from data
                    name_area = form_data[list(form_data.keys())[0]][0]
                    name_pattern = re.compile(r'(?<=mol-list")(?:\s*)(.*?)(?:\s*)(?=--)')
                    name = name_pattern.search(name_area).group().strip()

                    # generate svg from
                    mol = db.load_mol(name)
                    mol.sort()
                    svg = mol.svg()

                    self.send_response(200)
                    self.send_header("Content-Type", "image/svg+xml")
                    self.send_header("Content-length", len(svg))
                    self.end_headers()

                    self.wfile.write(bytes(svg, "utf-8")) # print molecule svg to page

                    return

                else:
                    response = "Error. No Molecule Selected."
                    status = 400

            # send headers and content
            self.send_response(status)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-length", len(response))
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))


        # invalid path
        else:
            self.send_response(404)
            self.end_headers()

            self.wfile.write(bytes("404: not found", "utf-8"))


# start server on port specified in system call
httpd = HTTPServer(('0.0.0.0', int(sys.argv[1])), HTTPRequestHandler)
httpd.serve_forever()