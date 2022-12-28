document.getElementById("filter_submit_btn").onclick=function(){
    var team_attrs_dict = team_attributes

    var filter_attrs = document.getElementsByName('filter_attr');
    var filter_attr;
    for(i = 0; i < filter_attrs.length; i++) {
        if(filter_attrs[i].checked)
        filter_attr=filter_attrs[i].value;
    }

    var operators = document.getElementsByName('operator');
    var operator;
    for(i = 0; i < operators.length; i++) {
        if(operators[i].checked)
        operator=operators[i].value;
    }
    var firstNumber=document.getElementById('first_number').value;

    var eliminated_teams=[];
    for (const [team_number, team_attr] of Object.entries(team_attrs_dict)) {
        var shouldEliminate=false;
        switch(operator) {
            case "greater than":
                var attr_list = team_attr[filter_attr].map(function (x) { return parseInt(x, 10);});
                console.log(attr_list)
                var average=attr_list.reduce((acc, c) => acc + c, 0);
                average/=attr_list.length;
                shouldEliminate=average<firstNumber;
                break;
            case "less than":
                shouldEliminate=average>firstNumber;
              // code block
                break;
            case "equal to":
                shouldEliminate=average!=firstNumber;
              // code block
              break;
            default:
              // code block
          }
        if(shouldEliminate){
            eliminated_teams.push(team_number);
        }
    }
    console.log(eliminated_teams)
    for (const eliminated_team of eliminated_teams){
        document.getElementById("team_entry_"+eliminated_team).style.display="none";
    }

};

var team_id_els=document.getElementsByClassName("team_id");
for(var team_id_el of team_id_els){
    team_id_el.onclick=function(e){
        var team_id=e.target.innerHTML;
        document.getElementById("main_div").style.display="none";
        console.log("team_attrs_table_"+team_id);
        console.log(document.getElementById("team_attrs_table_"+team_id))
        document.getElementById("team_attrs_table_"+team_id).style.display="inline-block";
    };
}
