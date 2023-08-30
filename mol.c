#include "mol.h"

// copy the values passed as arguments to the bond
void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{
    strcpy(atom->element, element);
    
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}


// copy the attributes in the atom to the corresponding arguments
void atomget(atom *atom, char element[3], double *x, double *y, double *z)
{
    strcpy(element, atom->element);

    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}


// copy the values passed as arguments to the bond and compute call compute coords
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom ** atoms, unsigned char *epairs)
{
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;

    compute_coords(bond);
}


// // copy the attributes in the bond to the corresponding arguments
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom ** atoms, unsigned char *epairs)
{
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}


// compute the z, x1, x2, y1, y2, len, dx, dy values of the bond
void compute_coords(bond *bond)
{
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;

    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    // average z value
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

    // length between a1 & a2
    bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));

    // distance between values divided by bond length
    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}


// returns the address of an area of memory to hold a molecule
// that has the required size to hold the maximum atoms and bonds
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{
    molecule *mol = malloc(sizeof(molecule));

    if (!mol)
    {
        return NULL;
    }


    // atom
    mol->atom_max = atom_max;
    mol->atom_no = 0;
    mol->atoms = NULL;
    mol->atom_ptrs = NULL;

    if (atom_max > 0)
    {
        mol->atoms = malloc(sizeof(atom) * atom_max);
        mol->atom_ptrs = malloc(sizeof(atom*) * atom_max);

        if (!mol->atoms || !mol->atom_ptrs)
        {
            return NULL;
        }
    }

    // bond
    mol->bond_max = bond_max;
    mol->bond_no = 0;
    mol->bonds = NULL;
    mol->bond_ptrs = NULL;

    if (bond_max > 0)
    {
        mol->bonds = malloc(sizeof(bond) * bond_max);
        mol->bond_ptrs = malloc(sizeof(bond*) * bond_max);

        if (!mol->bonds || !mol->bond_ptrs) 
        {
            return NULL;
        }
    }

    return mol;
}


// returns the memory address of a src bond copy
molecule *molcopy(molecule *src)
{
    molecule *mol = molmalloc(src->atom_max, src->bond_max);

    if (!mol)
    {
        return NULL;
    }

    // copy atoms from src molecule
    for (int i = 0; i < src->atom_no; i++)
    {
        molappend_atom(mol, &src->atoms[i]);
    }

    // copy bonds from src molecule
    for (int i = 0; i < src->bond_no; i++)
    {
        molappend_bond(mol, &src->bonds[i]);
    }

    return mol;
}


// free all the memory associated with a molecule
void molfree(molecule *ptr)
{
    free(ptr->atom_ptrs);
    free(ptr->atoms);
    free(ptr->bond_ptrs);
    free(ptr->bonds);
    free(ptr);
    ptr = NULL;
}


// copy data pointed to by atom to the first empty index in atoms
// set pointer to appended item in atom_ptrs
// double the size of atoms and atom_ptrs if arrays full
void molappend_atom(molecule *molecule, atom *atomToAdd)
{
    if (molecule->atom_max < 1) // if no space has been allocated for atom array
    {
        molecule->atom_max = 1;
        molecule->atoms = malloc(sizeof(struct atom));
        molecule->atom_ptrs = malloc(sizeof(struct atom*));

        if (!molecule->atoms || !molecule->atom_ptrs)
        {  
            exit(1);
        }
    } 
    else if (molecule->atom_max == molecule->atom_no) // if atom array is full
    {
        molecule->atom_max *= 2;

        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
        
        if (!molecule->atoms || !molecule->atom_ptrs)
        {
            exit(1);
        }

        // reset atom_ptrs pointers due to possibility of atoms memory location changed during realloc
        for (int i = 0; i < molecule->atom_no; i++)
        {
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }
    }

    // append new atom and a pointer to new atom
    molecule->atoms[molecule->atom_no] = *atomToAdd;
    molecule->atom_ptrs[molecule->atom_no++] = &molecule->atoms[molecule->atom_no];
}


// copy data pointed to by bond to the first empty index in atoms
// set pointer to appended item in bond_ptrs
// double the size of bonds and bond_ptrs if arrays full
void molappend_bond(molecule *molecule, bond *bondToAdd)
{
    if (molecule->bond_max < 1) // if no space has been allocated for bond array
    {
        molecule->bond_max = 1;
        molecule->bonds = malloc(sizeof(struct bond));
        molecule->bond_ptrs = malloc(sizeof(struct bond*));

        if (!molecule->bonds || !molecule->bond_ptrs)
        {
            exit(1);
        }
    }
    else if (molecule->bond_max == molecule->bond_no) // if bond array is full
    {
        molecule->bond_max *= 2;

        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);

        if (!molecule->bonds || !molecule->bond_ptrs)
        {
            exit(1);
        }

        // reset bond_ptrs pointers due to possibility of bonds memory location changed during realloc
        for (int i = 0; i < molecule->bond_no; i++)
        {
            molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }

    // append new bond and a pointer to new bond
    molecule->bonds[molecule->bond_no] = *bondToAdd;
    molecule->bond_ptrs[molecule->bond_no++] = &molecule->bonds[molecule->bond_no];
}


