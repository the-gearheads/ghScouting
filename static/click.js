// https://stackoverflow.com/a/62259593/13299016
const tbody = document.querySelector('#position tbody');
tbody.addEventListener('click', function(e) {
    const cell = e.target.closest('td');
    if (!cell) {
        return;
    } // Quit, not clicked on a cell
    const row = cell.parentElement;
    if (cell.cellIndex === 0) {
        team_number = row.innerText.split('\t')[0];
        team_score = row.innerText.split('\t')[1];
        console.log(team_number, team_score);
//        data = new FormData();
//        data.set('team_number', team_number);
//        data.set('team_score', team_score);
//
//        let request = new XMLHttpRequest();
//        request.open("POST", '/stats', true);
//        request.send(data);
//        request.onreadystatechange = function() {
//            if (request.readyState === 4 && request.status === 200) {
//                window.location = request.response;
//            }
//        }
        console.log(team_attributes[team_number])

        table = document.getElementById("attributes_table")
        // header row, probably a less verbose way to do this. someone ask chatgpt
        var table_row = table.insertRow(-1);
        var name_column = document.createElement("TH")
        name_column.innerHTML = "Attribute Name"
        table_row.appendChild(name_column);
        var name_column = document.createElement("TH")
        name_column.innerHTML = "Attribute range/values"
        table_row.appendChild(name_column);
        //
        Object.entries(team_attributes[team_number]).forEach(function([attr_name, attr_values_list]) {
            if (configuration['values'][attr_name]) {
                str_attribute = [...new Set(attr_values_list)].join(", ");
                console.log(str_attribute);
            }
            else {
                str_attribute = `${Math.max(...attr_values_list)} - ${Math.min(...attr_values_list)}`;
                console.log(str_attribute);
            }

            table_row = table.insertRow(-1);
            name_column = document.createElement("TH")
            name_column.innerHTML = attr_name
            table_row.appendChild(name_column);
            var attr_column = document.createElement("TH")
            attr_column.innerHTML = str_attribute
            table_row.appendChild(attr_column);
        });
        table.style.display = 'inline-block'
        best_teams_table = document.getElementById("position");
        best_teams_table.style.display = 'none';
        // sets new location for back key
        window.history.pushState({}, "", window.location.href.split("#")[0] + "#newhashvalue");
    }
});

// goes back to main stats page from a team attributes page
function best_teams_page() {
    table = document.getElementById("attributes_table")
    table.style.display = 'none'
    best_teams_table = document.getElementById("position");
    best_teams_table.style.display = 'inline-block';
}

// needed for going back to best teams page on back button click, instead of actual previous page
window.onpopstate = function(event) {
    console.log("popstate event triggered:" + event)
    if (location.hash = '#teampage') {
        best_teams_page();
        window.history.pushState({}, "", window.location.href.split("#")[0] + "");
    } else {
        history.back();
    }
}