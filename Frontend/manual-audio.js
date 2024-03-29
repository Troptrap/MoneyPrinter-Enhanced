const generateAButton = document.querySelector("#generateAButton");
const cancelAButton = document.querySelector("#cancelAButton");
const mslang = document.getElementById("mslang");
const microsoftvoice = document.getElementById("microsoftvoice");
const tiktokvoice = document.getElementById("tiktokvoice");
const AudioLibrary = document.getElementById("audiolibrary");
const AudioLibraryTable = document.getElementById("audiolibrarytable");
const advancedOptionsToggle = document.querySelector("#advancedOptionsToggle");
const bgSong = document.getElementById("bgSong");
const PlayerSelector = document.getElementById("songplayer");
const ArtistSelector = document.getElementById("artist");
const TitleSelector = document.getElementById("songtitle");
const MoodSelector = document.getElementById("mood");
const GenreSelector = document.getElementById("genre");
const InstrumentSelector = document.getElementById("instrument");
const RandomArtistSelector = document.getElementById("randomArtist");
const RandomTitleSelector = document.getElementById("randomTitle");
const RandomMoodSelector = document.getElementById("randomMood");
const RandomGenreSelector = document.getElementById("randomGenre");
const RandomInstrumentSelector = document.getElementById("randomInstrument");

const ttsdiv = document.getElementById("ttsdiv");
const sample = document.getElementById("sample");
const sampleInner = document.getElementById("sample-inner");
const samplePlayer = document.getElementById("sample-player");
const showSample = document.getElementById("show-sample");
const playSample = document.getElementById("play-sample");
const textareaElem = document.getElementById("script-text");
const back = document.getElementById("back-script");
const forward = document.getElementById("forward-media");
let currentTTS = "microsoft";
var lastMessage = "";
var script = "";
let sampleShow = false;

function showHideSample() {
	if (!sampleShow) {
		sampleShow = true;
		sampleInner.classList.remove("hidden");
		showSample.innerHTML = "Hide sample";
	} else {
		sampleShow = false;
		sampleInner.classList.add("hidden");
		showSample.innerHTML = "Listen sample";
	}
}

function populateScript() {
	fetch("script.json")
		.then((response) => response.json())
		.then((data) => {
			console.log(data);
			Object.keys(data).forEach((item) => {
				const text = data[item].text;
				textareaElem.insertAdjacentHTML("beforeend", `<p>${text}</p>`);
			});
		});
}

function sampleVoice() {
	const sampleText = document.getElementById("sample-text").innerText;
	const voiceValue =
		currentTTS == "tiktok"
			? tiktokvoice.value
			: currentTTS == "microsoft"
			? microsoftvoice.value
			: "Oops..error";
	const data = {
		script: sampleText,
		ttsengine: currentTTS,
		voice: voiceValue
	};

	// Send the actual request to the server
	fetch("/generate-sample", {
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
			samplePlayer.src =
				"../Frontend/sample.mp3?cb=" + new Date().getTime();
		})
		.catch((error) => {
			alert("An error occurred. Please try again later.");
			console.log(error);
		});
}

function playVoiceover(elem) {
	player = document.createElement("audio");
	player.controls = "controls";
	player.src = "../Frontend/ttsoutput.mp3";
	elem.appendChild(player);
}

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

function grabRandomSong() {
	fetch("/songs").then((response) =>
		response.json().then((data) => {
			let songs = Object.keys(data);
			let randomSong = songs[Math.floor(Math.random() * songs.length)];
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

function voiceOptions() {
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
					maxResults: 20,
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

		grabRandomSong();
	});
}

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
	cancelAButton.classList.add("hidden");

	// Enable generate button
	generatAButton.disabled = false;
	generateAButton.classList.remove("hidden");
};
const generateVideoAudio = () => {
	console.log("Generating audio...");
	// Disable button and change text
	generateAButton.classList.add("hidden");
	cancelAButton.classList.remove("hidden");
	generateAButton.disabled = true;

	const voiceValue =
		currentTTS == "tiktok"
			? tiktokvoice.value
			: currentTTS == "microsoft"
			? microsoftvoice.value
			: "Oops..error";
	const useMusicToggleState = useMusicToggle.checked;
	const bgSongValue = bgSong.value;

	const generateAudioUrl = "/generate-voiceover";

	// Construct data to be sent to the server
	const data = {
		script: textareaElem.innerText,
		ttsengine: currentTTS,
		voice: voiceValue,
		useMusic: useMusicToggleState,
		bgSong: bgSongValue
	};

	// Send the actual request to the server
	fetch(generateAudioUrl, {
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
		
			generateAButton.disabled = false;
			generateAButton.classList.remove("hidden");
			cancelAButton.classList.add("hidden");
			//clearInterval(msgInterval);
		})
		.catch((error) => {
			alert("An error occurred. Please try again later.");
			console.log(error);
		});
};

document.addEventListener("DOMContentLoaded", () => {
	msft_voice("en");
	populateScript();
	showSample.addEventListener("click", showHideSample);
	playSample.addEventListener("click", sampleVoice);
	back.addEventListener("click",()=>{window.location.href="/manual.html"})
	forward.addEventListener("click",()=>{window.location.href="/mediasearch.html"})
	mslang.addEventListener("input", () => {
		msft_voice(mslang.value);
	});
	generateAButton.addEventListener("click", generateVideoAudio);
	cancelAButton.addEventListener("click", cancelGeneration);

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
	voiceOptions();
});