// compare the z values of two atoms
// return 1 if a > b, 0 if a = b, else -1
int atom_cmp(const void *a, const void *b)
{
    atom *a1 = *(atom **)a;
    atom *a2 = *(atom **)b;

    if (a1->z == a2->z)
    {
        return 0;
    }
    return (a1->z > a2->z) ? 1 : -1;
}


// compare the z values of two bonds
// return 1 if a > b, 0 if a = b, else -1
int bond_cmp(const void *a, const void *b)
{
    bond *b1 = *(bond **)a;
    bond *b2 = *(bond **)b;

    if (b1->z == b2->z)
    {
        return 0;
    }
    return (b1->z > b2->z) ? 1 : -1;
}


// sort the atom_ptrs array in order of increasing z value
// sort bond_ptrs array in order of average z value of their two atoms
void molsort(molecule *molecule) 
{
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), atom_cmp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_cmp);
}


// set values in affine transformation matrix corresponding to rotation degrees around the x-axis
void xrotation(xform_matrix xform_matrix, unsigned short deg) 
{
    double rad = deg * (M_PI / 180.0); // convert to radians for use with C-math library

    // Set matrix for rotation around x-axis
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}


// set values in affine transformation matrix corresponding to rotation degrees around the y-axis
void yrotation(xform_matrix xform_matrix, unsigned short deg) 
{
    double rad = deg * (M_PI / 180.0); // convert to radians for use with C-math library

    // Set matrix for rotation around y-axis
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}


// set values in affine transformation matrix corresponding to rotation degrees around the z-axis
void zrotation(xform_matrix xform_matrix, unsigned short deg) 
{
    double rad = deg * (M_PI / 180.0); // convert to radians for use with C-math library

    // Set matrix for rotation around z-axis
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}


// apply transformation matrix to all of the atoms of the molecule
void mol_xform(molecule *molecule, xform_matrix matrix) 
{
    for (int atom_index = 0; atom_index < molecule->atom_no; atom_index++)
    {
        // holds original atom coordinates
        double col_matrix[3] = {molecule->atoms[atom_index].x,
                                    molecule->atoms[atom_index].y,
                                    molecule->atoms[atom_index].z};


        // matrix multiplication
        molecule->atoms[atom_index].x =  (matrix[0][0] * col_matrix[0] 
                                            + matrix[0][1] * col_matrix[1]
                                            + matrix[0][2] * col_matrix[2]);

        molecule->atoms[atom_index].y =  (matrix[1][0] * col_matrix[0] 
                                            + matrix[1][1] * col_matrix[1] 
                                            + matrix[1][2] * col_matrix[2]);

        molecule->atoms[atom_index].z =  (matrix[2][0] * col_matrix[0] 
                                            + matrix[2][1] * col_matrix[1] 
                                            + matrix[2][2] * col_matrix[2]);
    }

    // compute new coordinates for bond
    for (int bond_index = 0; bond_index < molecule->bond_no; bond_index++)
    {
        compute_coords(&molecule->bonds[bond_index]);
    }
}


// allocate memory for rotation structure, copy passed in molecule and
// fill rotations struct with copied src molecule covering each x, y, z rotation of the molecule divisible by 5
rotations *spin(molecule *mol)
{
    rotations *rot = malloc(sizeof(rotations));
    if (!rot)
    {
        return NULL;
    }

    // rotate molecule copies and add them to rotation struct
    xform_matrix matrix;
    for (int i = 0; i < 72; i++)
    {
        // make copies of src molecule for each rotation axis
        rot->x[i] = molcopy(mol);
        rot->y[i] = molcopy(mol);
        rot->z[i] = molcopy(mol);

        if (!rot->x[i] || !rot->y[i] || !rot->z[i])
        {
            return NULL;
        }

        int deg = i * 5;

        // rotations on x-axis
        xrotation(matrix, deg);
        mol_xform(rot->x[i], matrix);
        molsort(rot->x[i]);

        // rotations on y-axis
        yrotation(matrix, deg);
        mol_xform(rot->y[i], matrix);
        molsort(rot->y[i]);

        // rotations on z-axis
        zrotation(matrix, deg);
        mol_xform(rot->z[i], matrix);
        molsort(rot->z[i]);
    }

    return rot;
}


// free all memory associated with rotations structure
void rotationsfree(rotations *rotations)
{
    // free all 216 molecules within the structure
    for (int i = 0; i < 72; i++)
    {
        molfree(rotations->x[i]);
        molfree(rotations->y[i]);
        molfree(rotations->z[i]);
    }

    free(rotations);
    rotations = NULL;
}
