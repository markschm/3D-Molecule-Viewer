# Tell the OS where the .so file is at runtime -> required on linux
# export LD_LIBRARY_PATH=`pwd`
#####################################################################
CC=clang
CFLAGS=-Wall -std=c99 -pedantic
MATH_LIB=-lm

PYTHON_INCLUDE_PATH=/usr/include/python3.10
PYTHON_LANGUAGE_LIBRARY_PATH=/usr/lib/python3.10/config-3.10-x86_64-linux-gnu

all: libmol.so mol.o _molecule.so molecule_wrap.o molecule_wrap.c molecule.py

clean:
	rm -f *.o *.so molecule_wrap.c molecule.py


libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so $(MATH_LIB)

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fpic -o mol.o 

_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -o _molecule.so -L$(PYTHON_LANGUAGE_LIBRARY_PATH) -lpython3.10 -L. -lmol

molecule_wrap.o: molecule_wrap.c
	$(CC) -c molecule_wrap.c -fpic -o molecule_wrap.o -I$(PYTHON_INCLUDE_PATH) 

molecule_wrap.c molecule.py: molecule.i mol.c mol.h
	swig -python molecule.i
