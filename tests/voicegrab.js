function msft_voice(loc) {
	fetch("microsoft_voices.json").then((response) => {
		response.json().then((data) => {
			const locales = Object.keys(data);
			for (let locale of locales) {
				if (locale.startsWith(loc)) {
					data[locale].forEach((v) => {
						console.log(Object.values(v)[0]);
						console.log(Object.keys(v)[0]);
						const microsoftvoice =
							document.getElementById("microsoftvoice");
						let option = document.createElement("option");
						option.text = Object.values(v)[0];
						option.value = Object.keys(v)[0];
						microsoftvoice.appendChild(option);
					});
				}
			}
		});
	});
}

function langcode() {
	const langlist = document.getElementById("lang-list");
	fetch("microsoft_voices.json").then((response) => {
		response.json().then((data) => {
			const locales = Object.keys(data);
			for (let locale of locales) {
				let option = document.createElement("option");
				option.text = locale;
				langlist.appendChild(option);
			}
		});
	});
}

document.addEventListener("DOMContentLoaded", () => {
	
	const mslang = document.getElementById("mslang");
	const microsoftvoice = document.getElementById("microsoftvoice");
	mslang.addEventListener("change", () => {
		microsoftvoice.options.length = 0;
		msft_voice(mslang.value, microsoftvoice);
		
	});
	langcode();
});
