let sessionId = null;
const API_BASE = "http://127.0.0.1:5000";

const atm = {
  balance: 250,
  locked: false,
  cardInserted: false,
  pinEntered: '',
  selectedAccount: '',
  state: 'HOME',
  message: 'Insert your card to begin',
};

const el = {
  display: document.getElementById('display'),
  cardButton: document.getElementById('card-button'),
  insertAccount: document.getElementById('account-input'),
  pinPad: document.getElementById('pin-pad'),
  amountInput: document.getElementById('amount-input'),
  withdrawButton: document.getElementById('withdraw-button'),
  balanceButton: document.getElementById('balance-button'),
  resetButton: document.getElementById('reset-button'),
  log: document.getElementById('log'),
  testButton: document.getElementById('test-button'),
  lockoutBadge: document.getElementById('lockout-status'),
};

function updateDisplay() {
  el.display.textContent = atm.message;
  el.lockoutBadge.textContent = atm.locked ? 'LOCKED' : 'READY';
  el.lockoutBadge.className = atm.locked ? 'badge fail' : 'badge pass';
  el.insertAccount.value = atm.cardInserted ? atm.selectedAccount : '';
  el.insertAccount.disabled = atm.cardInserted;
  el.amountInput.disabled = atm.state !== 'MENU' || atm.locked;
  el.withdrawButton.disabled = atm.state !== 'MENU' || atm.locked;
  el.balanceButton.disabled = atm.state !== 'MENU' || atm.locked;
  el.pinPad.querySelectorAll('button').forEach((btn) => {
    btn.disabled = atm.state !== 'PIN_ENTRY' || atm.locked;
  });
  el.resetButton.disabled = false;
}

function logEvent(text) {
  const line = document.createElement('div');
  line.textContent = text;
  el.log.prepend(line);
}

async function insertCard() {
  if (atm.locked) {
    atm.message = 'Account locked. Reset to start.';
    updateDisplay();
    return;
  }
  if (!el.insertAccount.value.trim()) {
    atm.message = 'Enter your account number first.';
    updateDisplay();
    return;
  }

  atm.cardInserted = true;
  atm.selectedAccount = el.insertAccount.value.trim();
  atm.message = 'Card inserted. Verifying account...';
  updateDisplay();

  // Call backend to insert card
  try {
    const resp = await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: { type: 'insert_card', account: atm.selectedAccount },
      }),
    });
    const result = await resp.json();
    if (resp.ok) {
      atm.balance = result.balance;
      atm.locked = result.locked;
      atm.state = 'PIN_ENTRY';
      atm.message = 'Card verified. Enter your PIN.';
      logEvent('[INFO] Card inserted and verified.');
    } else {
      atm.message = 'Invalid account number.';
      logEvent('[ERROR] Invalid account number.');
      atm.cardInserted = false;
      atm.selectedAccount = '';
    }
  } catch (err) {
    atm.message = 'Error communicating with server.';
    logEvent(`[ERROR] ${err.message}`);
    atm.cardInserted = false;
  }
  updateDisplay();
}

async function enterPin(digit) {
  if (atm.state !== 'PIN_ENTRY' || atm.locked) return;
  if (atm.pinEntered.length >= 4) return;

  atm.pinEntered += digit;
  const obfuscated = '*'.repeat(atm.pinEntered.length);
  atm.message = `PIN entered: ${obfuscated}`;
  updateDisplay();

  if (atm.pinEntered.length === 4) {
    // Call backend to validate PIN
    try {
      const resp = await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: { type: 'enter_pin', pin: parseInt(atm.pinEntered) },
        }),
      });
      const result = await resp.json();
      if (resp.ok) {
        if (result.state === 'MENU') {
          atm.state = 'MENU';
          atm.pinEntered = '';
          atm.message = 'PIN accepted. Choose a transaction.';
          logEvent('[INFO] Authenticated successfully.');
        } else if (result.state === 'PIN_ERROR') {
          atm.pinEntered = '';
          atm.message = 'Invalid PIN. Card ejected.';
          logEvent('[WARN] Invalid PIN attempt.');
          atm.cardInserted = false;
          atm.state = 'HOME';
        } else if (result.state === 'LOCKED') {
          atm.locked = true;
          atm.state = 'LOCKED';
          atm.pinEntered = '';
          atm.message = 'Too many failed attempts. Account locked.';
          logEvent('[FAIL] Account locked after 3 failed PIN attempts.');
          atm.cardInserted = false;
        }
        atm.balance = result.balance;
      } else {
        atm.message = 'Error validating PIN.';
        logEvent(`[ERROR] ${result.error}`);
      }
    } catch (err) {
      atm.message = 'Server error.';
      logEvent(`[ERROR] ${err.message}`);
    }
    updateDisplay();
  }
}

