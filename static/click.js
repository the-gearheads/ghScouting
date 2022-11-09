// thanks Teemu
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
        data = new FormData();
        data.set('team_number', team_number);
        data.set('team_score', team_score);

        let request = new XMLHttpRequest();
        request.open("POST", '/stats', true);
        request.send(data);
        request.onreadystatechange = function() {
            if (request.readyState === 4 && request.status === 200) {
                window.location = request.response;
            }
        }
    }
});