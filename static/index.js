const BASE_URL = "http://localhost:8080";
const UNEXPECTED_ERROR 
    = "Unexpected Error Occurred. Operation Couldn't Be Completed.";


window.onload = function() {
    hideAllSections();

    document.querySelector('#view-molecule-tab').click();

    loadMoleculesRequest();
    loadElementsRequest();

    document.querySelector("#add-element-button")
        .addEventListener('click', addElementRequest);
    document.querySelector("#remove-element-button")
        .addEventListener('click', deleteElementRequest);
    document.querySelector("#upload-button")
        .addEventListener('click', uploadFileRequest);
    document.querySelector("#view-button")
        .addEventListener('click', viewMoleculeRequest);
};


// hide/close all sections
function hideAllSections() {

    // get list of all sections & hide them
    let sections = document.getElementsByClassName("page");
    for (let i = 0; i < sections.length; i++) {
        sections[i].style.display = "none";
    }

    // remove active class from all tabs
    let selectors = document.getElementsByClassName("tab");
    for (let i = 0; i < selectors.length; i++) {
        selectors[i].className = selectors[i].className.replace(" active", "");
    }
}


// open selected section
function openSection(event, section) {
    hideAllSections();    

    document.getElementById(section).style.display = "block";
    event.currentTarget.className += " active";
}


// build element object with data from form
// return null if fields missing
function buildElement() {
    const element = {};
    element.number = document.querySelector('#element-number').value;
    element.code = document.querySelector('#element-code').value;
    element.name = document.querySelector('#element-name').value;
    element.color1 = document.querySelector('#element-color1').value;
    element.color2 = document.querySelector('#element-color2').value;
    element.color3 = document.querySelector('#element-color3').value;
    element.radius = document.querySelector('#element-radius').value;

    for (const key in element) {
        if (element[key] === "") {
            alert(`Missing input in element ${key} field`);
            return null;
        }
    }

    element.number = parseInt(element.number);
    element.radius = parseInt(element.radius);

    return element;
}


// add element to element-list on client
function appendElement(element) {
    const newElement = document.createElement('option');
    newElement.text = element;
    newElement.id = `element-${element}`;

    document.querySelector("#element-list").appendChild(newElement);
}


// add molecule to molecule-list on client
function appendMolecule(molecule) {
    const newMolecule = document.createElement('option');

    newMolecule.text = molecule.name;
    newMolecule.value = molecule.name;
    newMolecule.id = `molecule-${molecule.name}`;

    document.querySelector("#molecule-list").appendChild(newMolecule);
}


// remove element from element-list
function removeElement(element) {
    const elementList = document.querySelector("#element-list");
    const optionToRemove = document.querySelector(`#element-${element}`);

    elementList.removeChild(optionToRemove);
}


// build form data object with .sdf file data
// return null if name field is empty or no file uploaded
function buildFormData() {
    const moleculeName = document.querySelector("#upload-molecule-name").value;
    if (moleculeName === "") {
        alert('Missing input in element name field');
        return null;
    }

    const formData = new FormData();
    const file = document.querySelector("#file").files[0];

    if (!file) {
        alert('No File Selected For Upload');
        return null;
    }

    formData.append('name', moleculeName);
    formData.append('file', file);

    return formData;
}


// add element to database and append to list on client
function addElementRequest() {
    const element = buildElement();
    if (element == null) {
        return;
    }

    fetch(BASE_URL + "/elements", {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'element': element})
    })
    .then(res => {
        if (res.status === 201) {
            appendElement(element.name);
        } else if (res.status !== 200) {
            alert(UNEXPECTED_ERROR);
        }
    });
}


// load elements from db to element-list
function loadElementsRequest() {
    fetch(BASE_URL + "/element_list", {method: 'GET'})
    .then(res => res.json())
    .then(res => res.elements.forEach(appendElement));
}


// load molecules from db to molecule list
function loadMoleculesRequest() {
    fetch(BASE_URL + "/molecule_list", {method: 'GET'})
    .then(res => res.json())
    .then(res => res.molecules.forEach(appendMolecule));
}


// delete element from database and from client
function deleteElementRequest() {
    const elementName = document.querySelector("#element-list").value;
    if (elementName === "") {
        return;
    }

    fetch(BASE_URL + "/elements/" + elementName, {method: 'DELETE'})
    .then(res => {
        if (res.status === 204) {
            removeElement(elementName);
        } else {
            alert(UNEXPECTED_ERROR);
        }
    });
}


// send file to server where molecule data will be stored
function uploadFileRequest() {
    const formData = buildFormData();

    fetch(BASE_URL + "/upload", {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(res => {
        alert(res.message);

        if (res.molecule) {
            appendMolecule(res.molecule);
        }
    })
    .catch(error => console.log(error));
}


// go to page to view selected molecule
function viewMoleculeRequest() {
    const molecule = document.querySelector("#molecule-list").value;
    if (molecule === "") {
        return;
    }

    window.location.href = `/molecule/${molecule}`;
}
