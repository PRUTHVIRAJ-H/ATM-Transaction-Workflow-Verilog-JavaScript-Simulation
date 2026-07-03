const fileInput = document.getElementById('vcd-file');
const status = document.getElementById('status');
const waveform = document.getElementById('waveform');

async function renderVcd(text, label) {
  const lines = text.split(/\r?\n/);
  const signals = [];
  const changes = [];

  for (const line of lines) {
    if (line.startsWith('$var')) {
      const parts = line.trim().split(/\s+/);
      if (parts.length >= 4) {
        const id = parts[3];
        const name = parts[4] || '';
        signals.push({ id, name });
      }
    }
    if (line.startsWith('#')) {
      changes.push(line);
    }
  }

  const rows = signals.slice(0, 12).map((sig) => {
    return `<div class="row"><strong>${sig.name}</strong><div class="bar"></div><div class="tiny">${sig.id}</div></div>`;
  }).join('');

  waveform.innerHTML = `<div class="card"><div class="label">Loaded signals</div><div class="list">${rows}</div></div>`;
  status.textContent = `Loaded ${signals.length} signals from ${label}`;
}

async function loadDefaultVcd() {
  try {
    const response = await fetch('./atm_waves.vcd');
    if (!response.ok) throw new Error('not found');
    const text = await response.text();
    await renderVcd(text, 'sim/atm_waves.vcd');
  } catch (err) {
    status.textContent = 'No local VCD found yet; upload a .vcd file to preview it.';
  }
}

if (fileInput) {
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    status.textContent = 'Loading VCD...';
    const text = await file.text();
    await renderVcd(text, file.name);
  });
}

loadDefaultVcd();
