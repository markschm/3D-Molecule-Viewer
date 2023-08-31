from mol_constants import *
import mol_display
import sqlite3
import os


class Database:

    # opens database connection to a file in local directory "molecule.db"
    # if reset is set to true delete molecule.db to start a fresh database
    def __init__(self, reset=False):

        if reset == True and os.path.exists("molecules.db"):
            os.remove("molecules.db")

        self.conn = sqlite3.connect("molecules.db")


    # Create the molecule.db tables if they don't already exist
    def create_tables(self):

        # Elements Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements
                               ( ELEMENT_NO     INTEGER     NOT NULL,
                                 ELEMENT_CODE   VARCHAR(3)  NOT NULL,
                                 ELEMENT_NAME   VARCHAR(32) NOT NULL,
                                 COLOUR1        CHAR(6)     NOT NULL,
                                 COLOUR2        CHAR(6)     NOT NULL,
                                 COLOUR3        CHAR(6)     NOT NULL,
                                 RADIUS         DECIMAL(3)  NOT NULL,
                                 PRIMARY KEY    (ELEMENT_CODE) );""")

        # Atoms Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                               ( ATOM_ID        INTEGER        PRIMARY KEY AUTOINCREMENT NOT NULL,
                                 ELEMENT_CODE   VARCHAR(3)     NOT NULL,
                                 X              DECIMAL(7, 4)  NOT NULL,
                                 Y              DECIMAL(7, 4)  NOT NULL,
                                 Z              DECIMAL(7, 4)  NOT NULL,
                                 FOREIGN KEY    (ELEMENT_CODE) REFERENCES Elements );""")

        # Bonds Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                               ( BOND_ID        INTEGER     PRIMARY KEY AUTOINCREMENT NOT NULL,
                                 A1             INTEGER     NOT NULL,
                                 A2             INTEGER     NOT NULL,
                                 EPAIRS         INTEGER     NOT NULL );""")

        # Molecules Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                               ( MOLECULE_ID    INTEGER     PRIMARY KEY AUTOINCREMENT NOT NULL,
                                 NAME           TEXT        NOT NULL UNIQUE );""")

        # MoleculeAtom Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                               ( MOLECULE_ID    INTEGER     NOT NULL,
                                 ATOM_ID        INTEGER     NOT NULL,
                                 PRIMARY KEY    (MOLECULE_ID, ATOM_ID),
                                 FOREIGN KEY    (MOLECULE_ID)   REFERENCES Molecules,
                                 FOREIGN KEY    (ATOM_ID)       REFERENCES Atoms );""")

        # MoleculeBond Table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                               ( MOLECULE_ID    INTEGER     NOT NULL,
                                 BOND_ID        INTEGER     NOT NULL,
                                 PRIMARY KEY    (MOLECULE_ID, BOND_ID),
                                 FOREIGN KEY    (MOLECULE_ID)   REFERENCES Molecules,
                                 FOREIGN KEY    (BOND_ID)       REFERENCES Bonds );""")

        self.force_add_element((0, "00", "Default", "000000", "55FF55", "AAFFAA", 50))

        # commit changes to database
        self.conn.commit()        


    # a method to use indexing to set values in a table
    def __setitem__(self, table, values):

        placeholders = ", ?" * len(values)
        query = f"INSERT INTO {table} VALUES ({placeholders[1:]});"

        self.conn.execute(query, values)
        self.conn.commit()

    
    # add element to Elements table, if element with same code already
    # exists in table delete it and then add new element
    # return True if element was replaced False otherwise
    def force_add_element(self, element_values):
        # element_values = (Number, Code, Name, Color1, Color2, Color3, Radius)

        not_exists = False

        # check if element exists in table
        element_occurences = self.conn.execute("SELECT COUNT (*) FROM Elements WHERE (ELEMENT_CODE=?);",
                                     (element_values[1],)).fetchone()[0]

        if element_occurences > 0:
            self.conn.execute("DELETE FROM Elements WHERE (ELEMENT_CODE=?);", (element_values[1],))
            not_exists = True

        self['Elements'] = element_values

        return not_exists


    # delete element by name from Elements table
    def delete_element(self, element_name):
        
        self.conn.execute("DELETE FROM Elements WHERE (ELEMENT_NAME=?); ", (element_name,))
        self.conn.commit()


    # add atom attributes to atom table
    # add entry to MoleculeAtom table to link molecule and atom
    def add_atom(self, molname, atom):
        
        # insert atom in Atoms table
        cursor = self.conn.execute("""INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) 
                                      VALUES (?, ?, ?, ?); """,
                                       (atom.atom.element, atom.atom.x, atom.atom.y, atom.z))


        # get id of last atom added to atom table
        atom_id = cursor.lastrowid

        # get molecule id
        mol_id = self.conn.execute("""SELECT (MOLECULE_ID) FROM Molecules
                                      WHERE (NAME=?); """, (molname,)).fetchone()[0]

        # add entry into MoleculeAtom table to link molecule and atom
        self.conn.execute("""INSERT INTO MoleculeAtom
                             VALUES (?, ?); """, (mol_id, atom_id))


    # add bond attributes to bond table
    # and entry to MoleculeBond table to link molecule and bond
    def add_bond(self, molname, bond):
        
        # insert bond in Bonds table
        cursor = self.conn.execute("""INSERT INTO Bonds (A1, A2, EPAIRS)
                                      VALUES (?, ?, ?);""", (bond.bond.a1, bond.bond.a2, bond.bond.epairs))


        # get id of last bond added to bond table
        bond_id = cursor.lastrowid

        # get molecule id
        mol_id = self.conn.execute("""SELECT (MOLECULE_ID) FROM Molecules
                                      WHERE (NAME=?); """, (molname,)).fetchone()[0]


        # add entry into MoleculeBond table to link molecule and bond
        self.conn.execute("""INSERT INTO MoleculeBond
                             VALUES (?, ?)""", (mol_id, bond_id))


    # create molecule object that parses svg file
    # then move data from molecule object to database
    # return True if valid file was given and molecule was added
    def add_molecule(self, name, fp):
        
        # create a molecule object
        mol = mol_display.Molecule()

        # parse molecule file
        if not mol.parse(fp):
            return False

        # add entry to molecules table 
        self.conn.execute("INSERT INTO Molecules (NAME) VALUES (?);", (name,))


        # call add atom and add bond for each atom and bond in molecule
        for i in range(mol.atom_no):
            self.add_atom(name, mol_display.Atom(mol.get_atom(i)))

        for i in range(mol.bond_no):
            self.add_bond(name, mol_display.Bond(mol.get_bond(i)))

        self.conn.commit()

        return True

    
    # returns a mol_display.Molecule object filled with the atoms and bonds
    # from molecules.db that are associated with the molecule with the given name
    def load_mol(self, name):
        mol = mol_display.Molecule()

        # query all atoms associated with molecule of passed in name
        atoms = self.conn.execute(
                 """SELECT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z FROM Atoms
                    INNER JOIN MoleculeAtom ON (Atoms.ATOM_ID=MoleculeAtom.ATOM_ID)
                    INNER JOIN Molecules    ON (MoleculeAtom.MOLECULE_ID=Molecules.MOLECULE_ID)
                    WHERE (Molecules.NAME=?)
                    ORDER BY Atoms.ATOM_ID ASC; """, (name,)).fetchall()

        # for each atom associated with molecule
        for atom in atoms:
            element, x, y, z = atom
            
            # append atom to molecule object
            mol.append_atom(element, float(x), float(y), float(z))

        
        # query all bonds associated with molecule of passed in name
        bonds = self.conn.execute(
                 """SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS FROM Bonds
                    INNER JOIN MoleculeBond ON (Bonds.BOND_ID=MoleculeBond.BOND_ID)
                    INNER JOIN Molecules    ON (MoleculeBond.MOLECULE_ID=Molecules.MOLECULE_ID)
                    WHERE (Molecules.NAME=?)
                    ORDER BY Bonds.BOND_ID ASC; """, (name,)).fetchall()

        # for each bond associated with molecule
        for bond in bonds:
            a1, a2, epairs = bond

            # append bond to molecule object
            mol.append_bond(a1, a2, epairs)


        return mol


    # fetch all molecules in database in form 'name, atom_no, bond_no'
    # return as string each molecule on new line
    def fetch_molecules(self):

        molecule_data = self.conn.execute("""SELECT Molecules.NAME, 
                                            (SELECT COUNT(*) FROM MoleculeAtom 
                                            WHERE MoleculeAtom.MOLECULE_ID=Molecules.MOLECULE_ID),
                                            (SELECT COUNT(*) FROM MoleculeBond 
                                            WHERE MoleculeBond.MOLECULE_ID=Molecules.MOLECULE_ID) 
                                            FROM Molecules;""").fetchall()

        data = ""
        for molecule in molecule_data:
            name, atoms, bonds = molecule

            data += f"{name}, {atoms}, {bonds}\n"

        return data


    # check if molecule already exists
    def molecule_exists(self, name):

        occurences = self.conn.execute("""SELECT COUNT(*) FROM Molecules 
                                        WHERE (NAME=?);""", (name,)).fetchone()[0]

        if occurences > 0:
            return True
        return False

    
    # fetch all element names from database
    # return string with each element name on new line
    def fetch_elements(self):

        elements = self.conn.execute("SELECT (ELEMENT_NAME) FROM Elements;")

        data = ""
        for e in elements:
            data += f"{e[0]}\n"

        return data


    # returns a dictionary mapping the element codes to their radius values
    # element codes and radius values are retrieved from the Elements table
    def radius(self):
        element_radius_tuples = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements;").fetchall()

        radius_dict = {}

        #for each tuple retrieved from query
        for t in element_radius_tuples:
            element_code, rad = t

            radius_dict[element_code] = rad


        return radius_dict

    
    # returns a dictionary mapping element codes to their element names
    # element codes and names are retrieved from the Elements table
    def element_name(self):
        element_name_tuples = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements;").fetchall()

        name_dict = {}

        # for each tuple retrieved from query
        for t in element_name_tuples:
            element_code, name = t

            name_dict[element_code] = name


        return name_dict


    # returns a string consisting of multiple concatenations
    # of the radial gradients for each element in database
    def radial_gradients(self):
        elements = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements;").fetchall()

        radial_str = ""

        # for each element retrieved from query
        for element in elements:
            name, color1, color2, color3 = element

            radial_str += RADIAL_GRADIENT_SVG % (name, color1, color2, color3)

        return radial_str


        


