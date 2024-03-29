const videoSubject = document.querySelector("#videoSubject");
const aiModel = document.querySelector("#aiModel");
const g4fmodel = document.querySelector("#g4fm");
const voice = document.querySelector("#voice");
const paragraphNumber = document.querySelector("#paragraphNumber");
const youtubeToggle = document.querySelector("#youtubeUploadToggle");
const useMusicToggle = document.querySelector("#useMusicToggle");

const customPrompt = document.querySelector("#customPrompt");
const generateButton = document.querySelector("#generateButton");
const cancelButton = document.querySelector("#cancelButton");
const outvid = document.querySelector("#outvid");
const mslang = document.getElementById("mslang");
const microsoftvoice = document.getElementById("microsoftvoice");
const tiktokvoice = document.getElementById("tiktokvoice");
const AudioLibrary = document.getElementById("audiolibrary");
const AudioLibraryTable = document.getElementById("audiolibrarytable");
const advancedOptionsToggle = document.querySelector("#advancedOptionsToggle");
const bgSong = document.getElementById("bgSong");
const PlayerSelector = document.getElementById("songplayer");
let currentTTS = "microsoft";
let videoformat = "portrait";

var lastMessage = "";
var script = "";
function insertScriptText(elem, data) {
	textareaElem = document.createElement("textarea");
	textareaElem.classList.add(
		"border-2",
		"border-blue-300",
		"p-2",
		"rounded-md",
		"focus:outline-none",
		"focus:border-blue-500"
	);
	textareaElem.rows = 8;
	textareaElem.value = data;
	elem.appendChild(textareaElem);
}
function playVoiceover(elem) {
	player = document.createElement("audio");
	player.controls = "controls";
	player.src = "../Frontend/ttsoutput.mp3";
	elem.appendChild(player);
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
				if (data.startsWith("Audio generation")) {
				  playVoiceover(stdOut);
				}
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

advancedOptionsToggle.addEventListener("click", () => {
	// Change Emoji, from ▼ to ▲ and vice versa
	const emoji = advancedOptionsToggle.textContent;
	advancedOptionsToggle.textContent = emoji.includes("▼")
		? "Show less Options ▲"
		: "Show Advanced Options ▼";
	const advancedOptions = document.querySelector("#advancedOptions");
	advancedOptions.classList.toggle("hidden");
});
useMusicToggle.addEventListener("click", () => {
	if (useMusicToggle.checked == true) {
		AudioLibrary.classList.remove("hidden");
		AudioLibraryTable.classList.remove("hidden");
		PlayerSelector.classList.remove("hidden");
		grabRandomSong();
	} else {
		AudioLibrary.classList.add("hidden");
		AudioLibraryTable.classList.add("hidden");
		PlayerSelector.classList.add("hidden");
	}
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

const generateVideo = () => {
	// Check for messages every second
	const msgInterval = setInterval(checkForMessages, 1000);
	console.log("Generating video...");
	// Disable button and change text
	generateButton.disabled = true;
	generateButton.classList.add("hidden");
	outvid.classList.add("hidden");

	// Show cancel button
	cancelButton.classList.remove("hidden");

	// Get values from input fields
	const videoSubjectValue = videoSubject.value;
	const aiModelValue = aiModel.value;
	const g4fmodelValue = g4fmodel.value;
	const voiceValue =
		currentTTS == "tiktok"
			? tiktokvoice.value
			: currentTTS == "microsoft"
			? microsoftvoice.value
			: "Oops..error";
	const paragraphNumberValue = paragraphNumber.value;
	const youtubeUpload = youtubeToggle.checked;
	const useMusicToggleState = useMusicToggle.checked;
	const bgSongValue = bgSong.value;
	const customPromptValue = customPrompt.value;
	const subtitlesPosition =
		document.querySelector("#subtitlesPosition").value;

	const url = "api/generate";

	// Construct data to be sent to the server
	const data = {
		videoSubject: videoSubjectValue,
		aiModel: aiModelValue,
		g4fmodel: g4fmodelValue,
		ttsengine: currentTTS,
		voice: voiceValue,
		format: videoformat,
		paragraphNumber: paragraphNumberValue,
		automateYoutubeUpload: youtubeUpload,
		useMusic: useMusicToggleState,
		bgSong: bgSongValue,
		subtitlesPosition: subtitlesPosition,
		customPrompt: customPromptValue
	};

	// Send the actual request to the server
	fetch(url, {
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
			//alert(data.message);
			// Hide cancel button after generation is complete

			generateButton.disabled = false;
			generateButton.classList.remove("hidden");
			cancelButton.classList.add("hidden");
			outvid.classList.remove("hidden");
			outvid.src = data.data;
			clearInterval(msgInterval);
		})
		.catch((error) => {
			alert("An error occurred. Please try again later.");
			console.log(error);
		});
};

generateButton.addEventListener("click", generateVideo);
cancelButton.addEventListener("click", cancelGeneration);

videoSubject.addEventListener("keyup", (event) => {
	if (event.key === "Enter") {
		generateVideo();
	}
});

function getengine(e) {
	currentTTS = e.id;
	if (currentTTS == "microsoft") {
		tiktokvoice.classList.add("hidden");
		microsoftvoice.classList.remove("hidden");
		mslang.classList.remove("hidden");
		langlist.classList.remove("hidden");
	}
	if (currentTTS == "tiktok") {
		tiktokvoice.classList.remove("hidden");
		microsoftvoice.classList.add("hidden");
		mslang.classList.add("hidden");
		langlist.classList.add("hidden");
	}
}
function getformat(e) {
	videoformat = e.id;
	console.log(videoformat);
}

function msft_voice(loc) {
	fetch("microsoft_voices.json").then((response) => {
		response.json().then((data) => {
			let locales = Object.keys(data);
			microsoftvoice.innerHTML = "";
			for (const locale of locales) {
				if (locale.startsWith(loc)) {
					data[locale].forEach((v) => {
						const option = document.createElement("option");
						option.text = Object.values(v)[0];
						option.value = Object.keys(v)[0];
						microsoftvoice.appendChild(option);
					});
				}
			}
		});
	});
}

function grabAll(url) {
	return fetch(url)
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			return data;
		});
}

document.addEventListener("DOMContentLoaded", () => {
	msft_voice("en");
	mslang.addEventListener("input", () => {
		msft_voice(mslang.value);
	});
});
fetch("microsoft_voices.json").then((response) => {
	response.json().then((all) => {
		const langcomplete = new autoComplete({
			// API Advanced Configuration Object

			selector: "#mslang",
			placeHolder: "Your locale ..",
			data: {
				src: Object.keys(all),
				cache: true
			},
			resultsList: {
				element: (list, data) => {
					if (!data.results.length) {
						// Create "No Results" message element
						const message = document.createElement("div");
						// Add class to the created element
						message.setAttribute("class", "no_result");
						// Add message text content
						message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
						// Append message element to the results list
						list.prepend(message);
					}
				},
				noResults: true
			},
			resultItem: {
				highlight: true
			},
			submit: true,
			events: {
				input: {
					selection: (event) => {
						const selection = event.detail.selection.value;
						langcomplete.input.value = selection;
						mslang.dispatchEvent(new Event("input"));
					}
				}
			}
		});
	});

	const allArtists = grabAll("/songs/artists").then((all) => {
		const artistcomplete = new autoComplete({
			// API Advanced Configuration Object

			selector: "#artist",
			placeHolder: "Search for Artist...",
			data: {
				src: all,
				cache: true
			},
			resultsList: {
				element: (list, data) => {
					if (!data.results.length) {
						// Create "No Results" message element
						const message = document.createElement("div");
						// Add class to the created element
						message.setAttribute("class", "no_result");
						// Add message text content
						message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
						// Append message element to the results list
						list.prepend(message);
					}
				},
				noResults: true
			},
			resultItem: {
				highlight: true
			},
			events: {
				input: {
					selection: (event) => {
						const selection = event.detail.selection.value;
						artistcomplete.input.value = selection;
					}
				}
			}
		});
	});
	const allTitles = grabAll("/songs/titles").then((all) => {
		const titlecomplete = new autoComplete({
			// API Advanced Configuration Object

			selector: "#songtitle",
			placeHolder: "Search Titles...",
			data: {
				src: all,
				cache: true
			},
			resultsList: {
				element: (list, data) => {
					if (!data.results.length) {
						// Create "No Results" message element
						const message = document.createElement("div");
						// Add class to the created element
						message.setAttribute("class", "no_result");
						// Add message text content
						message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
						// Append message element to the results list
						list.prepend(message);
					}
				},
				noResults: true
			},
			resultItem: {
				highlight: true
			},
			events: {
				input: {
					selection: (event) => {
						const selection = event.detail.selection.value;
						titlecomplete.input.value = selection;
					}
				}
			}
		});
	});

	const allGenres = grabAll("/songs/genres").then((all) => {
		const genrecomplete = new autoComplete({
			// API Advanced Configuration Object

			selector: "#genre",
			placeHolder: "Search for Genre...",
			data: {
				src: all,
				cache: true
			},
			resultsList: {
				element: (list, data) => {
					if (!data.results.length) {
						// Create "No Results" message element
						const message = document.createElement("div");
						// Add class to the created element
						message.setAttribute("class", "no_result");
						// Add message text content
						message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
						// Append message element to the results list
						list.prepend(message);
					}
				},
				noResults: true
			},
			resultItem: {
				highlight: true
			},
			events: {
				input: {
					selection: (event) => {
						const selection = event.detail.selection.value;
						genrecomplete.input.value = selection;
					}
				}
			}
		});
	});
	const allInstruments = grabAll("/songs/instruments").then((all) => {
		const instrumentcomplete = new autoComplete({
			// API Advanced Configuration Object

			selector: "#instrument",
			placeHolder: "Search for Instrument...",
			data: {
				src: all,
				cache: true
			},
			resultsList: {
				element: (list, data) => {
					if (!data.results.length) {
						// Create "No Results" message element
						const message = document.createElement("div");
						// Add class to the created element
						message.setAttribute("class", "no_result");
						// Add message text content
						message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
						// Append message element to the results list
						list.prepend(message);
					}
				},
				noResults: true
			},
			resultItem: {
				highlight: true
			},
			events: {
				input: {
					selection: (event) => {
						const selection = event.detail.selection.value;
						instrumentcomplete.input.value = selection;
					}
				}
			}
		});
	});

	grabAll("/songs/moods").then((moods) => {
		const moodSelect = document.getElementById("mood");
		for (let mood of moods) {
			option = document.createElement("option");
			option.text = mood;
			option.value = mood;
			moodSelect.appendChild(option);
		}
	});

	// inside DOMContentLoaded

	const ArtistSelector = document.getElementById("artist");
	const TitleSelector = document.getElementById("songtitle");
	const MoodSelector = document.getElementById("mood");
	const GenreSelector = document.getElementById("genre");
	const InstrumentSelector = document.getElementById("instrument");
	const RandomArtistSelector = document.getElementById("randomArtist");
	const RandomTitleSelector = document.getElementById("randomTitle");
	const RandomMoodSelector = document.getElementById("randomMood");
	const RandomGenreSelector = document.getElementById("randomGenre");
	const RandomInstrumentSelector =
		document.getElementById("randomInstrument");
	RandomArtistSelector.addEventListener("change", () => {
		if (RandomArtistSelector.checked) {
			ArtistSelector.classList.add("hidden");
		} else {
			ArtistSelector.classList.remove("hidden");
		}
	});
	RandomTitleSelector.addEventListener("change", () => {
		if (RandomTitleSelector.checked) {
			TitleSelector.classList.add("hidden");
		} else {
			TitleSelector.classList.remove("hidden");
		}
	});
	RandomMoodSelector.addEventListener("change", () => {
		if (RandomMoodSelector.checked) {
			MoodSelector.classList.add("hidden");
		} else {
			MoodSelector.classList.remove("hidden");
		}
	});
	RandomGenreSelector.addEventListener("change", () => {
		if (RandomGenreSelector.checked) {
			GenreSelector.classList.add("hidden");
		} else {
			GenreSelector.classList.remove("hidden");
		}
	});
	RandomInstrumentSelector.addEventListener("change", () => {
		if (RandomInstrumentSelector.checked) {
			InstrumentSelector.classList.add("hidden");
		} else {
			InstrumentSelector.classList.remove("hidden");
		}
	});

	function querySongs() {
		let params = {};
		let randomartist = RandomArtistSelector.checked;
		if (randomartist == false) {
			params["artist"] = ArtistSelector.value;
		}
		let randomtitle = RandomTitleSelector.checked;
		if (randomtitle == false) {
			params["title"] = TitleSelector.value;
		}
		let randommood = RandomMoodSelector.checked;
		if (randommood == false) {
			params["mood"] = MoodSelector.value;
		}
		let randomgenre = RandomGenreSelector.checked;
		if (randomgenre == false) {
			params["genre"] = GenreSelector.value;
		}
		let randominstrument = RandomInstrumentSelector.checked;
		if (randominstrument == false) {
			params["instrument"] = InstrumentSelector.value;
		}

		let url = new URL("/songs", window.location.href);
		url.search = new URLSearchParams(params).toString();
		fetch(url)
			.then((response) => response.json())
			.then((data) => {
				AudioLibraryTable.innerHTML = "";
				for (let k of Object.keys(data)) {
					let songelem = document.createElement("tr");
					songelem.tabIndex = "0";

					let artistelem = document.createElement("td");
					artistelem.innerText = data[k]["artist"];
					songelem.appendChild(artistelem);
					let titleelem = document.createElement("td");
					titleelem.innerText = data[k]["title"];
					songelem.appendChild(titleelem);
					let moodelem = document.createElement("td");
					moodelem.innerText = data[k]["mood"];
					songelem.appendChild(moodelem);
					let genreelem = document.createElement("td");
					genreelem.innerText = data[k]["genre"];
					songelem.appendChild(genreelem);
					let urlelem = document.createElement("input");
					urlelem.type = "hidden";
					urlelem.value = data[k]["url"];
					songelem.appendChild(urlelem);

					AudioLibraryTable.appendChild(songelem);
				}
			})
			.catch((error) => {
				console.error(error);
			});
	}
	AudioLibrary.addEventListener("change", () => {
		// inside audiolibrary event
		querySongs();
	});
	AudioLibraryTable.addEventListener("click", (e) => {
		let url = e.target.parentNode.querySelector("input").value;
		let id = url.replace("http://docs.google.com/uc?export=open&id=", "");
		PlayerSelector.innerHTML = `<div id="fountainG">
	<div id="fountainG_1" class="fountainG"></div>
	<div id="fountainG_2" class="fountainG"></div>
	<div id="fountainG_3" class="fountainG"></div>
	<div id="fountainG_4" class="fountainG"></div>
	<div id="fountainG_5" class="fountainG"></div>
	<div id="fountainG_6" class="fountainG"></div>
	<div id="fountainG_7" class="fountainG"></div>
	<div id="fountainG_8" class="fountainG"></div>
</div>`;
		fetch("/songs/download/" + id)
			.then((response) => response.json())
			.then((data) => {
				if (data["downloaded"] == "true") {
					src = data["filename"];
					PlayerSelector.innerHTML = `<audio controls autoplay>
  <source src=${src}>
Your browser does not support the audio element.
</audio>`;
				}
			});
	});
	function grabRandomSong() {
		fetch("/songs").then((response) =>
			response.json().then((data) => {
				let songs = Object.keys(data);
				let randomSong =
					songs[Math.floor(Math.random() * songs.length)];
				let song = data[randomSong];
				let artist = song["artist"];
				let title = song["title"];
				let id = song["url"].replace(
					"http://docs.google.com/uc?export=open&id=",
					""
				);
				fetch("/songs/download/" + id)
					.then((response) => response.json())
					.then((data) => {
						if (data["downloaded"] == "true") {
							src = data["filename"];
							bgSong.value = src;
							PlayerSelector.innerHTML = `<audio controls >
  <source src=${src}>
Your browser does not support the audio element.
</audio>`;
						}
					});
			})
		);
	}
	grabRandomSong();
});
