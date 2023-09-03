window.onload = function() {
    hideAllSections();

    document.querySelector('#view-molecule-tab').click();
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

function openSection(event, section) {

    hideAllSections();    

    // open selected section
    document.getElementById(section).style.display = "block";
    event.currentTarget.className += " active";
}