###############################################################################
# Part 1 main
# for testing __init__, __setitem__, add_molecule, add_atom, add_bond
###############################################################################
if __name__ == "__main__":
    db = Database(reset=True)
    db.create_tables()


    # testing __setitem__
    db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
    db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
    db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
    db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )


    # testing add_molecule, add_atom, add_bond
    fp = open( 'sdf/water-3D-structure-CT1000292221.sdf' )
    db.add_molecule( 'Water', fp );

    fp = open( 'sdf/caffeine-3D-structure-CT1001987571.sdf' )
    db.add_molecule( 'Caffeine', fp )

    fp = open( 'sdf/CID_31260.sdf' )
    db.add_molecule( 'Isopentanol', fp )

    fp = open( 'sdf/random.sdf' )
    db.add_molecule( 'NightmareTest', fp)

    fp = open( 'sdf/ethane.sdf' )
    db.add_molecule( 'Ethane', fp )


    # display tables
    print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() )

    print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() )

    print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() )

    print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() )

    print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() )

    print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() )


###############################################################################
# Part 2 main
# for testing load_mol, radius, element_name, radial_gradients
###############################################################################
if __name__ == "__main__":
    db = Database(reset=False); # or use default

    mol = db.load_mol("Water")

    mol_display.radius = db.radius()
    mol_display.element_name = db.element_name()
    HEADER += db.radial_gradients()

    for molecule in [ 'Water', 'Caffeine', 'Isopentanol', 'NightmareTest', 'Ethane' ]:
        mol = db.load_mol( molecule )
        mol.sort()
        fp = open( molecule + ".svg", "w" )
        fp.write( mol.svg() )
        fp.close()
