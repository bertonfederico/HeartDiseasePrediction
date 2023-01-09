function getPrediction() {
    const json = getJson();
    sendRequest(json);
}

function getJson() {
    const data = {
        BMI: document.getElementById("BMI").value,
        Smoking: document.getElementById("Smoking").value,
        AlcoholDrinking: document.getElementById("AlcoholDrinking").value,
        Stroke: document.getElementById("Stroke").value,
        PhysicalHealth: document.getElementById("PhysicalHealth").value,
        MentalHealth: document.getElementById("MentalHealth").value,
        DiffWalking: document.getElementById("DiffWalking").value,
        Sex: document.getElementById("Sex").value,
        AgeCategory: document.getElementById("AgeCategory").value,
        Race: document.getElementById("Race").value,
        Diabetic: document.getElementById("Diabetic").value,
        PhysicalActivity: document.getElementById("PhysicalActivity").value,
        GenHealth: document.getElementById("GenHealth").value,
        SleepTime: document.getElementById("SleepTime").value,
        Asthma: document.getElementById("Asthma").value,
        KidneyDisease: document.getElementById("KidneyDisease").value,
        SkinCancer: document.getElementById("SkinCancer").value
    }
    const postData = {
        id: "input",
        arguments: data
    }
    return postData
}

function sendRequest(jsonReq) {
    xhr = new XMLHttpRequest();
    const url = "http://localhost:8080/openscoring/model/HeartDisease";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const json = JSON.parse(xhr.responseText);
            document.getElementById("resultDiv").innerHTML = json.results.HeartDisease;
        }
    }
    const data = JSON.stringify(jsonReq);
    xhr.send(data);
}