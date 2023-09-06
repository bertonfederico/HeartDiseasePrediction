function getPrediction() {
    const json = getJson();
    sendRequest(json);
}

function getJson() {
    const data = {
        bmi: document.getElementById("BMI_opt").value,
        smoking: document.getElementById("Smoking_opt").value,
        alcoholdrinking: document.getElementById("AlcoholDrinking_opt").value,
        stroke: document.getElementById("Stroke_opt").value,
        physicalhealth: document.getElementById("PhysicalHealth_opt").value,
        mentalhealth: document.getElementById("MentalHealth_opt").value,
        diffwalking: document.getElementById("DiffWalking_opt").value,
        sex: document.getElementById("Sex_opt").value,
        agecategory: document.getElementById("AgeCategory_opt").value,
        race: document.getElementById("Race_opt").value,
        diabetic: document.getElementById("Diabetic_opt").value,
        physicalactivity: document.getElementById("PhysicalActivity_opt").value,
        genhealth: document.getElementById("GenHealth_opt").value,
        sleeptime: document.getElementById("SleepTime_opt").value,
        asthma: document.getElementById("Asthma_opt").value,
        kidneydisease: document.getElementById("KidneyDisease_opt").value,
        skincancer: document.getElementById("SkinCancer_opt").value
    }
    const postData = {
        id: "input",
        arguments: data
    }
    return postData
}

function sendRequest(jsonReq) {
    showTab(17);
    xhr = new XMLHttpRequest();
    const url = "http://localhost:8080/openscoring/model/HeartDisease";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const json = JSON.parse(xhr.responseText);
            document.getElementById("prediction").innerHTML = json.results.heartdisease;
            document.getElementById("probability").innerHTML = json.results["probability(" + json.results.heartdisease + ")"];
            showTab(18);
        }
    }
    const data = JSON.stringify(jsonReq);
    xhr.send(data);
}

function registerResponse() {
    showTab(19);
    const currentdate = new Date(); ;
    let date_id = "" + currentdate.getFullYear() + (currentdate.getMonth()+1) + currentdate.getDate() + currentdate.getHours() + currentdate.getMinutes() + currentdate.getSeconds();
    if (location.hostname != "") {
        date_id += date_id + location.hostname;
    }
    const json = {
        id: date_id,
        bmi: Number(document.getElementById("BMI_opt").value),
        smoking: document.getElementById("Smoking_opt").value,
        alcoholdrinking: document.getElementById("AlcoholDrinking_opt").value,
        stroke: document.getElementById("Stroke_opt").value,
        physicalhealth: Number(document.getElementById("PhysicalHealth_opt").value),
        mentalhealth: Number(document.getElementById("MentalHealth_opt").value),
        diffwalking: document.getElementById("DiffWalking_opt").value,
        sex: document.getElementById("Sex_opt").value,
        agecategory: document.getElementById("AgeCategory_opt").value,
        race: document.getElementById("Race_opt").value,
        diabetic: document.getElementById("Diabetic_opt").value,
        physicalactivity: document.getElementById("PhysicalActivity_opt").value,
        genhealth: document.getElementById("GenHealth_opt").value,
        sleeptime: Number(document.getElementById("SleepTime_opt").value),
        asthma: document.getElementById("Asthma_opt").value,
        kidneydisease: document.getElementById("KidneyDisease_opt").value,
        skincancer: document.getElementById("SkinCancer_opt").value,
        heartdisease: document.getElementById("HeartDiseaseResponse").value
    }
    const postData = {
        id: "input",
        arguments: json
    }
    xhr = new XMLHttpRequest();
    const url = "http://127.0.0.1:5000/insert";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const json = JSON.parse(xhr.responseText);
            document.getElementById("prediction");
        }
    }
    const data = JSON.stringify(postData);
    xhr.send(data);
}