// on page load hide all sections then open view-molecule
window.onload = function() {
    hideAllSections();
    document.getElementById("view-molecule-tab").click();
}


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


// open the selected section and set its tab active
function openSection(event, section) {

    hideAllSections();    

    // open selected section
    document.getElementById(section).style.display = "block";
    event.currentTarget.className += " active";
}


// take a comma separated string for moleculename, atom_no, bond_no
// convert it to an option element for molecule-list
function moleculeRow(csv) {
    mol_data = csv.split(",");

    // use something else instead of tables in future
    let molecule = `<option id="molecule-${mol_data[0]}"><table><tr>`;

    molecule += `<td>${mol_data[0]}</td>`;
    molecule += "<td hidden>--</td>";
    molecule += `<td>${mol_data[1]}</td>`;
    molecule += `<td>${mol_data[2]}</td>`;
    molecule += `</tr></table></option>`;

    return molecule;
}


// request molecule data from server and append it to molecule-list
function loadMoleculeList() {
    $.get("/molecule_data")
        .done(function(data) {
            console.log(data);

            // // in future change to json or something for sending the data
            // let mol_data = data.split("\n");

            // for (let i = 0; i < mol_data.length; i++) {
            //     if (mol_data[i].length > 0) {
            //         $("#molecule-list").append(moleculeRow(mol_data[i]));
            //     }
            // }
        })
        .fail(function(e) {
            console.log("Error. Couldn't Retrieve Molecule Data.");
        });
}


// take a string of \n separated element names
// load them into elements-list
function loadElementList() {
    $.get("/elements_data")
    .done(function(data) {
        console.log(data);
        
        // let elements = data.split("\n");

        // for (let i = 0; i < elements.length; i++) {
        //     if (elements[i].length > 0) {
        //         $("#element-list").append(`<option id="element-${elements[i]}">${elements[i]}</option>`);
        //     }
        // }
    })
    .fail(function(e) {
        console.log("Error. Couldn't Retrieve Elements.")
    });
}



$(document).ready(function() {

    loadMoleculeList();
    loadElementList();

    $('#upload-form').submit(function (ev) {
        ev.preventDefault();
        var formData = new FormData($(this)[0]);
        $.ajax({
            url: 'upload',
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (molecule_name) {
                $("#molecule-list").empty();
                loadMoleculeList();
                alert(`${molecule_name} Added To Database!`);
            },
            error: function (e) {
                alert(e.responseText);
            }
        });
    });


    $("#remove-element-button").click(function() {
        $.post("/remove_element",
            {
                element_name: $("#element-list").val()
            })
            .done(function(element_name) {
                $(`#element-${element_name}`).remove();
            })
            .fail(function(e) {
                console.log(e.responseText);
            });
    });


    $("#add-element-button").click(function() {
        $.post("/add_element",
            {
                element_number: $("#element-number").val(),
                element_code: $("#element-code").val(),
                element_name: $("#element-name").val(),
                color1: $("#element-color1").val(),
                color2: $("#element-color2").val(),
                color3: $("#element-color3").val(),
                radius: $("#element-radius").val()
            })
            .done(function(element_name) {
                // if element isnt being replaced
                if (element_name !== "Replaced") {
                    $("#element-list").append(`<option id="element-${element_name}">${element_name}</option>`);
                }
            })
            .fail(function(e) {
                console.log(e.responseText);
            });
    });
});