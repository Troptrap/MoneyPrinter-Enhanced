fetch('/data.srt')
  .then(response => response.text())
  .then(data => {
    const content = [];
    let i = 0;
    let obj = {};

    // Process the SRT content here (similar logic to your Node.js code)
    const lines = data.split('\n');
    while (i < lines.length - 1) {
      const line = lines[i];
      if (line === '') {
        i += 1;
        content.push(obj);
        obj = {};
      } else if (Number.isInteger(parseInt(line)) && !line.includes('-->')) {
        obj.position = parseInt(line);
        i += 1;
      } else if (line.includes('--')) {
        const parts = line.split('-->');
        const start = parts[0].split(',')[0].trim();
        const timer1 = parts[0].split(',')[1].trim();
        const end = parts[1].split(',')[0].trim();
        const timer2 = parts[1].split(',')[1].replace('\r', '').trim();
        obj.start = start;
        obj.timer1 = timer1;
        obj.end = end;
        obj.timer2 = timer2;
        i += 1;
      } else if (line.match(/[a-z|A-Z]/i)) { // Case-insensitive match for letters
        if (line.includes('<i>')) {
          line = line.replace('<i>', '');
          line = line.replace('</i>', '');
        }
        obj.text = line;
        i += 1;
      }
    }

    // Use the processed content (content) for further manipulation
    console.log(content);  // Example: log the processed content for debugging

    // You can manipulate the subtitles here (e.g., display them)
    const subtitleContainer = document.getElementById('subtitle-container');
    content.forEach(subtitle => {
      const subtitleElement = document.createElement('p');
      subtitleElement.textContent = `${subtitle.start} - ${subtitle.end}: ${subtitle.text}`;
      subtitleContainer.appendChild(subtitleElement);
    });
  })
  .catch(error => {
    console.error('Error fetching SRT file:', error);
  });
