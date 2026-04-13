from flask import Flask, request, jsonify, render_template
import json
import random
import os
from collections import defaultdict

app = Flask(__name__)

# --- RHYTHM & PRIMITIVE LOGIC ---
def get_word_primitives(word):
    matra_to_vowel = {
        'ा': 'आ', 'ि': 'इ', 'ी': 'ई', 'ु': 'उ', 'ू': 'ऊ', 
        'ृ': 'ऋ', 'े': 'ए', 'ै': 'ऐ', 'ो': 'ओ', 'ौ': 'औ',
        'ं': 'अं', 'ः': 'अः'
    }
    primitives = []
    i = 0
    while i < len(word):
        char = word[i]
        next_char = word[i+1] if i+1 < len(word) else None
        if char == 'ँ': 
            i += 1
            continue
        if '\u0915' <= char <= '\u0939' or '\u0958' <= char <= '\u095f':
            if next_char == '्':
                primitives.append(char + '्'); i += 2
            elif next_char in matra_to_vowel:
                primitives.append(char + '्'); primitives.append(matra_to_vowel[next_char]); i += 2
            else:
                primitives.append(char + '्'); primitives.append('अ'); i += 1
        else:
            if char != '्': primitives.append(char)
            i += 1
    return primitives

def word_to_l_s(word):
    primitives = get_word_primitives(word)
    syllables = []
    current_syl = []
    for p in primitives:
        current_syl.append(p)
        if not p.endswith('्'):
            syllables.append(current_syl); current_syl = []
    if current_syl:
        if syllables: syllables[-1].extend(current_syl)
        else: syllables.append(current_syl)

    guru_vowels = {'आ', 'ई', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', 'अं', 'अः'}
    weights = []
    for idx, syl in enumerate(syllables):
        v = next((p for p in syl if not p.endswith('्')), 'अ')
        is_s = v in guru_vowels
        v_idx = syl.index(v) if v in syl else -1
        if not is_s and any(p.endswith('्') for p in syl[v_idx+1:]):
            is_s = True
        if not is_s and idx + 1 < len(syllables):
            next_syl = syllables[idx + 1]
            consonant_count = 0
            for p in next_syl:
                if p.endswith('्'): consonant_count += 1
                else: break
            if consonant_count >= 2: is_s = True
        weights.append("S" if is_s else "l")
    return "".join(weights)

# --- DATA STORAGE & PRECOMPUTATION ---
VOC_PATH = r"C:\Users\lekhp\OneDrive\Desktop\clean_nepali_words.json"
voc_data = []
rhythm_map = defaultdict(list)
rhyme_tail_map = defaultdict(list)
word_info = {}

def precompute_vocabulary():
    """Processes the vocabulary into hash maps for O(1) API response times."""
    global voc_data
    if os.path.exists(VOC_PATH):
        with open(VOC_PATH, encoding="utf-8") as f:
            voc_data = json.load(f)
        
        for word in voc_data:
            prims = get_word_primitives(word)
            rhythm = word_to_l_s(word)
            syl_count = len(rhythm)
            
            word_info[word] = {"rhythm": rhythm, "prims": prims}
            rhythm_map[rhythm].append(word)
            
            if len(prims) >= 2:
                tail = tuple(prims[-2:])
                rhyme_tail_map[(syl_count, tail)].append(word)

# Load data at startup
precompute_vocabulary()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    rem = data.get('formula', "")
    target_syl = int(data.get('syllable_count', 3)) 
    
    if len(rem) < target_syl:
        return jsonify({"suggestions": []})

    prefix = rem[:target_syl]
    suggestions = rhythm_map.get(prefix, [])
    return jsonify({"suggestions": random.sample(suggestions, min(len(suggestions), 30))})

@app.route('/get_rhymes', methods=['POST'])
def get_rhymes():
    target_word = request.json.get('word', "")
    info = word_info.get(target_word)
    
    if not info:
        prims = get_word_primitives(target_word)
        rhythm = word_to_l_s(target_word)
        syl_count = len(rhythm)
    else:
        prims = info['prims']
        syl_count = len(info['rhythm'])

    if len(prims) < 2:
        return jsonify({"rhymes": []})

    tail = tuple(prims[-2:])
    # Only look at words with the same syllable count and ending primitives
    potential_rhymes = rhyme_tail_map.get((syl_count, tail), [])
    
    scored_rhymes = []
    for word in potential_rhymes:
        if word == target_word: continue
        w_prims = word_info[word]['prims']
        match_count = 0
        for p1, p2 in zip(reversed(prims), reversed(w_prims)):
            if p1 == p2: match_count += 1
            else: break
        scored_rhymes.append((word, match_count))

    scored_rhymes.sort(key=lambda x: x[1], reverse=True)
    return jsonify({"rhymes": [r[0] for r in scored_rhymes[:20]]})

@app.route('/get_rhythm', methods=['POST'])
def get_rhythm():
    word = request.json.get('word', "")
    if word in word_info:
        return jsonify({"rhythm": word_info[word]['rhythm']})
    return jsonify({"rhythm": word_to_l_s(word)})

if __name__ == '__main__':
    app.run(debug=True)