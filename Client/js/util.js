addIntDropDown("PhysicalHealth", 0, 30);
addIntDropDown("MentalHealth", 0, 30);
addIntDropDown("SleepTime", 0, 24);


function addIntDropDown(dropdownId, min, max) {
    selectMenu = document.getElementById(dropdownId);
    for (let i = min; i <= max; i++) {
        const tempOption = document.createElement("option");
        tempOption.setAttribute("value", [i]);
        tempOption.innerHTML = i;
        selectMenu.appendChild(tempOption);
    }
}

function addLooadingGif() {
    resultDiv = document.getElementById("resultDiv");
    const image = document.createElement("img");
    image.src = "./res/loading.gif";
    resultDiv.appendChild(image);
}