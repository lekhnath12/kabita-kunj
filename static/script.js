let fullFormula = document.getElementById('formula-input').value;
let remainingFormula = fullFormula;
let poemWords = []; 

const formulaDisplay = document.getElementById('rem-formula');
const formulaInput = document.getElementById('formula-input');
const updateBtn = document.getElementById('update-formula');
const poemCanvas = document.getElementById('poem-canvas');
const suggestionBox = document.getElementById('word-suggestions');
const rhymeBox = document.getElementById('rhyme-suggestions');
const romanInput = document.getElementById('roman-input');
const dropdown = document.getElementById('dropdown-menu');
const sylSlider = document.getElementById('syl-slider');
const sylValDisplay = document.getElementById('syl-val');

// --- 1. Settings & Reset ---
updateBtn.onclick = () => {
    fullFormula = formulaInput.value.trim();
    remainingFormula = fullFormula;
    poemWords = [];
    renderPoem();
    updateSuggestions();
};

sylSlider.oninput = () => {
    sylValDisplay.innerText = sylSlider.value;
    updateSuggestions(); 
};

// --- 2. Backspace & Shuffle ---
document.getElementById('backspace-btn').onclick = () => {
    if (poemWords.length === 0) return;
    const lastEntry = poemWords.pop();
    if (lastEntry.endOfLine) {
        remainingFormula = lastEntry.rhythm;
    } else {
        remainingFormula = lastEntry.rhythm + remainingFormula;
    }
    renderPoem();
    updateSuggestions();
};

document.getElementById('refresh-suggestions').onclick = updateSuggestions;

// --- 3. Poem Rendering ---
function renderPoem() {
    formulaDisplay.innerText = remainingFormula;
    let canvasText = "";
    poemWords.forEach((item) => {
        canvasText += item.word + " ";
        if (item.endOfLine) canvasText += "\n";
    });
    poemCanvas.innerText = canvasText;
}

// --- 4. Word Selection & API ---
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
        let isEndOfLine = remainingFormula.length === 0;
        if (isEndOfLine) remainingFormula = fullFormula; 
        
        poemWords.push({ word: word, rhythm: rhythm, endOfLine: isEndOfLine });
        renderPoem();
        updateSuggestions();
        fetchRhymes(word); 
    } else {
        alert(`"${word}" (${rhythm}) does not fit the pattern "${remainingFormula}"`);
    }
}

async function fetchRhymes(word) {
    const response = await fetch('/get_rhymes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ word: word })
    });
    const data = await response.json();
    rhymeBox.innerHTML = '';
    
    if (data.rhymes.length === 0) {
        rhymeBox.innerHTML = '<p style="color:gray; font-size:0.8em;">No matches found.</p>';
        return;
    }

    data.rhymes.forEach(rw => {
        const btn = document.createElement('button');
        btn.className = 'rhyme-btn';
        btn.innerText = rw;
        btn.onclick = () => selectWord(rw);
        rhymeBox.appendChild(btn);
    });
}

async function updateSuggestions() {
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            formula: remainingFormula,
            syllable_count: parseInt(sylSlider.value)
        })
    });
    const data = await response.json();
    suggestionBox.innerHTML = '';
    data.suggestions.forEach(w => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-btn';
        btn.innerText = w;
        btn.onclick = () => selectWord(w);
        suggestionBox.appendChild(btn);
    });
}

// --- 5. Transliteration ---
romanInput.oninput = async (e) => {
    const text = e.target.value.trim();
    if (!text) { dropdown.style.display = 'none'; return; }
    
    const url = `https://inputtools.google.com/request?text=${text}&itc=ne-t-i0-und&num=5&cp=0&cs=1&ie=utf-8&oe=utf-8&app=test`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data[0] === "SUCCESS") {
            const options = data[1][0][1];
            dropdown.innerHTML = '';
            options.forEach(opt => {
                const div = document.createElement('div');
                div.className = 'dropdown-item';
                div.innerText = opt;
                div.onclick = () => {
                    dropdown.style.display = 'none';
                    romanInput.value = '';
                    selectWord(opt);
                };
                dropdown.appendChild(div);
            });
            dropdown.style.display = 'block';
        }
    } catch (err) { console.error(err); }
};

window.onload = updateSuggestions;