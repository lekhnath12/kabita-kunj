from flask import Flask, request, jsonify, render_template
import json
import random
import os

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

# --- DATA LOADING ---
VOC_PATH = r"C:\Users\lekhp\OneDrive\Desktop\clean_nepali_words.json"
voc = []
prim_voc = {}

if os.path.exists(VOC_PATH):
    with open(VOC_PATH, encoding="utf-8") as f:
        voc = json.load(f)
    for word in voc:
        rhythm = word_to_l_s(word)
        prim_voc.setdefault(rhythm, []).append(word)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    rem = data.get('formula', "")
    target_syl = data.get('syllable_count', 3) 
    suggestions = []
    if len(rem) >= target_syl:
        prefix = rem[:target_syl]
        if prefix in prim_voc:
            suggestions.extend(prim_voc[prefix])
    return jsonify({"suggestions": random.sample(suggestions, min(len(suggestions), 30))})

@app.route('/get_rhymes', methods=['POST'])
def get_rhymes():
    target_word = request.json.get('word', "")
    target_prims = get_word_primitives(target_word)
    target_rhythm = word_to_l_s(target_word) # Get the syllable pattern
    target_syl_count = len(target_rhythm)
    
    rhyme_list = []

    for word in voc:
        if word == target_word: 
            continue
            
        # Optimization: Only process words with the same number of syllables
        # Each char in l/S string represents one syllable
        word_rhythm = word_to_l_s(word)
        if len(word_rhythm) != target_syl_count:
            continue

        word_prims = get_word_primitives(word)
        match_count = 0
        
        # Count matching primitives from the end (phonetic rhyme)
        for p1, p2 in zip(reversed(target_prims), reversed(word_prims)):
            if p1 == p2: 
                match_count += 1
            else: 
                break
        
        if match_count >= 2:
            rhyme_list.append({"word": word, "score": match_count})

    # Sort by the best phonetic match
    rhyme_list.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"rhymes": [r['word'] for r in rhyme_list[:20]]})

@app.route('/get_rhythm', methods=['POST'])
def get_rhythm():
    word = request.json.get('word', "")
    return jsonify({"rhythm": word_to_l_s(word)})

if __name__ == '__main__':
    app.run(debug=True)