function detectPeaks(signal, fs){

let peaks = [];

for(let i=1;i<signal.length-1;i++){

if(signal[i] > signal[i-1] &&
signal[i] > signal[i+1] &&
signal[i] > 0.6*Math.max(...signal)){

peaks.push(i);

}

}

let rr=[];

for(let i=1;i<peaks.length;i++)
rr.push((peaks[i]-peaks[i-1])/fs);

if(rr.length===0)
return 0;

let avg = rr.reduce((a,b)=>a+b)/rr.length;

return 60/avg;

}