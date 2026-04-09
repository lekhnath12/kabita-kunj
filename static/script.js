let fullFormula = "lSSlSSlSSlSS";
let remainingFormula = fullFormula;
let lineCount = 0;
let selectedIdx = 0;

const formulaDisplay = document.getElementById('rem-formula');
const poemCanvas = document.getElementById('poem-canvas');
const suggestionBox = document.getElementById('word-suggestions');
const romanInput = document.getElementById('roman-input');
const dropdown = document.getElementById('dropdown-menu');

// --- 1. Fetch Transliteration Options ---
async function fetchTransliteration(text) {
    if (!text) { dropdown.style.display = 'none'; return; }
    
    // num=5 gives us multiple choices
    const url = `https://inputtools.google.com/request?text=${text}&itc=ne-t-i0-und&num=5&cp=0&cs=1&ie=utf-8&oe=utf-8&app=test`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data[0] === "SUCCESS") {
            showDropdown(data[1][0][1]);
        }
    } catch (e) {
        console.error("API Error", e);
    }
}

// --- 2. Dropdown UI Logic ---
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
    selectWord(word); // Existing function to add to poem
}

// --- 3. Keyboard Navigation ---
romanInput.addEventListener('keydown', (e) => {
    const items = document.querySelectorAll('.dropdown-item');
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        items[selectedIdx].classList.remove('active');
        selectedIdx = (selectedIdx + 1) % items.length;
        items[selectedIdx].classList.add('active');
    } 
    else if (e.key === 'ArrowUp') {
        e.preventDefault();
        items[selectedIdx].classList.remove('active');
        selectedIdx = (selectedIdx - 1 + items.length) % items.length;
        items[selectedIdx].classList.add('active');
    }
    else if (e.key === 'Enter' || (e.key === ' ' && dropdown.style.display === 'block')) {
        e.preventDefault();
        if (items[selectedIdx]) {
            finalizeSelection(items[selectedIdx].innerText);
        }
    }
});

// Fetch options as you type
romanInput.addEventListener('input', (e) => {
    fetchTransliteration(e.target.value.trim());
});

// --- 4. Existing Poem Logic (Keep your previous logic here) ---
async function selectWord(word) {
    const response = await fetch('/get_rhythm', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ word: word })
    });
    const data = await response.json();
    const rhythm = data.rhythm;

    if (remainingFormula.startsWith(rhythm)) {
        poemCanvas.innerText += word + " ";
        remainingFormula = remainingFormula.substring(rhythm.length);
        if (remainingFormula.length === 0) {
            lineCount++;
            poemCanvas.innerText += (lineCount % 4 === 0) ? "\n\n" : "\n";
            remainingFormula = fullFormula;
        }
        formulaDisplay.innerText = remainingFormula;
        updateSuggestions();
    } else {
        alert(`"${word}" (${rhythm}) doesn't fit!`);
    }
}

async function updateSuggestions() {
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
}

// Initialize
updateSuggestions();