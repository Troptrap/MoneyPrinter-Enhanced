document.addEventListener("DOMContentLoaded", () => {
	const closewindow = document.getElementById("closewindow");
	const pexelsvideo = document.getElementById("Pexels-Video");
	const pixabayvideo = document.getElementById("Pixabay-Video");
	const pexels = document.getElementById("Pexels-Photo");
	const pixabay = document.getElementById("Pixabay-Photo");
	const unsplash = document.getElementById("Unsplash-Photo");
	const flickr = document.getElementById("Flickr-Photo");

	const fullImageDialog = document.getElementById("full-image-dialog");
	const closeDialog = document.getElementById("close-dialog");

	function closeFullImage() {
		const fullImage = fullImageDialog.querySelector('img');
		fullImage.remove();
		fullImageDialog.close();
	}
	closeDialog.addEventListener("click", closeFullImage);
	
	function removeUnusedRemote() {
		const remoteCards = document.querySelectorAll(".remote");
		remoteCards.forEach((el) => el.remove());
	}
	function grabMedia() {
		const elem = this;
		const card = this.parentElement;
		const url = elem.dataset.url;
		fetch("/grabmedia", {
			method: "POST",
			headers: {
				Accept: "application/json, text/plain, */*",
				"Content-Type": "application/json"
			},
			body: JSON.stringify({ url: url })
		})
			.then((response) => response.json())
			.then((data) => {
				console.log(data);
				fetch("media/list.json")
					.then((response) => response.json())
					.then((data) => {
						if (!(url in data)) {
							elem.value = "Grab it";
							elem.classList.add(
								"bg-blue-500",
								"hover:bg-blue-700"
							);
						} else {
							elem.value = "Grabbed Already";
							elem.classList.remove(
								"bg-blue-500",
								"hover:bg-blue-700"
							);
							elem.classList.add(
								"bg-black-100",
								"disabled",
								"text-yellow-700"
							);
							card.classList.remove("remote");
							card.classList.add("local");
						}
					});
			});
	}

	function pixabayvid() {
		const term = document.getElementById("find").value;
		const mediaResults = document.getElementById("media-results");
		let url = `/pixabay/video/search/${term}`;

		fetch(url)
			.then((response) => response.json())
			.then((data) => {
				for (const [srcbig, srcsmall] of Object.entries(data)) {
					let card = document.createElement("div");
					card.classList.add(
						"card",
						"border-solid",
						"border-t-8",
						"border-blue-900",
						"justify-center"
					);
					let grab = document.createElement("input");
					grab.type = "submit";
					grab.classList.add(
						"duration-100",
						"linear",
						"text-white",
						"px-1",
						"py-1",
						"w-full",
						"rounded-md"
					);

					fetch("media/list.json")
						.then((response) => response.json())
						.then((data) => {
							if (!(srcbig in data)) {
								grab.value = "Grab it";
								grab.classList.add(
									"bg-blue-500",
									"hover:bg-blue-700"
								);
								card.classList.add("remote");
							} else {
								grab.value = "Grabbed Already";
								grab.classList.add(
									"bg-black-100",
									"disabled",
									"text-yellow-700"
								);
								card.classList.remove("remote");
								card.classList.add("local");
							}
						});
					grab.dataset.url = srcbig;
					grab.addEventListener("click", grabMedia);

					let vidhtml = document.createElement("video");
					let source = document.createElement("source");
					source.src = srcsmall;
					vidhtml.appendChild(source);
					vidhtml.classList.add("flex-col");
					vidhtml.setAttribute("controls", "controls");
					card.appendChild(vidhtml);
					card.appendChild(grab);
					mediaResults.insertAdjacentElement("afterbegin", card);
				}
			});
	}

	function pexelsvid() {
		const term = document.getElementById("find").value;
		const mediaResults = document.getElementById("media-results");
		let url = `/pexels/video/search/${term}`;

		fetch(url)
			.then((response) => response.json())
			.then((data) => {
				for (const [srcbig, srcsmall] of Object.entries(data)) {
					let card = document.createElement("div");
					card.classList.add(
						"card",
						"border-solid",
						"border-t-8",
						"border-blue-900",
						"justify-center"
					);
					let grab = document.createElement("input");
					grab.type = "submit";
					grab.classList.add(
						"duration-100",
						"linear",
						"text-white",
						"px-1",
						"py-1",
						"w-full",
						"rounded-md"
					);

					fetch("media/list.json")
						.then((response) => response.json())
						.then((data) => {
							if (!(srcbig in data)) {
								grab.value = "Grab it";
								grab.classList.add(
									"bg-blue-500",
									"hover:bg-blue-700"
								);
								card.classList.add("remote");
							} else {
								grab.value = "Grabbed Already";
								grab.classList.add(
									"bg-black-100",
									"disabled",
									"text-yellow-700"
								);
								card.classList.remove("remote");
								card.classList.add("local");
							}
						});
					grab.dataset.url = srcbig;
					grab.addEventListener("click", grabMedia);

					let vidhtml = document.createElement("video");
					let source = document.createElement("source");
					source.src = srcsmall;
					vidhtml.appendChild(source);
					vidhtml.classList.add("flex-col");
					vidhtml.setAttribute("controls", "controls");
					card.appendChild(vidhtml);
					card.appendChild(grab);
					mediaResults.insertAdjacentElement("afterbegin", card);
				}
			});
	}


	function getPhotos(photoSource) {
		const term = document.getElementById("find").value;
		const mediaResults = document.getElementById("media-results");
		let url = `/${photoSource}/photo/search/${term}`;

		fetch(url)
			.then((response) => response.json())
			.then((data) => {
				for (const src of data) {
					let card = document.createElement("div");
					card.classList.add(
						"card",
						"border-solid",
						"border-t-8",
						"border-blue-900",
						"justify-center"
					);
					let grab = document.createElement("input");
					grab.type = "submit";
					grab.classList.add(
						"duration-100",
						"linear",
						"text-white",
						"px-1",
						"py-1",
						"w-full",
						"rounded-md"
					);

					fetch("media/list.json")
						.then((response) => response.json())
						.then((data) => {
							if (!(src in data)) {
								grab.value = "Grab it";
								grab.classList.add(
									"bg-blue-500",
									"hover:bg-blue-700"
								);
								card.classList.add("remote");
							} else {
								grab.value = "Grabbed Already";
								grab.classList.add(
									"bg-black-100",
									"disabled",
									"text-yellow-700"
								);
								card.classList.remove("remote");
								card.classList.add("local");
							}
						});
					grab.dataset.url = src;
					grab.addEventListener("click", grabMedia);

					let imghtml = document.createElement("img");
					imghtml.src = src;
					imghtml.classList.add("flex-col");
					let imgfull = document.createElement("img");
					imgfull.src = src;
					card.addEventListener("click", function () {
						fullImageDialog.appendChild(imgfull);
						fullImageDialog.showModal();
					});
					card.appendChild(imghtml);
					card.appendChild(grab);
					mediaResults.insertAdjacentElement("afterbegin", card);
				}
			});
	}

	
	pixabayvideo.addEventListener("click", removeUnusedRemote);
	pixabayvideo.addEventListener("click", pixabayvid);
	pexels.addEventListener("click", removeUnusedRemote);
	pexels.addEventListener("click", () => {
		getPhotos("pexels");
	});
	pixabay.addEventListener("click", removeUnusedRemote);
	pixabay.addEventListener("click", () => {
		getPhotos("pixabay");
	});
	unsplash.addEventListener("click", removeUnusedRemote);
	unsplash.addEventListener("click", () => {
		getPhotos("unsplash");
	});
	flickr.addEventListener("click", removeUnusedRemote);
	flickr.addEventListener("click", () => {
		getPhotos("flickr");
	});
	pexelsvideo.addEventListener("click", removeUnusedRemote);
	pexelsvideo.addEventListener("click", pexelsvid);

	closewindow.addEventListener("click", () => {
		window.close();
	});
});
