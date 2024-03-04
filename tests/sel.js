const instrument = document.getElementById("instrument");
const mood = document.getElementById("mood");
const genre = document.getElementById("genre");
const song = document.getElementById("song");
document.addEventListener("DOMContentLoaded", () => {
	fetch("audiolibrary.json").then((response) => {
		response.json().then((data) => {
			//genre
			for (let item of data){
			  
			}
		});
	});
	/*	fetch("instr.json").then((response) => {
	  	response.json().then((data) => {
	  		for (let x of data) {
	  			let o = document.createElement("option");
	  			o.text = x;
	  			o.value = x;

				instrument.appendChild(o);
				pd.innerText = instrument.innerHTML;
			}
		});
	}); */
});
