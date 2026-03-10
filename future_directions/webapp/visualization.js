let ecgData = [];

const ctx = document.getElementById('ecgChart');

const chart = new Chart(ctx, {

type:'line',

data:{
labels:[],
datasets:[{
label:'ECG',
data:[],
borderColor:'lime',
borderWidth:2,
pointRadius:0
}]
},

options:{
animation:false,
scales:{
x:{display:false},
y:{min:-2,max:2}
}
}

});

function updatePlot(value){

if(ecgData.length > 500)
ecgData.shift();

ecgData.push(value);

chart.data.datasets[0].data = ecgData;
chart.data.labels = ecgData.map((_,i)=>i);

chart.update();

}