let fullFormula = document.getElementById('formula-input').value;
let remainingFormula = fullFormula;
let poemWords = []; // Array of {word: string, rhythm: string, endOfLine: boolean}
let selectedIdx = 0;

const formulaDisplay = document.getElementById('rem-formula');
const formulaInput = document.getElementById('formula-input');
const updateBtn = document.getElementById('update-formula');
const poemCanvas = document.getElementById('poem-canvas');
const suggestionBox = document.getElementById('word-suggestions');
const romanInput = document.getElementById('roman-input');
const dropdown = document.getElementById('dropdown-menu');
const refreshBtn = document.getElementById('refresh-suggestions');
const backspaceBtn = document.getElementById('backspace-btn');

// --- 1. Settings & Reset Logic ---
updateBtn.onclick = () => {
    fullFormula = formulaInput.value.trim();
    if (!fullFormula) return;
    remainingFormula = fullFormula;
    poemWords = [];
    renderPoem();
    updateSuggestions();
};

// --- 2. Backspace (Undo) Logic ---
backspaceBtn.onclick = () => {
    if (poemWords.length === 0) return;

    const lastEntry = poemWords.pop();
    
    // If we just deleted a line-finishing word, reset formula to its specific rhythm
    if (lastEntry.endOfLine) {
        remainingFormula = lastEntry.rhythm;
    } else {
        remainingFormula = lastEntry.rhythm + remainingFormula;
    }

    renderPoem();
    updateSuggestions();
};

// --- 3. UI Rendering ---
function renderPoem() {
    formulaDisplay.innerText = remainingFormula;
    let canvasText = "";
    
    poemWords.forEach((item) => {
        canvasText += item.word + " ";
        if (item.endOfLine) {
            canvasText += "\n"; // Actual line break
        }
    });
    
    poemCanvas.innerText = canvasText;
}

// --- 4. Transliteration (Direct API) ---
async function fetchTransliteration(text) {
    if (!text) { dropdown.style.display = 'none'; return; }
    const url = `https://inputtools.google.com/request?text=${text}&itc=ne-t-i0-und&num=5&cp=0&cs=1&ie=utf-8&oe=utf-8&app=test`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data[0] === "SUCCESS") {
            showDropdown(data[1][0][1]);
        }
    } catch (e) { console.error("Transliteration Error:", e); }
}

function showDropdown(options) {
    dropdown.innerHTML = '';
    selectedIdx = 0;
    options.forEach((opt, index) => {
        const div = document.createElement('div');
        div.className = 'dropdown-item' + (index === 0 ? ' active' : '');
        div.innerText = opt;
        div.onclick = () => finalizeSelection(opt);
        dropdown.appendChild(div);
    });
    dropdown.style.display = 'block';
}

function finalizeSelection(word) {
    dropdown.style.display = 'none';
    romanInput.value = '';
    selectWord(word);
}

// --- 5. Word Selection & Rhythm Validation ---
async function selectWord(word) {
    const response = await fetch('/get_rhythm', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ word: word })
    });
    const data = await response.json();
    const rhythm = data.rhythm;

    if (remainingFormula.startsWith(rhythm)) {
        remainingFormula = remainingFormula.substring(rhythm.length);
        
        let isEndOfLine = false;
        if (remainingFormula.length === 0) {
            isEndOfLine = true;
            remainingFormula = fullFormula; // Reset formula for next line
        }

        poemWords.push({ word: word, rhythm: rhythm, endOfLine: isEndOfLine });
        
        renderPoem();
        updateSuggestions();
    } else {
        alert(`"${word}" (${rhythm}) does not fit the remaining rhythm "${remainingFormula}"`);
    }
}

// --- 6. Event Listeners ---
romanInput.oninput = (e) => fetchTransliteration(e.target.value.trim());

romanInput.onkeydown = (e) => {
    const items = document.querySelectorAll('.dropdown-item');
    if (dropdown.style.display === 'block' && items.length > 0) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            items[selectedIdx].classList.remove('active');
            selectedIdx = (selectedIdx + 1) % items.length;
            items[selectedIdx].classList.add('active');
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            items[selectedIdx].classList.remove('active');
            selectedIdx = (selectedIdx - 1 + items.length) % items.length;
            items[selectedIdx].classList.add('active');
        } else if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            finalizeSelection(items[selectedIdx].innerText);
        }
    }
};

async function updateSuggestions() {
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ formula: remainingFormula })
        });
        const data = await response.json();
        suggestionBox.innerHTML = '';
        data.suggestions.forEach(word => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.innerText = word;
            btn.onclick = () => selectWord(word);
            suggestionBox.appendChild(btn);
        });
    } catch (e) { console.error("Prediction Error:", e); }
}

refreshBtn.onclick = updateSuggestions;
window.onload = updateSuggestions;