async function withdraw() {
  if (atm.state !== 'MENU' || atm.locked) return;
  const amount = Number(el.amountInput.value);
  if (!amount || amount % 10 !== 0) {
    atm.message = 'Enter a valid withdrawal amount (multiples of 10).';
    updateDisplay();
    return;
  }
  if (amount > 100) {
    atm.message = 'Maximum withdrawal is $100.';
    updateDisplay();
    return;
  }

  atm.message = `Requesting withdrawal of $${amount}...`;
  updateDisplay();

  try {
    const resp = await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: { type: 'withdraw', amount: amount },
      }),
    });
    const result = await resp.json();
    if (resp.ok) {
      atm.balance = result.balance;
      if (result.dispense > 0) {
        atm.message = `Dispensed $${result.dispense}. New balance: $${atm.balance}.`;
        logEvent(`[PASS] Withdrew $${result.dispense}. Balance: $${atm.balance}`);
      } else {
        atm.message = 'Withdrawal denied. Insufficient funds or invalid amount.';
        logEvent('[FAIL] Withdrawal denied.');
      }
    } else {
      atm.message = 'Withdrawal error. Returning to menu.';
      logEvent(`[ERROR] ${result.error}`);
    }
  } catch (err) {
    atm.message = 'Server error.';
    logEvent(`[ERROR] ${err.message}`);
  }
  el.amountInput.value = '';
  updateDisplay();
}

async function showBalance() {
  if (atm.state !== 'MENU' || atm.locked) return;

  atm.message = 'Checking balance...';
  updateDisplay();

  try {
    const resp = await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: { type: 'select_balance' },
      }),
    });
    const result = await resp.json();
    if (resp.ok) {
      atm.balance = result.balance;
      atm.message = `Available balance: $${atm.balance}.`;
      logEvent(`[PASS] Balance inquiry: $${atm.balance}`);
    } else {
      atm.message = 'Error checking balance.';
      logEvent(`[ERROR] ${result.error}`);
    }
  } catch (err) {
    atm.message = 'Server error.';
    logEvent(`[ERROR] ${err.message}`);
  }
  updateDisplay();
}

async function resetAtm() {
  try {
    await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: { type: 'reset' },
      }),
    });
  } catch (err) {
    logEvent(`[WARN] Reset error: ${err.message}`);
  }

  atm.cardInserted = false;
  atm.pinEntered = '';
  atm.selectedAccount = '';
  atm.state = 'HOME';
  atm.message = 'ATM reset. Insert card to begin.';
  atm.locked = false;
  atm.balance = 250;
  el.insertAccount.value = '';
  el.amountInput.value = '';
  logEvent('[INFO] ATM reset.');
  updateDisplay();
}

async function runDemoTests() {
  logEvent('Running demo scenario...');
  const demoActions = [
    { type: 'insert_card', account: '1234' },
    { type: 'enter_pin', pin: 9 },
    { type: 'select_balance' },
  ];

  let demoPass = 0;
  for (const action of demoActions) {
    try {
      const resp = await fetch(`${API_BASE}/api/session/${sessionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const result = await resp.json();
      if (resp.ok) {
        logEvent(`[PASS] ${action.type} executed successfully.`);
        demoPass++;
      } else {
        logEvent(`[FAIL] ${action.type} failed: ${result.error}`);
      }
    } catch (err) {
      logEvent(`[ERROR] Demo error: ${err.message}`);
    }
  }
  logEvent(`Demo complete: ${demoPass}/${demoActions.length} passed.`);
  atm.message = 'Demo test completed. Check log.';
  updateDisplay();
}

async function init() {
  // Start a new session with backend
  try {
    const resp = await fetch(`${API_BASE}/api/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await resp.json();
    sessionId = result.session_id;
    logEvent(`[INFO] Session started: ${sessionId}`);
  } catch (err) {
    logEvent(`[ERROR] Failed to start session: ${err.message}`);
    atm.message = 'Failed to connect to server.';
    updateDisplay();
    return;
  }

  // Attach event listeners
  el.cardButton.addEventListener('click', insertCard);
  el.pinPad.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON' && !e.target.disabled) {
      enterPin(e.target.textContent);
    }
  });
  el.withdrawButton.addEventListener('click', withdraw);
  el.balanceButton.addEventListener('click', showBalance);
  el.resetButton.addEventListener('click', resetAtm);
  el.testButton.addEventListener('click', runDemoTests);
  
  updateDisplay();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
