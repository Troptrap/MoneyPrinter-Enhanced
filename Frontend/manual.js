const videoSubject = document.querySelector("#videoSubject");
const aiModel = document.querySelector("#aiModel");
const g4fmodel = document.querySelector("#g4fm");

const paragraphNumber = document.querySelector("#paragraphNumber");
const generateButton = document.querySelector("#generateButton");
const cancelButton = document.querySelector("#cancelButton");

const textareaElem = document.getElementById("script-text");

var lastMessage = "";
var script = "";

function nextSaveAsObj() {
	const scriptTextDiv = document.getElementById("script-text");

	const scriptData = {};

	// Loop through all child elements of the scriptTextDiv
	for (const element of scriptTextDiv.children) {
		if (element.tagName === "INPUT" && element.id.startsWith("title")) {
			const titleIndex = parseInt(element.id.slice(6)); // Extract the index from id
			scriptData[titleIndex] = scriptData[titleIndex] || {}; // Initialize if not existing
			scriptData[titleIndex].title = element.value;
		} else if (element.tagName === "P" && element.id.startsWith("text")) {
			const textIndex = parseInt(element.id.slice(5)); // Extract the index from id
			scriptData[textIndex] = scriptData[textIndex] || {}; // Initialize if not existing
			scriptData[textIndex].text = element.innerText;
		}
	}

	console.log(scriptData); // This will now contain the desired object structure
	fetch("/api/save-script", {
		method: "POST",
		body: JSON.stringify(scriptData),
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json"
		}
	})
		.then((response) => response.json())
		.then((data) => {
			if (data == "Script saved") {
				window.location.href = "/manual-audio.html";
			} else {
				nextBtn.classList.remove("bg-blue-500");
				nextBtn.classList.remove("hover:bg-blue-700");
				nextBtn.classList.add("bg-red-500");
				nextBtn.innerHTML = "Error saving script";
			}
		});
}

nextBtn = document.getElementById("next");
nextBtn.addEventListener("click", nextSaveAsObj);

function insertScriptText(data) {
	textareaElem.classList.add(
		"border-2",
		"border-blue-300",
		"p-2",
		"rounded-md",
		"focus:outline-none",
		"focus:border-blue-500"
	);
	textareaElem.contentEditable = true;
	textareaElem.insertAdjacentHTML("beforeend", data);
}

function checkForMessages() {
	fetch("/check_messages")
		.then((response) => response.json())
		.then((data) => {
			if (data !== lastMessage) {
				const msgDiv = document.getElementById("message");
				const stdOut = document.getElementById("stdout");
				if (!data.startsWith("Script text")) {
					msgDiv.innerHTML += data + "<br/>";
				}
				if (data.startsWith("Script text:")) {
					data = data.replace("Script text: ", "");
					if (data !== script) {
						script = data;
						insertScriptText(stdout, script);
					}
				}
				/*	if (data.startsWith("Audio generation")) {
					playVoiceover(stdOut);
				} */
				lastMessage = data;
			}
		});
}

function listFreeModels() {
	if (aiModel.value === "g4f") {
		g4fmodel.classList.remove("hidden");
		fetch("/g4f-models")
			.then((response) => response.json())
			.then((data) => {
				for (let item of data) {
					let option = document.createElement("option");
					option.text = item;
					option.value = item;
					if (option.value == "mixtral-8x7b") {
						option.setAttribute("selected", "selected");
					}
					g4fmodel.appendChild(option);
				}
			});
	} else {
		g4fmodel.innerHTML = "";
		g4fmodel.classList.add("hidden");
	}
}

document.addEventListener("DOMContentLoaded", () => {
	listFreeModels();
	aiModel.addEventListener("change", listFreeModels);
});

const cancelGeneration = () => {
	console.log("Canceling generation...");
	// Send request to /cancel
	fetch("api/cancel", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json"
		}
	})
		.then((response) => response.json())
		.then((data) => {
			alert(data.message);
			console.log(data);
		})
		.catch((error) => {
			alert("An error occurred. Please try again later.");
			console.log(error);
		});

	// Hide cancel button
	cancelButton.classList.add("hidden");

	// Enable generate button
	generateButton.disabled = false;
	generateButton.classList.remove("hidden");
};

const generateVideoScript = () => {
	// Check for messages every second
	const msgInterval = setInterval(checkForMessages, 1000);
	console.log("Generating script...");
	// Disable button and change text
	generateButton.disabled = true;
	generateButton.classList.add("hidden");

	// Show cancel button
	cancelButton.classList.remove("hidden");

	// Get values from input fields
	const videoSubjectValue = videoSubject.value;
	const aiModelValue = aiModel.value;
	const g4fmodelValue = g4fmodel.value;

	const subtopicNumberValue = subtopicNumber.value;
	const paragraphNumberValue = paragraphNumber.value;

	const generateScriptUrl = "api/generate-script";

	// Construct data to be sent to the server
	const data = {
		videoSubject: videoSubjectValue,
		aiModel: aiModelValue,
		g4fmodel: g4fmodelValue,
		subtopicNumber: subtopicNumberValue,
		paragraphNumber: paragraphNumberValue
	};
	textareaElem.innerHTML = "";
					nextBtn.classList.add("bg-blue-500");
				nextBtn.classList.add("hover:bg-blue-700");
	nextBtn.innerHTML = "Next >> Audio Creation";

	// Send the actual request to the server
	fetch(generateScriptUrl, {
		method: "POST",
		body: JSON.stringify(data),
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json"
		}
	})
		.then((response) => response.json())
		.then((data) => {
			console.log(data);

			Object.keys(data).forEach((item) => {
				const title = `<input id="title-${item}" type="hidden" value="${data[item]["title"]}"/>`;
				const text = `<p id="text-${item}" class="bg-white-400 text-black border-2 border-blue-300 p-2 rounded-md focus:outline-none focus:border-blue-500">${data[item]["text"]}</p>`;
				insertScriptText(title);
				insertScriptText(text);
			});

			generateButton.disabled = false;
			generateButton.classList.remove("hidden");
			cancelButton.classList.add("hidden");
			clearInterval(msgInterval);
		})
		.catch((error) => {
			alert("An error occurred. Please try again later.");
			console.log(error);
		});
};

generateButton.addEventListener("click", generateVideoScript);
cancelButton.addEventListener("click", cancelGeneration);

videoSubject.addEventListener("keyup", (event) => {
	if (event.key === "Enter") {
		generateVideoScript();
	}
});
