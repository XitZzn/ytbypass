const storageArea = (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync) 
  ? chrome.storage.sync 
  : (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local ? chrome.storage.local : null);

const DEFAULTS = {
  enabled: true,
  rate: 1,
  autoIncrease: true,
  library: '',
  startDate: new Date().toISOString(),
  lastResetDate: new Date().toISOString(),
};

const enabledEl = document.getElementById('enabled');
const rateEl = document.getElementById('rate');
const rateValueEl = document.getElementById('rateValue');
const autoIncreaseEl = document.getElementById('autoIncrease');
const libraryEl = document.getElementById('library');
const urlStatusEl = document.getElementById('urlStatus');
const saveBtn = document.getElementById('saveBtn');
const resetBtn = document.getElementById('resetBtn');

rateEl.addEventListener('input', () => {
  rateValueEl.textContent = rateEl.value + '%';
});

function load() {
  if (!storageArea) return;
  storageArea.get(DEFAULTS, (items) => {
    enabledEl.checked = items.enabled !== false;
    rateEl.value = (typeof items.rate === 'number') ? items.rate : 1;
    rateValueEl.textContent = rateEl.value + '%';
    autoIncreaseEl.checked = items.autoIncrease !== false;
    libraryEl.value = items.library || '';
  });
}

function save() {
  if (!storageArea) {
    urlStatusEl.textContent = 'Erro: chrome.storage não está disponível.';
    urlStatusEl.className = 'status err';
    return;
  }

  const libText = libraryEl.value.trim();
  let urls = [];
  if (libText) {
    urls = libText.split(',').map(u => u.trim()).filter(Boolean);
  }

  storageArea.get(['startDate'], (existing) => {
    const startDate = existing.startDate || new Date().toISOString();
    const data = {
      enabled: enabledEl.checked,
      rate: parseInt(rateEl.value, 10) || 1,
      autoIncrease: autoIncreaseEl.checked,
      library: urls.join(','),
      startDate: startDate,
      lastResetDate: new Date().toISOString(),
    };

    storageArea.set(data, () => {
      urlStatusEl.textContent = 'Configurações salvas! Taxa inicial de ' + data.rate + '% (aumentando 1% ao dia).';
      urlStatusEl.className = 'status ok';
      setTimeout(() => { urlStatusEl.textContent = ''; }, 3500);
    });
  });
}

function resetDefaults() {
  if (!storageArea) return;
  storageArea.set(DEFAULTS, () => {
    load();
    urlStatusEl.textContent = 'Padrões restaurados (1% + 1% ao dia).';
    urlStatusEl.className = 'status ok';
    setTimeout(() => { urlStatusEl.textContent = ''; }, 2500);
  });
}

saveBtn.addEventListener('click', save);
resetBtn.addEventListener('click', resetDefaults);

document.addEventListener('DOMContentLoaded', load);
