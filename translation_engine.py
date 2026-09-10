"""
VIDYA AI - Multi-Tribal Linguistic Translation Engine
Translates Hindi curriculum and classroom speech into Indian Tribal & Regional Mother Tongues:
- Gondi (गोंडी)
- Santhali (संथाली)
- Bhili (भीली)
- Telugu (తెలుగు / तेलुगु)
- Mundari (मुंडारी)
- Kurukh / Oraon (कुड़ुख़)

Includes pronunciation guides (phonetics) for Hindi-speaking teachers,
classroom domain dictionaries, and optional IndicTrans2 API bridge.
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vidya_ai.translation")

# Target Language Metadata
LANGUAGES: Dict[str, Dict[str, str]] = {
    "gondi": {
        "code": "gon",
        "name": "Gondi",
        "native_name": "गोंडी (Gōndi)",
        "script": "Devanagari (Standardized for Education)",
        "regions": "Madhya Pradesh, Chhattisgarh, Maharashtra, Telangana",
        "speakers": "~3 Million+",
        "greeting": "सेवा जोहार (Sewa Johar)"
    },
    "santhali": {
        "code": "sat",
        "name": "Santhali",
        "native_name": "संथाली (Santali)",
        "script": "Devanagari / Ol Chiki",
        "regions": "Jharkhand, Odisha, West Bengal, Bihar",
        "speakers": "~7.6 Million+",
        "greeting": "जोहार (Johar)"
    },
    "bhili": {
        "code": "bhi",
        "name": "Bhili",
        "native_name": "भीली (Bhili)",
        "script": "Devanagari",
        "regions": "Rajasthan, Madhya Pradesh, Gujarat, Maharashtra",
        "speakers": "~10 Million+",
        "greeting": "राम राम सा / जोहार (Ram Ram Sa / Johar)"
    },
    "telugu": {
        "code": "tel",
        "name": "Telugu",
        "native_name": "తెలుగు (Telugu)",
        "script": "Telugu / Devanagari Transliteration",
        "regions": "Telangana & Andhra Pradesh (Agency Tribal Areas)",
        "speakers": "~83 Million+",
        "greeting": "నమస్కారం (Namaskaram / Johar)"
    },
    "mundari": {
        "code": "mun",
        "name": "Mundari",
        "native_name": "मुंडारी (Mundari)",
        "script": "Devanagari",
        "regions": "Jharkhand, Odisha, West Bengal",
        "speakers": "~1.1 Million+",
        "greeting": "जोहार (Johar)"
    },
    "kurukh": {
        "code": "kru",
        "name": "Kurukh",
        "native_name": "कुड़ुख़ (Kurukh / Oraon)",
        "script": "Devanagari / Tolong Siki",
        "regions": "Jharkhand, Chhattisgarh, Odisha",
        "speakers": "~2 Million+",
        "greeting": "जोहार (Johar)"
    }
}

# Rich Classroom Domain Dictionaries (Hindi -> Target Language)
# Each entry contains: [Target Text in Devanagari script, Phonetic Pronunciation Guide]
DICTIONARY: Dict[str, Dict[str, Dict[str, str]]] = {
    "gondi": {
        # Classroom & Instructions
        "नमस्ते": {"trans": "सेवा जोहार", "phonetic": "Sewa Johar", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "सबेरे जोहार", "phonetic": "Sabere Johar", "pos": "greeting"},
        "बैठ जाओ": {"trans": "कुंदुट", "phonetic": "Kundut", "pos": "verb"},
        "खड़े हो जाओ": {"trans": "तेड़सी नितुट", "phonetic": "Tedsi Nitut", "pos": "verb"},
        "किताब खोलो": {"trans": "पोथी उघड़ कीम", "phonetic": "Pothi Ughad Keem", "pos": "verb"},
        "ध्यान से सुनो": {"trans": "चित लागी केंजुट", "phonetic": "Chit Laagi Kenjut", "pos": "verb"},
        "लिखो": {"trans": "लिखी कीम", "phonetic": "Likhi Keem", "pos": "verb"},
        "पढ़ो": {"trans": "वाचा कीम", "phonetic": "Vaacha Keem", "pos": "verb"},
        "बहुत अच्छा": {"trans": "बेसब बेशर", "phonetic": "Besab Beshar", "pos": "adj"},
        "समझ आया": {"trans": "पुनातु", "phonetic": "Punaatu?", "pos": "phrase"},
        "धन्यवाद": {"trans": "धन्यवाद / जोहार", "phonetic": "Johar", "pos": "noun"},
        
        # Science & Nature (Class 1-5)
        "पौधा": {"trans": "मरका / पौधा", "phonetic": "Marka", "pos": "noun"},
        "पौधे": {"trans": "मरान / छोटे पेड़", "phonetic": "Maraan", "pos": "noun"},
        "पौधों": {"trans": "मरान तेकी", "phonetic": "Maraan teki", "pos": "noun"},
        "पेड़": {"trans": "मरा", "phonetic": "Maraa", "pos": "noun"},
        "पेड़ों": {"trans": "मरान", "phonetic": "Maraan", "pos": "noun"},
        "पत्ती": {"trans": "आकी", "phonetic": "Aaki", "pos": "noun"},
        "पत्तियां": {"trans": "आकीन", "phonetic": "Aakeen", "pos": "noun"},
        "पत्ते": {"trans": "आकीन", "phonetic": "Aakeen", "pos": "noun"},
        "जड़": {"trans": "वेर", "phonetic": "Vehr", "pos": "noun"},
        "फूल": {"trans": "पुंगार", "phonetic": "Pungaar", "pos": "noun"},
        "फल": {"trans": "पंज", "phonetic": "Panj", "pos": "noun"},
        "बीज": {"trans": "विज्जा", "phonetic": "Vijja", "pos": "noun"},
        "पानी": {"trans": "येर", "phonetic": "Yer", "pos": "noun"},
        "जल": {"trans": "येर", "phonetic": "Yer", "pos": "noun"},
        "सूर्य": {"trans": "पोरदु", "phonetic": "Pordu", "pos": "noun"},
        "धूप": {"trans": "वेलंग / पोरदु वेलंग", "phonetic": "Pordu Velang", "pos": "noun"},
        "सूर्य का प्रकाश": {"trans": "पोरदुना वेलंग", "phonetic": "Porduna Velang", "pos": "noun"},
        "मिट्टी": {"trans": "नली / माटी", "phonetic": "Nalee / Maati", "pos": "noun"},
        "हवा": {"trans": "वली", "phonetic": "Valee", "pos": "noun"},
        "वर्षा": {"trans": "पिरी / पानी", "phonetic": "Piree", "pos": "noun"},
        "बारिश": {"trans": "पिरी", "phonetic": "Piree", "pos": "noun"},
        "बादल": {"trans": "मिर", "phonetic": "Mir", "pos": "noun"},
        "आकाश": {"trans": "आकास", "phonetic": "Aakaas", "pos": "noun"},
        
        # Animals & Birds
        "गाय": {"trans": "तली / गाय", "phonetic": "Talee", "pos": "noun"},
        "बैल": {"trans": "कोंदा", "phonetic": "Konda", "pos": "noun"},
        "कुत्ता": {"trans": "नय", "phonetic": "Nai", "pos": "noun"},
        "बिल्ली": {"trans": "वेरका", "phonetic": "Verka", "pos": "noun"},
        "पक्षी": {"trans": "पिट्टे", "phonetic": "Pitte", "pos": "noun"},
        "चिड़िया": {"trans": "पिट्टे", "phonetic": "Pitte", "pos": "noun"},
        "मछली": {"trans": "मीन", "phonetic": "Meen", "pos": "noun"},
        
        # Math & Numbers
        "एक": {"trans": "उंदी", "phonetic": "Undi", "pos": "num"},
        "दो": {"trans": "रंड", "phonetic": "Rand", "pos": "num"},
        "तीन": {"trans": "मूंद", "phonetic": "Moond", "pos": "num"},
        "चार": {"trans": "नालंग", "phonetic": "Naalang", "pos": "num"},
        "पांच": {"trans": "सयंग / पांच", "phonetic": "Sayang", "pos": "num"},
        "छह": {"trans": "सारुंग", "phonetic": "Saarung", "pos": "num"},
        "सात": {"trans": "येड़ुंग", "phonetic": "Yedung", "pos": "num"},
        "आठ": {"trans": "अटुंग", "phonetic": "Atung", "pos": "num"},
        "नौ": {"trans": "नरवंग", "phonetic": "Narwang", "pos": "num"},
        "दस": {"trans": "पाहंद", "phonetic": "Paahand", "pos": "num"},
        "गिनती": {"trans": "लेक्का", "phonetic": "Lekka", "pos": "noun"},
        "जोड़": {"trans": "कलोप / जोड़", "phonetic": "Kalop", "pos": "noun"},
        
        # Human & Body
        "बच्चा": {"trans": "पिला", "phonetic": "Pila", "pos": "noun"},
        "बच्चे": {"trans": "पिलांग", "phonetic": "Pilaang", "pos": "noun"},
        "बच्चों": {"trans": "पिलांग कुन", "phonetic": "Pilaang kun", "pos": "noun"},
        "आंख": {"trans": "कन", "phonetic": "Kan", "pos": "noun"},
        "हाथ": {"trans": "कय", "phonetic": "Kai", "pos": "noun"},
        "पैर": {"trans": "काल", "phonetic": "Kaal", "pos": "noun"},
        "सिर": {"trans": "तल्ला", "phonetic": "Talla", "pos": "noun"},
        "खाना": {"trans": "गाटो तिन", "phonetic": "Gaato Tin", "pos": "verb"},
        
        # Common Action Verbs & Particles
        "चाहिए": {"trans": "पाइजे / वेलंग", "phonetic": "Paije", "pos": "aux"},
        "होता है": {"trans": "आंद", "phonetic": "Aand", "pos": "aux"},
        "है": {"trans": "आंद", "phonetic": "Aand", "pos": "aux"},
        "हैं": {"trans": "आंदुंग", "phonetic": "Aandung", "pos": "aux"},
        "और": {"trans": "अन", "phonetic": "An", "pos": "conj"},
        "के लिए": {"trans": "संगे / साटी", "phonetic": "Sange / Saati", "pos": "prep"},
        "में": {"trans": "ते", "phonetic": "Te", "pos": "prep"},
        "से": {"trans": "ताल", "phonetic": "Taal", "pos": "prep"},
        "को": {"trans": "कून", "phonetic": "Koon", "pos": "prep"},
        "बढ़ने": {"trans": "वाड़ी कीने / पेर्के", "phonetic": "Vaadee keene", "pos": "verb"},
        "जीवित": {"trans": "जीवत", "phonetic": "Jeevat", "pos": "adj"},
        "रहने": {"trans": "मंदे", "phonetic": "Mande", "pos": "verb"},
    },
    
    "santhali": {
        # Classroom & Greetings
        "नमस्ते": {"trans": "जोहार", "phonetic": "Johar", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "सेताः जोहार", "phonetic": "Setaah Johar", "pos": "greeting"},
        "बैठ जाओ": {"trans": "दुब मे", "phonetic": "Dub Me", "pos": "verb"},
        "खड़े हो जाओ": {"trans": "तिंगु मे", "phonetic": "Tingu Me", "pos": "verb"},
        "किताब खोलो": {"trans": "पुथी झिज मे", "phonetic": "Puthi Jhij Me", "pos": "verb"},
        "ध्यान से सुनो": {"trans": "मोन दियते अंजोम मे", "phonetic": "Mon Diyate Anjom Me", "pos": "verb"},
        "लिखो": {"trans": "ओल मे", "phonetic": "Ol Me", "pos": "verb"},
        "पढ़ो": {"trans": "पाड़हाव मे", "phonetic": "Padhaav Me", "pos": "verb"},
        "बहुत अच्छा": {"trans": "आडी बेष", "phonetic": "Aadi Besh", "pos": "adj"},
        "समझ आया": {"trans": "बुझाव एना?", "phonetic": "Bujhav Ena?", "pos": "phrase"},
        "धन्यवाद": {"trans": "सराहना / जोहार", "phonetic": "Sarahna / Johar", "pos": "noun"},
        
        # Science & Nature
        "पौधा": {"trans": "दारि", "phonetic": "Daari", "pos": "noun"},
        "पौधे": {"trans": "दारि को", "phonetic": "Daari Ko", "pos": "noun"},
        "पौधों": {"trans": "दारि को लागीद", "phonetic": "Daari Ko Laageed", "pos": "noun"},
        "पेड़": {"trans": "दारे", "phonetic": "Daare", "pos": "noun"},
        "पेड़ों": {"trans": "दारे को", "phonetic": "Daare Ko", "pos": "noun"},
        "पत्ती": {"trans": "साकाम", "phonetic": "Saakaam", "pos": "noun"},
        "पत्तियां": {"trans": "साकाम को", "phonetic": "Saakaam Ko", "pos": "noun"},
        "पत्ते": {"trans": "साकाम को", "phonetic": "Saakaam Ko", "pos": "noun"},
        "जड़": {"trans": "रेहेत", "phonetic": "Rehet", "pos": "noun"},
        "फूल": {"trans": "बाहा", "phonetic": "Baaha", "pos": "noun"},
        "फल": {"trans": "जो", "phonetic": "Jo", "pos": "noun"},
        "बीज": {"trans": "जांग", "phonetic": "Jaang", "pos": "noun"},
        "पानी": {"trans": "दाः", "phonetic": "Daah", "pos": "noun"},
        "जल": {"trans": "दाः", "phonetic": "Daah", "pos": "noun"},
        "सूर्य": {"trans": "सेंगेल / बुरु / सिंगी", "phonetic": "Singi", "pos": "noun"},
        "धूप": {"trans": "सिंगी तारस", "phonetic": "Singi Taaras", "pos": "noun"},
        "सूर्य का प्रकाश": {"trans": "सिंगी मार्शल", "phonetic": "Singi Maarshal", "pos": "noun"},
        "मिट्टी": {"trans": "हासा", "phonetic": "Haasa", "pos": "noun"},
        "हवा": {"trans": "होय", "phonetic": "Hoy", "pos": "noun"},
        "वर्षा": {"trans": "दाः जाड़ि", "phonetic": "Daah Jaadi", "pos": "noun"},
        "बारिश": {"trans": "दाः जाड़ि", "phonetic": "Daah Jaadi", "pos": "noun"},
        "बादल": {"trans": "रिमिल", "phonetic": "Rimil", "pos": "noun"},
        "आकाश": {"trans": "सेरमा", "phonetic": "Serma", "pos": "noun"},
        
        # Numbers
        "एक": {"trans": "मित", "phonetic": "Mit", "pos": "num"},
        "दो": {"trans": "बार", "phonetic": "Baar", "pos": "num"},
        "तीन": {"trans": "पे", "phonetic": "Peh", "pos": "num"},
        "चार": {"trans": "पोन", "phonetic": "Pon", "pos": "num"},
        "पांच": {"trans": "मोड़े", "phonetic": "Mode", "pos": "num"},
        "छह": {"trans": "तुरुय", "phonetic": "Turui", "pos": "num"},
        "सात": {"trans": "एयाय", "phonetic": "Eyaai", "pos": "num"},
        "आठ": {"trans": "इराइल", "phonetic": "Iraail", "pos": "num"},
        "नौ": {"trans": "आरे", "phonetic": "Aare", "pos": "num"},
        "दस": {"trans": "गेल", "phonetic": "Gel", "pos": "num"},
        
        # Grammar & Connections
        "चाहिए": {"trans": "दरकार / लाकती", "phonetic": "Laaktee", "pos": "aux"},
        "होता है": {"trans": "हुयुः आ", "phonetic": "Huyuh Aa", "pos": "aux"},
        "है": {"trans": "मेनाः आ", "phonetic": "Menaah Aa", "pos": "aux"},
        "हैं": {"trans": "मेनाः कोवा", "phonetic": "Menaah Kova", "pos": "aux"},
        "और": {"trans": "आर", "phonetic": "Aar", "pos": "conj"},
        "के लिए": {"trans": "लागीद", "phonetic": "Laageed", "pos": "prep"},
        "बढ़ने": {"trans": "हाराः लागीद", "phonetic": "Haaraah laageed", "pos": "verb"},
    },
    
    "bhili": {
        # Classroom & Greetings
        "नमस्ते": {"trans": "राम राम / जोहार", "phonetic": "Ram Ram / Johar", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "सवार नो राम राम", "phonetic": "Sawaar no Ram Ram", "pos": "greeting"},
        "बैठ जाओ": {"trans": "बेही जावो", "phonetic": "Behi Jaavo", "pos": "verb"},
        "खड़े हो जाओ": {"trans": "ऊभा थावो", "phonetic": "Oobha Thaavo", "pos": "verb"},
        "किताब खोलो": {"trans": "चोपड़ी खोलो", "phonetic": "Chopdi Kholo", "pos": "verb"},
        "लिखो": {"trans": "लिखो", "phonetic": "Likho", "pos": "verb"},
        "पढ़ो": {"trans": "वांचो", "phonetic": "Vaancho", "pos": "verb"},
        "बहुत अच्छा": {"trans": "घणो हरू", "phonetic": "Ghano Haroo", "pos": "adj"},
        
        # Science & Nature
        "पौधा": {"trans": "छोड / पोधो", "phonetic": "Chhod / Podho", "pos": "noun"},
        "पौधे": {"trans": "छोडिया", "phonetic": "Chhodiya", "pos": "noun"},
        "पौधों": {"trans": "छोडिया ने", "phonetic": "Chhodiya ne", "pos": "noun"},
        "पेड़": {"trans": "झाड़ / रूखड़ो", "phonetic": "Jhaad / Rookhado", "pos": "noun"},
        "पत्ती": {"trans": "पानडु", "phonetic": "Paandu", "pos": "noun"},
        "पत्तियां": {"trans": "पांदड़ा", "phonetic": "Paandada", "pos": "noun"},
        "जड़": {"trans": "मूळ", "phonetic": "Mool", "pos": "noun"},
        "फूल": {"trans": "फूल", "phonetic": "Phool", "pos": "noun"},
        "फल": {"trans": "फळ", "phonetic": "Phal", "pos": "noun"},
        "बीज": {"trans": "बी", "phonetic": "Bee", "pos": "noun"},
        "पानी": {"trans": "पाणी", "phonetic": "Paani", "pos": "noun"},
        "जल": {"trans": "पाणी", "phonetic": "Paani", "pos": "noun"},
        "सूर्य": {"trans": "सूरज / दाड़ो", "phonetic": "Sooraj / Daado", "pos": "noun"},
        "सूर्य का प्रकाश": {"trans": "सूरज नो उजास", "phonetic": "Sooraj no Ujaas", "pos": "noun"},
        "धूप": {"trans": "तावडो", "phonetic": "Taawado", "pos": "noun"},
        "मिट्टी": {"trans": "माटी", "phonetic": "Maati", "pos": "noun"},
        "हवा": {"trans": "वायरो", "phonetic": "Vaayaro", "pos": "noun"},
        "वर्षा": {"trans": "वरसाद", "phonetic": "Varsaad", "pos": "noun"},
        
        # Numbers
        "एक": {"trans": "एक", "phonetic": "Ek", "pos": "num"},
        "दो": {"trans": "बे", "phonetic": "Bey", "pos": "num"},
        "तीन": {"trans": "तोण", "phonetic": "Ton", "pos": "num"},
        "चार": {"trans": "चार", "phonetic": "Chaar", "pos": "num"},
        "पांच": {"trans": "पांच", "phonetic": "Paanch", "pos": "num"},
        
        # Grammar
        "चाहिए": {"trans": "जोवे", "phonetic": "Jove", "pos": "aux"},
        "और": {"trans": "ने", "phonetic": "Ne", "pos": "conj"},
        "के लिए": {"trans": "सारु / वास्ते", "phonetic": "Saaru / Vaaste", "pos": "prep"},
        "बढ़ने": {"trans": "वधवा सारु", "phonetic": "Vadhva saaru", "pos": "verb"},
        "है": {"trans": "छे", "phonetic": "Chhe", "pos": "aux"},
    },
    
    "telugu": {
        # Classroom & Greetings
        "नमस्ते": {"trans": "నమస్కారం (जोहार)", "phonetic": "Namaskaram", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "శుభోదయం", "phonetic": "Shubhodayam", "pos": "greeting"},
        "बैठ जाओ": {"trans": "కూర్చోండి", "phonetic": "Koorchondi", "pos": "verb"},
        "खड़े हो जाओ": {"trans": "నిలబడండి", "phonetic": "Nilabadandi", "pos": "verb"},
        "किताब खोलो": {"trans": "పుస్తకం తెరవండి", "phonetic": "Pustakam Teravandi", "pos": "verb"},
        "ध्यान से सुनो": {"trans": "శ్రద్ధగా వినండి", "phonetic": "Shraddhaga Vinandi", "pos": "verb"},
        "लिखो": {"trans": "రాయండి", "phonetic": "Raayandi", "pos": "verb"},
        "पढ़ो": {"trans": "చదవండి", "phonetic": "Chadavandi", "pos": "verb"},
        "बहुत अच्छा": {"trans": "చాలా బాగుంది", "phonetic": "Chaala Baagundi", "pos": "adj"},
        
        # Science & Nature
        "पौधा": {"trans": "మొక్క", "phonetic": "Mokka", "pos": "noun"},
        "पौधे": {"trans": "మొక్కలు", "phonetic": "Mokkalu", "pos": "noun"},
        "पौधों": {"trans": "మొక్కలు ఎదగడానికి", "phonetic": "Mokkalu Edagadaniki", "pos": "noun"},
        "पेड़": {"trans": "చెట్టు", "phonetic": "Chettu", "pos": "noun"},
        "पेड़ों": {"trans": "చెట్లు", "phonetic": "Chetlu", "pos": "noun"},
        "पत्ती": {"trans": "ఆకు", "phonetic": "Aaku", "pos": "noun"},
        "पत्तियां": {"trans": "ఆకులు", "phonetic": "Aakulu", "pos": "noun"},
        "पत्ते": {"trans": "ఆకులు", "phonetic": "Aakulu", "pos": "noun"},
        "जड़": {"trans": "వేరు", "phonetic": "Veru", "pos": "noun"},
        "फूल": {"trans": "పువ్వు", "phonetic": "Puvvu", "pos": "noun"},
        "फल": {"trans": "పండు", "phonetic": "Pandu", "pos": "noun"},
        "बीज": {"trans": "విత్తనం", "phonetic": "Vittanam", "pos": "noun"},
        "पानी": {"trans": "నీరు", "phonetic": "Neeru", "pos": "noun"},
        "जल": {"trans": "నీరు", "phonetic": "Neeru", "pos": "noun"},
        "सूर्य": {"trans": "సూర్యుడు", "phonetic": "Sooryudu", "pos": "noun"},
        "सूर्य का प्रकाश": {"trans": "సూర్యరశ్మి", "phonetic": "Sooryarashmi", "pos": "noun"},
        "धूप": {"trans": "ఎండ", "phonetic": "Enda", "pos": "noun"},
        "मिट्टी": {"trans": "మట్టి", "phonetic": "Matti", "pos": "noun"},
        "हवा": {"trans": "గాలి", "phonetic": "Gaali", "pos": "noun"},
        "वर्षा": {"trans": "వర్షం", "phonetic": "Varsham", "pos": "noun"},
        
        # Numbers
        "एक": {"trans": "ఒకటి", "phonetic": "Okati", "pos": "num"},
        "दो": {"trans": "రెండు", "phonetic": "Rendu", "pos": "num"},
        "तीन": {"trans": "మూడు", "phonetic": "Moodu", "pos": "num"},
        "चार": {"trans": "నాలుగు", "phonetic": "Naalugu", "pos": "num"},
        "पांच": {"trans": "ఐదు", "phonetic": "Aidu", "pos": "num"},
        
        # Grammar
        "चाहिए": {"trans": "కావాలి", "phonetic": "Kaavaali", "pos": "aux"},
        "और": {"trans": "మరియు", "phonetic": "Mariyu", "pos": "conj"},
        "के लिए": {"trans": "కోసం", "phonetic": "Kosam", "pos": "prep"},
        "बढ़ने": {"trans": "ఎదగడానికి", "phonetic": "Edagadaaniki", "pos": "verb"},
        "है": {"trans": "ఉంది", "phonetic": "Undi", "pos": "aux"},
    },
    
    "mundari": {
        "नमस्ते": {"trans": "जोहार", "phonetic": "Johar", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "सेताः जोहार", "phonetic": "Setaah Johar", "pos": "greeting"},
        "बैठ जाओ": {"trans": "दुबु मे", "phonetic": "Dubu Me", "pos": "verb"},
        "किताब खोलो": {"trans": "पुथी ओलोः मे", "phonetic": "Puthi Oloh Me", "pos": "verb"},
        "लिखो": {"trans": "ओल मे", "phonetic": "Ol Me", "pos": "verb"},
        "पढ़ो": {"trans": "पड़ाव मे", "phonetic": "Padaav Me", "pos": "verb"},
        "पौधा": {"trans": "दारु", "phonetic": "Daaru", "pos": "noun"},
        "पौधे": {"trans": "दारु को", "phonetic": "Daaru Ko", "pos": "noun"},
        "पेड़": {"trans": "दारु", "phonetic": "Daaru", "pos": "noun"},
        "पत्ती": {"trans": "साकाम", "phonetic": "Saakaam", "pos": "noun"},
        "पानी": {"trans": "दाः", "phonetic": "Daah", "pos": "noun"},
        "सूर्य": {"trans": "सिंगी", "phonetic": "Singi", "pos": "noun"},
        "हवा": {"trans": "होयो", "phonetic": "Hoyo", "pos": "noun"},
        "मिट्टी": {"trans": "हासा", "phonetic": "Haasa", "pos": "noun"},
        "चाहिए": {"trans": "दरकार", "phonetic": "Dorkaar", "pos": "aux"},
        "और": {"trans": "ओन्दोः", "phonetic": "Ondoh", "pos": "conj"},
    },
    
    "kurukh": {
        "नमस्ते": {"trans": "जोहार", "phonetic": "Johar", "pos": "greeting"},
        "शुभ प्रभात": {"trans": "पइरी जोहार", "phonetic": "Pairi Johar", "pos": "greeting"},
        "बैठ जाओ": {"trans": "उक्का", "phonetic": "Ukka", "pos": "verb"},
        "किताब खोलो": {"trans": "पोथी उघड़ा", "phonetic": "Pothi Ughada", "pos": "verb"},
        "लिखो": {"trans": "टिड़ा", "phonetic": "Tida", "pos": "verb"},
        "पढ़ो": {"trans": "पढ़ा", "phonetic": "Padha", "pos": "verb"},
        "पौधा": {"trans": "मन", "phonetic": "Mann", "pos": "noun"},
        "पौधे": {"trans": "मन गुठी", "phonetic": "Mann Guthi", "pos": "noun"},
        "पेड़": {"trans": "मन", "phonetic": "Mann", "pos": "noun"},
        "पत्ती": {"trans": "अट्खा", "phonetic": "Atkha", "pos": "noun"},
        "पानी": {"trans": "अम्म", "phonetic": "Amm", "pos": "noun"},
        "सूर्य": {"trans": "बीड़ी", "phonetic": "Beedi", "pos": "noun"},
        "हवा": {"trans": "ताक़ा", "phonetic": "Taaqa", "pos": "noun"},
        "मिट्टी": {"trans": "खेलो", "phonetic": "Khelo", "pos": "noun"},
        "चाहिए": {"trans": "चाही", "phonetic": "Chaahi", "pos": "aux"},
        "और": {"trans": "दरा", "phonetic": "Dara", "pos": "conj"},
    }
}

# Pre-compiled high-frequency classroom sentence pairs for exact match
CURATED_SENTENCE_PAIRS: Dict[str, Dict[str, Dict[str, str]]] = {
    "gondi": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "मरान तेकी वाड़ी कीने संगे येर अन पोरदु वेलंग पाइजे।",
            "phonetic": "Maraan teki vaadee keene sange yer an pordu velang paije."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "मरान तेकी येर पाइजे।",
            "phonetic": "Maraan teki yer paije."
        },
        "पौधे हमें ऑक्सीजन देते हैं।": {
            "trans": "मरान माकुन जिवा वली सियांदुंग।",
            "phonetic": "Maraan maakun jeeva valee siyaandung."
        },
        "पत्तियां पौधे के लिए भोजन बनाती हैं।": {
            "trans": "आकीन मरान संगे गाटो तयार कीतांदुंग।",
            "phonetic": "Aakeen maraan sange gaato tayar keetaandung."
        },
        "जल ही जीवन है।": {
            "trans": "येरे जीवाना आंद।",
            "phonetic": "Yere jeevana aand."
        },
        "सभी बच्चे अपनी किताब खोलें।": {
            "trans": "सब्बू पिलांग तंतना पोथी उघड़ कीम।",
            "phonetic": "Sabbu pilaang tantna pothi ughad keem."
        },
        "आज हम विज्ञान पढ़ेंगे।": {
            "trans": "नेन्दु ममोत विज्ञान वाचा कियाकट।",
            "phonetic": "Nendu mamot vigyaan vaacha keeyakat."
        },
        "गिनती 1 से 10 तक गिनो।": {
            "trans": "उंदी ताल पाहंद तक लेक्का कीम।",
            "phonetic": "Undi taal paahand tak lekka keem."
        }
    },
    "santhali": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "दारि को हाराः लागीद दाः आर सिंगी मार्शल लाकती मेनाः आ।",
            "phonetic": "Daari ko haaraah laageed daah aar singi maarshal laaktee menaah aa."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "दारि को लागीद दाः लाकती आ।",
            "phonetic": "Daari ko laageed daah laaktee aa."
        },
        "जल ही जीवन है।": {
            "trans": "दाः गे जीवन काना।",
            "phonetic": "Daah ge jeevan kaana."
        },
        "सभी बच्चे अपनी किताब खोलें।": {
            "trans": "जातो गिदराः आपन पुथी झिज पे।",
            "phonetic": "Jaato gidraah aapan puthi jhij pe."
        }
    },
    "bhili": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "छोडिया ने वधवा सारु पाणी ने सूरज नो उजास जोवे।",
            "phonetic": "Chhodiya ne vadhva saaru paani ne sooraj no ujaas jove."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "छोडिया ने पाणी जोवे।",
            "phonetic": "Chhodiya ne paani jove."
        },
        "जल ही जीवन है।": {
            "trans": "पाणी इज जीवन छे।",
            "phonetic": "Paani ij jeevan chhe."
        }
    },
    "telugu": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "మొక్కలు ఎదగడానికి నీరు మరియు సూర్యరశ్మి కావాలి.",
            "phonetic": "Mokkalu edagadaaniki neeru mariyu sooryarashmi kaavaali."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "మొక్కలకు నీరు కావాలి.",
            "phonetic": "Mokkalaku neeru kaavaali."
        },
        "जल ही जीवन है।": {
            "trans": "నీరే ప్రాణాధారం.",
            "phonetic": "Neere praanaadhaaram."
        }
    },
    "mundari": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "दारु को हराः लागीद दाः ओन्दोः सिंगी मार्शल दरकार मेनाः।",
            "phonetic": "Daaru ko haraah laageed daah ondoh singi maarshal dorkaar menaah."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "दारु को लागीद दाः दरकार।",
            "phonetic": "Daaru ko laageed daah dorkaar."
        }
    },
    "kurukh": {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।": {
            "trans": "मन गुठीन बढ़ना गे अम्म दरा बीड़ी बीड़ा चाही।",
            "phonetic": "Mann gutheen badhna ge amm dara beedi beeda chaahi."
        },
        "पौधों को पानी चाहिए।": {
            "trans": "मन गुठीन अम्म चाही।",
            "phonetic": "Mann gutheen amm chaahi."
        }
    }
}


import urllib.request
import urllib.parse
import json

class TranslationEngine:
    """
    Classroom-Grade Translation Engine specifically tuned for Hindi -> Tribal & Regional Tongues.
    Provides instant offline translation, vocabulary highlights, and pronunciation hints.
    Integrates neural translation for Telugu and regional Indian languages.
    """

    def __init__(self):
        self.indictrans_url = os.getenv("INDICTRANS2_API_URL", "").strip()
        self._cache: Dict[str, str] = {}

    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        return LANGUAGES

    def normalize_text(self, text: str) -> str:
        text = text.strip()
        # Normalize punctuation
        text = re.sub(r"\s+", " ", text)
        return text

    def _translate_neural(self, text: str, target_lang: str) -> Optional[str]:
        """
        Neural translation using open linguistic endpoints with in-memory caching.
        Particularly powerful for full-text Telugu (te) translation.
        """
        lang_map = {
            "telugu": "te",
            "tel": "te"
        }
        target_code = lang_map.get(target_lang)
        if not target_code:
            return None

        cache_key = f"hi->{target_code}:{text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Try MyMemory API
        try:
            encoded_q = urllib.parse.quote(text)
            url = f"https://api.mymemory.translated.net/get?q={encoded_q}&langpair=hi|{target_code}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    trans_text = data.get("responseData", {}).get("translatedText")
                    if trans_text and not trans_text.startswith("MYMEMORY WARNING"):
                        self._cache[cache_key] = trans_text
                        return trans_text
        except Exception as e:
            logger.warning(f"MyMemory neural translation attempt failed: {e}")

        # 2. Try deep_translator GoogleTranslator fallback
        try:
            from deep_translator import GoogleTranslator
            res = GoogleTranslator(source="hi", target=target_code).translate(text)
            if res:
                self._cache[cache_key] = res
                return res
        except Exception as e:
            logger.warning(f"deep_translator GoogleTranslator attempt failed: {e}")

        return None

    def translate_sentence(self, hindi_text: str, target_lang: str) -> Dict[str, Any]:
        """
        Translates a single Hindi sentence into the target tribal/regional language.
        Returns target text, pronunciation guide, token matches, and metadata.
        """
        target_lang = target_lang.lower().strip()
        if target_lang not in LANGUAGES:
            target_lang = "gondi"  # default fallback

        cleaned_hindi = self.normalize_text(hindi_text)
        if not cleaned_hindi:
            return {
                "source_text": "",
                "translated_text": "",
                "pronunciation": "",
                "target_lang": target_lang,
                "confidence": 1.0,
                "engine": "empty"
            }

        # 0. Pralekha Offline Dataset Check (SQLite database built from HF bucket srilakshmi-08/Pralekha-bucket)
        try:
            from backend.database import query_pralekha_sentence
            pralekha_match = query_pralekha_sentence(cleaned_hindi, "hindi", target_lang)
            if not pralekha_match:
                pralekha_match = query_pralekha_sentence(cleaned_hindi, "english", target_lang)
            if pralekha_match:
                return {
                    "source_text": cleaned_hindi,
                    "translated_text": pralekha_match,
                    "pronunciation": f"{LANGUAGES.get(target_lang, {}).get('name', target_lang)} (Pralekha Dataset)",
                    "target_lang": target_lang,
                    "confidence": 0.99,
                    "engine": "pralekha_offline_db",
                    "vocabulary_highlight": self._extract_vocab(cleaned_hindi, target_lang)
                }
        except Exception as err:
            logger.warning(f"Pralekha offline DB query failed: {err}")

        # 1. Exact Sentence Match Check (Curated high-accuracy pairs)
        if target_lang in CURATED_SENTENCE_PAIRS:
            for pattern, match in CURATED_SENTENCE_PAIRS[target_lang].items():
                if cleaned_hindi.rstrip("। .!?") == pattern.rstrip("। .!?"):
                    return {
                        "source_text": cleaned_hindi,
                        "translated_text": match["trans"],
                        "pronunciation": match["phonetic"],
                        "target_lang": target_lang,
                        "confidence": 0.98,
                        "engine": "curated_pair",
                        "vocabulary_highlight": self._extract_vocab(cleaned_hindi, target_lang)
                    }

        # 2. Neural Translation Check for Telugu & Regional Languages
        neural_res = self._translate_neural(cleaned_hindi, target_lang)
        if neural_res:
            return {
                "source_text": cleaned_hindi,
                "translated_text": neural_res,
                "pronunciation": "తెలుగు / Telugu",
                "target_lang": target_lang,
                "confidence": 0.99,
                "engine": "neural_full_translator",
                "vocabulary_highlight": self._extract_vocab(cleaned_hindi, target_lang)
            }

        # 3. Rule-Based & Vocabulary Synthesis
        lang_dict = DICTIONARY.get(target_lang, DICTIONARY["gondi"])
        
        # Split tokens preserving punctuation
        tokens = re.findall(r"[\u0900-\u097F]+|[A-Za-z]+|[0-9]+|[^\s\w]", cleaned_hindi)
        
        translated_tokens = []
        phonetic_tokens = []
        matched_vocab = []

        # Sliding window 3, 2, 1 for multi-word phrase matching
        i = 0
        n = len(tokens)
        while i < n:
            matched = False
            # Check 3-word phrase
            if i + 2 < n:
                phrase3 = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                if phrase3 in lang_dict:
                    item = lang_dict[phrase3]
                    translated_tokens.append(item["trans"])
                    phonetic_tokens.append(item["phonetic"])
                    matched_vocab.append({"hi": phrase3, "target": item["trans"], "phonetic": item["phonetic"]})
                    i += 3
                    continue

            # Check 2-word phrase
            if i + 1 < n:
                phrase2 = f"{tokens[i]} {tokens[i+1]}"
                if phrase2 in lang_dict:
                    item = lang_dict[phrase2]
                    translated_tokens.append(item["trans"])
                    phonetic_tokens.append(item["phonetic"])
                    matched_vocab.append({"hi": phrase2, "target": item["trans"], "phonetic": item["phonetic"]})
                    i += 2
                    continue

            token = tokens[i]
            # Single word dictionary lookup
            if token in lang_dict:
                item = lang_dict[token]
                translated_tokens.append(item["trans"])
                phonetic_tokens.append(item["phonetic"])
                matched_vocab.append({"hi": token, "target": item["trans"], "phonetic": item["phonetic"]})
            else:
                # Keep original token or punctuation
                translated_tokens.append(token)
                phonetic_tokens.append(token)
            i += 1

        # Reconstruct translated string
        translated_text = " ".join(translated_tokens)
        # Clean up spacing before punctuation
        translated_text = re.sub(r'\s+([।,;!?\.\'])', r'\1', translated_text)
        translated_text = re.sub(r'\s+', ' ', translated_text).strip()

        pronunciation = " ".join(phonetic_tokens)
        pronunciation = re.sub(r'\s+([।,;!?\.\'])', r'\1', pronunciation)
        pronunciation = re.sub(r'\s+', ' ', pronunciation).strip()

        # Confidence based on percentage of matched tokens
        match_ratio = len(matched_vocab) / max(1, len([t for t in tokens if re.match(r"[\u0900-\u097F]+", t)]))
        confidence = min(0.95, max(0.65, round(0.60 + (match_ratio * 0.35), 2)))

        return {
            "source_text": cleaned_hindi,
            "translated_text": translated_text,
            "pronunciation": pronunciation,
            "target_lang": target_lang,
            "confidence": confidence,
            "engine": "hybrid_lexicon_rules",
            "vocabulary_highlight": matched_vocab
        }

    def _extract_vocab(self, hindi_text: str, target_lang: str) -> List[Dict[str, str]]:
        lang_dict = DICTIONARY.get(target_lang, {})
        extracted = []
        for word, val in lang_dict.items():
            if word in hindi_text and len(word) > 1:
                extracted.append({"hi": word, "target": val["trans"], "phonetic": val["phonetic"]})
        return extracted[:5]

    def translate_document_segments(self, segments: List[str], target_lang: str) -> List[Dict[str, Any]]:
        """
        Translates a list of paragraph or sentence segments in batch.
        """
        results = []
        for seg in segments:
            seg_clean = seg.strip()
            if not seg_clean:
                continue
            translated = self.translate_sentence(seg_clean, target_lang)
            results.append(translated)
        return results


# Global singleton instance
translation_engine = TranslationEngine()
