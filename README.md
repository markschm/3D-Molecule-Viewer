# 3D Molecule Viewer

## Run Program
```
In root directory build and run:
> docker-compose up

In browser go to:
http://localhost:8080/
```

## Features (update)
images here


## Description (update)
didn't completely finish assignment because I didn't give myself enough time :( . Wanted to setup the project to be run anywhere with docker since before it was only able to run on school server with the environment. only few tweaks were made to move it from running on school server to docker. Those changes are def not what I want to keep so those will be changing very soon. explain y i used docker

## Todo
- update all endpoints to send and receive json responses
    - update all molsql functions to return json structured objects that can easily be converted
    - switch to flask server
    - just setup endpoints and then fix the javascript later, just make list of endpoints and return structure so js stuff after will be easy using fetch
    - only issue is sending the file with the weird format as it's sent but I guess that can be figured out
- add short description to be shown on github
- fix spacing issue in molecule selection area
- add photos of program in use
- fix the mini changes that I made from environment change
- finish the assignment with rotations and stuff
- explain what assignment can do and add some sdf files for people to try
- update 404 page


## Example Endpoint structures
### /molecule_list GET
Server Response:
```
{
    'molecules': [
        {
            'name': 'Water',
            'atoms: 3,
            'bonds': 2
        },
        {
            ...
        }
    ]
}
```

### /element_list GET
Server Response:
```
{
    'elements': [
        'Default',
        'Hydrogen',
        ...
    ]
}
```

### /upload POST
Server Receives: File  
Server Response:
```
{
    'message': 'status message',
    'molecule': {
        'name': 'Water',
        'atoms: 3,
        'bonds': 2
    }
}
```

### /elements PUT
Server Receives:
```
{
    'element': {
        'name': 'Oxygen',
        'code': 'O',
        'number': 8,
        'radius': 40,
        'color1': #FF0000,
        'color2': #00FF00,
        'color3': #0000FF
    }
}
```

### /elements/<element_name> DELETE
Delete selected element from database

### /molecule/<molecule_name> GET
Server redirects and displays selected molecule
