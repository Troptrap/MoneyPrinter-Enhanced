const videoExt = [
	"m1v",
	"mpeg",
	"mov",
	"qt",
	"mpa",
	"mpg",
	"mpe",
	"avi",
	"movie",
	"mp4",
	"m4v"
];

const imageExt = [
	"ras",
	"xwd",
	"bmp",
	"jpe",
	"jpg",
	"jpeg",
	"xpm",
	"ief",
	"pbm",
	"tif",
	"gif",
	"ppm",
	"xbm",
	"tiff",
	"rgb",
	"pgm",
	"png",
	"pnm"
];
const fixedDuration = 20;
let mediaCount = 0;

const getFileExtension = (filename) => filename.split(".").pop();
function isVideoOrImage(localSrc) {
	const extension = getFileExtension(localSrc);

	if (videoExt.includes(extension)) {
		return "video";
	} else if (imageExt.includes(extension)) {
		return "image";
	} else {
		return "unknown"; // Handle cases where the extension is not recognized
	}
}

let usedMedia = [];

function populateMediaFromList(i) {
	const el = document.getElementById(i);
	const paragraphDuration =
		parseInt(el.dataset.end) - parseInt(el.dataset.start);
	console.log("Paragraph: " + paragraphDuration);
	let totalMediaDuration = 0;
	fetch("../media/list.json")
		.then((response) => response.json())
		.then((data) => {
			for (const remoteSrc of Object.keys(data)) {
				const localSrc = data[remoteSrc];
				if (totalMediaDuration > paragraphDuration) {
					continue;
				}

				if (!usedMedia.includes(localSrc)) {
					const mediaType = isVideoOrImage(localSrc);
					if (mediaType == "image") {
						let card = document.createElement("div");
						card.classList.add(
							"card",
							"border-solid",
							"border-t-8",
							"border-blue-900"
						);
						card.id = "card" + mediaCount;
						card.dataset.duration =
							parseFloat(fixedDuration) * 1000;
						totalMediaDuration += parseFloat(fixedDuration) * 1000;
						let imghtml = document.createElement("img");
						imghtml.src = "../media/" + localSrc;
						imghtml.src = "../media/" + localSrc;
						//imghtml.classList.add("flex-col");
						let imgfull = document.createElement("img");
						imgfull.src = "../media/" + localSrc;
						card.appendChild(imghtml);
						el.appendChild(card);
					}
					if (mediaType == "video") {
						let card = document.createElement("div");
						card.classList.add(
							"card",
							"border-solid",
							"border-t-8",
							"border-blue-900"
						);
						card.id = "card" + mediaCount;
						let vidhtml = document.createElement("video");
						let source = document.createElement("source");
						source.src = "../media/" + localSrc;
						vidhtml.appendChild(source);
						//vidhtml.classList.add("flex-col");
						vidhtml.setAttribute("controls", "controls");
						vidhtml.setAttribute("preload", "metadata");
						/*vidhtml.setAttribute("poster", videodata[vid]["thumb"]);*/

						vidhtml.addEventListener("loadedmetadata", () => {
							console.log(
								localSrc + " duration: " + vidhtml.duration
							);
							card.dataset.duration =
								parseFloat(vidhtml.duration) * 1000;
							totalMediaDuration +=
								parseFloat(vidhtml.duration) * 1000;
						});
						card.appendChild(vidhtml);
						el.appendChild(card);
					}
					usedMedia.push(localSrc);
					mediaCount += 1;
					console.log("totalMediaDuration: " + totalMediaDuration);
				}
			}
		});
}

function getSubs() {
	return fetch("/script.srt")
		.then((response) => response.text())
		.then((data) => {
			const content = [];
			let i = 0;
			let obj = {};

			// Process the SRT content here (similar logic to your Node.js code)
			const lines = data.split("\n");
			while (i < lines.length - 1) {
				const line = lines[i];
				if (line === "") {
					i += 1;
					content.push(obj);
					obj = {};
				} else if (
					Number.isInteger(parseInt(line)) &&
					!line.includes("-->")
				) {
					obj.position = parseInt(line);
					i += 1;
				} else if (line.includes("--")) {
					const parts = line.split("-->");
					const start = parts[0].split(",")[0].trim();
					const timer1 = parts[0].split(",")[1].trim();
					const end = parts[1].split(",")[0].trim();
					const timer2 = parts[1]
						.split(",")[1]
						.replace("\r", "")
						.trim();
					obj.start = start;
					obj.timer1 = timer1;
					obj.end = end;
					obj.timer2 = timer2;
					i += 1;
				} else if (line.match(/[a-z|A-Z]/i)) {
					// Case-insensitive match for letters
					if (line.includes("<i>")) {
						line = line.replace("<i>", "");
						line = line.replace("</i>", "");
					}
					obj.text = line;
					i += 1;
				}
			}

			// Use the processed content (content) for further manipulation
			//	console.log(content);
			return content;
		})
		.catch((error) => {
			console.error("Error fetching SRT file:", error);
		});
}

function getScript() {
	return fetch("script.json")
		.then((response) => response.json())
		.then((data) => {
			//console.log(JSON.stringify(data));
			return data;
		});
}
function insertParagraphs() {
	fetch("../temp/script.json")
		.then((response) => response.json())
		.then((data) => {
			console.log(JSON.stringify(data));
			for (let part of Object.keys(data)) {
				const partDiv = document.createElement("div");
				const mediaDiv = document.createElement("div");
				partDiv.id = "part" + part;
				partDiv.classList.add("flex", "flex-col", "part");
				mediaDiv.id = "media" + part;
				mediaDiv.classList.add("media");
				const paragraphPart = document.createElement("p");
				paragraphPart.innerHTML = data[part].text;
				paragraphPart.classList.add("border-2", "border-indigo-700","text");
				mediaDiv.dataset.start = data[part].start;
				mediaDiv.dataset.end = data[part].end;
				partDiv.appendChild(paragraphPart);
				partDiv.appendChild(mediaDiv);
				document.body.appendChild(partDiv);
				populateMediaFromList(mediaDiv.id);
			}
		});
}

// Helper function to convert time string to milliseconds
function convertTimeToMilliseconds(srtTime) {
	// Split the SRT time into components
	const [hours, minutes, secondsAndMilliseconds] = srtTime.split(":");

	// Extract seconds and milliseconds
	const [seconds, milliseconds] = secondsAndMilliseconds.split(",");

	// Convert each part to a number and calculate total milliseconds
	const totalMilliseconds =
		parseFloat(hours) * 3600 * 1000 +
		parseFloat(minutes) * 60 * 1000 +
		parseFloat(seconds) * 1000 +
		parseFloat(milliseconds);

	return totalMilliseconds;
}

//document.addEventListener("DOMContentLoaded", populateMediaFromList);
document.addEventListener("DOMContentLoaded", () => {
	insertParagraphs();
});
//document.addEventListener("DOMContentLoaded", getScript);
