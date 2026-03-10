let currentFilter = "none";

function setFilter(name){

currentFilter = name;

console.log("Filter:",name);

}

function applyFilter(x){

switch(currentFilter){

case "butterworth":
return x;

case "chebyshev":
return x;

case "kalman":
return x;

case "adaptive":
return x;

default:
return x;

}

}