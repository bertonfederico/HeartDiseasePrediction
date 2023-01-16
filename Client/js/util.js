addIntDropDown("PhysicalHealth_opt", 0, 30);
addIntDropDown("MentalHealth_opt", 0, 30);
addIntDropDown("SleepTime_opt", 0, 24);


function addIntDropDown(dropdownId, min, max) {
    selectMenu = document.getElementById(dropdownId);
    for (let i = min; i <= max; i++) {
        const tempOption = document.createElement("option");
        tempOption.setAttribute("value", [i]);
        tempOption.innerHTML = i;
        selectMenu.appendChild(tempOption);
    }
}