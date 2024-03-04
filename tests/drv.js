let p = document.getElementById("p");
fetch(
	"https://drive.usercontent.google.com/download?id=1GgOgE_S_r4yvRyo0X9VVdEDfOMdWoux0&export=open"
).then(response => {
  
  if (response.ok){
    
    
	console.log("ok");
  }
}
)