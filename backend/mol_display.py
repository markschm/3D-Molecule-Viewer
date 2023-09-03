from backend.mol_constants import *
from backend import molecule
import re


# wrapper class for the c atom class/struct
# strores c_atom clas/struct as a member variable
class Atom:

    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z


    def __str__(self):
        return f"{self.atom.element}, x, y, z = {self.atom.x}, {self.atom.y}, {self.z}\n"


    # returns svg string representation of atom
    def svg(self):
        return ('\n <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>' 
            % (OFFSET_X + (self.atom.x * 100), OFFSET_Y + (self.atom.y * 100), radius.get(self.atom.element, radius["00"]), element_name.get(self.atom.element, element_name["00"])))


# wrapper class for the c bond class/struct
# stores c_bond class/struct as a member variable
class Bond:

    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z


    def __str__(self):
        return f"Atom {self.bond.a1} <-> Atom {self.bond.a2} | Electrion Pairs: {self.bond.epairs}\n" \
                    f"Atom Coordinates: {self.bond.x1}, {self.bond.y1} and {self.bond.x2}, {self.bond.y2}\n" \
                    f"len, dx, dy = {self.bond.len}, {self.bond.dx}, {self.bond.dy}\n"


    # returns svg string representation of the bond
    def svg(self):
        BOND_RADIUS = 10

        # compute values with svg offsets
        x1 = OFFSET_X + (self.bond.x1 * 100) + (self.bond.dy * BOND_RADIUS)
        y1 = OFFSET_Y + (self.bond.y1 * 100) - (self.bond.dx * BOND_RADIUS)

        x2 = OFFSET_X + (self.bond.x1 * 100) - (self.bond.dy * BOND_RADIUS)
        y2 = OFFSET_Y + (self.bond.y1 * 100) + (self.bond.dx * BOND_RADIUS) 

        x3 = OFFSET_X + (self.bond.x2 * 100) - (self.bond.dy * BOND_RADIUS)
        y3 = OFFSET_Y + (self.bond.y2 * 100) + (self.bond.dx * BOND_RADIUS)

        x4 = OFFSET_X + (self.bond.x2 * 100) + (self.bond.dy * BOND_RADIUS)
        y4 = OFFSET_Y + (self.bond.y2 * 100) - (self.bond.dx * BOND_RADIUS)


        # compute bond cap values
        a1_z = self.bond.get_atom(self.bond.a1).z
        a2_z = self.bond.get_atom(self.bond.a2).z

        dz = (a2_z - a1_z) / self.bond.len

        if dz < 0:
            cap_x = (x3 + x4) / 2
            cap_y = (y3 + y4) / 2

        else:
            cap_x = (x1 + x2) / 2
            cap_y = (y1 + y2) / 2


        # get bond id to associate bond polygon with linear gradient
        bond_id = f"bond{int(x1 + y4) - 500}"


        # fill in values for svg elements
        poly_linear_gradient = LINEAR_GRADIENT_SVG % (bond_id , x1, y1, x2, y2)

        polygon = '\n <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="url(#%s)"/>' \
                    % (x1, y1, x2, y2, x3, y3, x4, y4, bond_id)

        ellipse = '\n <ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f"  fill="url(#%s)" />' \
                    % (cap_x, cap_y, BOND_RADIUS, BOND_RADIUS, bond_id)


        return (poly_linear_gradient + polygon + ellipse)


# Molecule subclass of swig created molecule class
# used for creating svg of molecule object
class Molecule (molecule.molecule):

    def __str__(self):
        out_string = f"-- Molecule -- {self.atom_no} Atoms | {self.bond_no} Bonds\n"

        out_string += "Atoms:\n"
        for i in range(self.atom_no):
            out_string += Atom(self.get_atom(i)).__str__()

        out_string += "\nBonds:\n"
        for i in range(self.bond_no):
            out_string += Bond(self.get_bond(i)).__str__() + "\n"

        return out_string


    # return svg string representation of molecule using bonds and atoms
    def svg(self):
        svg_str = ""
        svg_str += HEADER + gradients

        atom_index, bond_index = 0, 0
        # while not at last atom or bond in their lists
        while atom_index < self.atom_no and bond_index < self.bond_no:
            # if atom z value is less than bond z value
            if self.get_atom(atom_index).z < self.get_bond(bond_index).z:
                svg_str += Atom(self.get_atom(atom_index)).svg()
                atom_index += 1

            else: # if bond z value is less than atom
                svg_str += Bond(self.get_bond(bond_index)).svg()
                bond_index += 1

        # for each atom left in list
        while atom_index < self.atom_no:
            svg_str += Atom(self.get_atom(atom_index)).svg()
            atom_index += 1

        # for each bond left in list
        while bond_index < self.bond_no:
            svg_str += Bond(self.get_bond(bond_index)).svg()
            bond_index += 1

        svg_str += FOOTER

        return svg_str


    # parse sdf file data passed in as a textiowrapper object
    # get the atom, bond and rotation data and fill the molecule object with the data
    # return True if parse was successful otherwise false
    def parse(self, file):
        # regex patterns
        atom_pattern = re.compile(r'\n(?:\s+-?\d+.\d+){3}\s+[A-Z]{1,2}(?=(?:\s+\d+){12}\s*\n)')
        bond_pattern = re.compile(r'\n(?:\s+\d+){3}(?=(?:\s+\d+){4}\s*\n)')
        rotation_pattern = re.compile(r'name="(pitch|yaw|roll)"\s+(\d+)\s+')

        data = file.read()[8:]

        # check to see if file is an sdf
        if "M  END" in data and "$$$$" in data:

            # find all atoms, bonds, rotations from forum using regex patterns
            atom_data = atom_pattern.findall(data)
            bond_data = bond_pattern.findall(data)
            rotation_data = rotation_pattern.findall(data)

            # for each atom in atom_data
            for i in atom_data:
                atom_info = i.split() # [x, y, z, element]
                self.append_atom(atom_info[3], float(atom_info[0]), float(atom_info[1]), float(atom_info[2]))

            # for each bond in bond_data
            for i in bond_data:
                bond_info = i.split() # [a1, a2, epairs]
                self.append_bond(int(bond_info[0]) - 1, int(bond_info[1]) - 1, int(bond_info[2]))

            # apply rotation values that were passed through form
            self.apply_rotations(rotation_data)

            return True


        return False


    # apply pitch, yaw, roll rotations to molecule
    def apply_rotations(self, rotations):
        # rotations ex: [('pitch', '20'), ...]

        roll, pitch, yaw = 0, 0, 0

        # for each rotation tuple
        for rotation in rotations:
            direction, degrees = rotation

            if direction == 'pitch':
                pitch = int(degrees)
            
            elif direction == 'yaw':
                yaw = int(degrees)
            
            elif direction == 'roll':
                roll = int(degrees)

        self.rotate(roll, pitch, yaw)
