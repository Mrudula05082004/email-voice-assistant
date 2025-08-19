// app.js
// Frontend voice assistant UI + backend fetch integration.
// NOTE: This uses the Web Speech API (SpeechRecognition & speechSynthesis).
// Works best in Chrome/Chromium-based browsers.

const btnCheck = document.getElementById('btn-check');
const btnRefresh = document.getElementById('btn-refresh');
const btnSend = document.getElementById('btn-send');
const btnSendVoice = document.getElementById('btn-send-voice');
const emailList = document.getElementById('email-list');

const toInput = document.getElementById('to');
const subjectInput = document.getElementById('subject');
const bodyInput = document.getElementById('body');
const micButtons = document.querySelectorAll('.micro');

const BACKEND = '';// e.g. 'http://127.0.0.1:5000' or leave '' for same origin

// Basic speech utils
function speak(text){
  if (!('speechSynthesis' in window)) return;
  const ut = new SpeechSynthesisUtterance(text);
  ut.lang = 'en-US';
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(ut);
}

// Simple wrapper for SpeechRecognition
function listenOnce(promptText = '') {
  return new Promise((resolve, reject) => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      reject('Speech recognition not supported in this browser.');
      return;
    }
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const sr = new SpeechRec();
    sr.lang = 'en-US';
    sr.interimResults = false;
    sr.maxAlternatives = 1;

    if (promptText) speak(promptText);

    sr.onresult = (e) => {
      const t = e.results[0][0].transcript;
      resolve(t);
    };
    sr.onerror = (e) => reject(e.error || 'speech error');
    sr.onend = () => {
      // if nothing returned, resolve null
      resolve(null);
    };
    sr.start();
  });
}

// fetch recent emails from backend
async function fetchEmails(){
  emailList.innerHTML = `<div class="small">Loading…</div>`;
  try {
    const res = await fetch(`${BACKEND}/check_emails`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json(); // expect array of {from, subject, body}
    renderEmails(data);
  } catch (err) {
    emailList.innerHTML = `<div class="small">Error: ${err.message || err}</div>`;
    speak('Error fetching emails');
    console.error(err);
  }
}

function renderEmails(emails = []){
  if (!emails.length) {
    emailList.innerHTML = `<div class="small">No recent emails found.</div>`;
    return;
  }
  emailList.innerHTML = '';
  emails.forEach((mail, i) => {
    const card = document.createElement('div');
    card.className = 'email-card';
    card.innerHTML = `
      <div class="email-meta">
        <div class="from">${mail.from || 'Unknown'}</div>
        <div class="small">#${i+1}</div>
      </div>
      <div class="email-subject">${mail.subject || '(no subject)'}</div>
      <div class="small">${(mail.body||'').slice(0,150)}${(mail.body||'').length>150 ? '…':''}</div>
      <div class="email-actions" style="margin-top:10px">
        <button class="read">🔊 Read</button>
        <button class="open">Open</button>
        <button class="copy-to">✉️ Reply (copy)</button>
      </div>
    `;
    // actions
    card.querySelector('.read').onclick = () => {
      speak(`From ${mail.from}. Subject ${mail.subject || ''}.`);
      setTimeout(()=> speak(mail.body || 'No content'), 800);
    };
    card.querySelector('.open').onclick = () => {
      alert(`From: ${mail.from}\nSubject: ${mail.subject}\n\n${mail.body}`);
    };
    card.querySelector('.copy-to').onclick = () => {
      toInput.value = extractEmailFromHeader(mail.from) || '';
      subjectInput.value = `Re: ${mail.subject || ''}`;
      bodyInput.value = `\n\n---\nQuoted:\n${mail.body || ''}`;
      speak('Recipient and subject filled for reply. Edit and send.');
    };

    emailList.appendChild(card);
  });
}

function extractEmailFromHeader(header){
  // header like: "Name <email@example.com>"
  if (!header) return '';
  const m = header.match(/<([^>]+)>/);
  if (m) return m[1];
  // if plain email
  const simple = header.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}/);
  return simple ? simple[0] : header;
}

// send email via backend
async function sendEmail(payload){
  try {
    speak('Sending email now.');
    const res = await fetch(`${BACKEND}/send_email`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    speak('Email sent successfully.');
    alert('Sent ✓');
    return data;
  } catch(err){
    speak('Error sending email.');
    alert('Send error: ' + (err.message || err));
  }
}

// UI event bindings
btnCheck.onclick = async () => {
  speak('Checking your recent emails.');
  await fetchEmails();
};

btnRefresh.onclick = () => fetchEmails();

btnSend.onclick = async () => {
  const to = toInput.value.trim();
  const subject = subjectInput.value.trim();
  const body = bodyInput.value.trim();
  if (!to) return alert('Enter recipient email');
  await sendEmail({to,subject,body});
};

// Voice flow: sequential prompts to collect to, subject, body
btnSendVoice.onclick = async () => {
  try {
    const to = await listenOnce('Please say the recipient email address now.');
    if (!to) return speak('No recipient captured. Cancelling.');
    const subject = await listenOnce('Now say the subject.');
    const body = await listenOnce('Now say the email body.');
    // basic normalization: replace " at the rate " -> @ etc. You can improve as needed
    const norm = txt => (txt||'').replace(/\s+at\s+the\s+rate\s+/gi,'@').replace(/\s+dot\s+/gi,'.').replace(/\s+dash\s+/gi,'-').trim();
    toInput.value = norm(to);
    subjectInput.value = subject || '';
    bodyInput.value = body || '';
    await sendEmail({to:toInput.value, subject:subjectInput.value, body:bodyInput.value});
  } catch (err) {
    console.error(err);
    speak('Speech recognition not available or failed.');
  }
};

// per-field mic buttons
micButtons.forEach(btn=>{
  btn.addEventListener('click', async () => {
    const target = btn.dataset.target;
    try {
      const spoken = await listenOnce(`Speak the ${target}`);
      if (!spoken) return;
      const normalized = spoken.replace(/\s+at\s+the\s+rate\s+/gi,'@').replace(/\s+dot\s+/gi,'.').replace(/\s+dash\s+/gi,'-').trim();
      if (target === 'body') document.getElementById(target).value += (document.getElementById(target).value ? '\n' : '') + normalized;
      else document.getElementById(target).value = normalized;
    } catch (err) {
      console.error(err);
      alert('Voice input failed: ' + err);
    }
  });
});

// initial load
fetchEmails();
