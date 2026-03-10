let port;
let reader;

let buffer=[];

const fs = 250;

document.getElementById("connectBtn")
.addEventListener("click",connectSerial);

async function connectSerial(){

port = await navigator.serial.requestPort();

await port.open({baudRate:115200});

reader = port.readable.getReader();

readSerial();

}

async function readSerial(){

while(true){

const {value,done} = await reader.read();

if(done) break;

const text = new TextDecoder().decode(value);

let lines = text.split("\n");

lines.forEach(line=>{

let v = parseFloat(line);

if(!isNaN(v)){

v = applyFilter(v);

updatePlot(v);

buffer.push(v);

if(buffer.length>500)
buffer.shift();

let hr = detectPeaks(buffer,fs);

document.getElementById("bpm").innerText =
"Heart Rate: "+hr.toFixed(1)+" BPM";

}

});

}

}

function playSimulation(){

const file = document
.getElementById("fileInput")
.files[0];

const reader = new FileReader();

reader.onload = function(e){

let data = e.target.result
.split("\n")
.map(Number);

let i=0;

let sim = setInterval(()=>{

if(i>=data.length)
clearInterval(sim);

updatePlot(data[i]);

buffer.push(data[i]);

let hr = detectPeaks(buffer,fs);

document.getElementById("bpm")
.innerText="Heart Rate: "+hr.toFixed(1)+" BPM";

i++;

},20);

};

reader.readAsText(file);

}