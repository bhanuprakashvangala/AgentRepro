const fileList = document.getElementById('file-list');
const preview = document.getElementById('preview');
const statusDot = document.getElementById('sse-dot');
const statusLabel = document.getElementById('sse-status');

let currentFile = null;

async function loadFileList() {
  const response = await fetch('/api/files');
  const { files } = await response.json();
  fileList.innerHTML = '';
  files.forEach((file) => {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.textContent = file;
    button.addEventListener('click', () => renderMarkdown(file));
    li.appendChild(button);
    fileList.appendChild(li);
  });
  if (!currentFile && files.length > 0) {
    renderMarkdown(files[0]);
  }
  updateActiveButton();
}

async function renderMarkdown(file) {
  currentFile = file;
  const response = await fetch(`/api/render?file=${encodeURIComponent(file)}`);
  const data = await response.json();
  if (data.error) {
    preview.innerHTML = `<p class="error">${data.error}</p>`;
    return;
  }
  preview.innerHTML = data.html;
  updateActiveButton();
}

function updateActiveButton() {
  const buttons = fileList.querySelectorAll('button');
  buttons.forEach((btn) => {
    if (btn.textContent === currentFile) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

function setupEventSource() {
  const source = new EventSource('/events');
  source.addEventListener('open', () => {
    statusDot.classList.remove('offline');
    statusLabel.textContent = 'Connected';
  });
  source.addEventListener('error', () => {
    statusDot.classList.add('offline');
    statusLabel.textContent = 'Reconnecting…';
  });
  source.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data);
    if (!currentFile || payload.file === currentFile) {
      renderMarkdown(currentFile || payload.file);
    }
    loadFileList();
  });
}

loadFileList();
setupEventSource();
