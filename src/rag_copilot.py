import os
import sys
import re
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Automatically load GEMINI_API_KEY from ~/.env or project .env
load_dotenv(os.path.expanduser("~/.env"), override=True)
load_dotenv(override=True)


# Structured knowledge base extracted from docs/technical_manual.md (EN, ES, EU)
MANUAL_KNOWLEDGE = {
    "Page 4": {
        "comp": "LOTO",
        "torque": "0 bar (V-102) / 0 V (400V AC Breaker)",
        "en": {
            "name": "General LOTO Safety Protocol",
            "spare": "Personal safety padlock, lockout tag, cut-resistant gloves, and safety glasses",
            "symptoms": "Mandatory before any intervention on model1, model2, model3, or model4",
            "steps": [
                "1. Turn off the main 400V AC three-phase breaker and place your personal padlock and lockout tag (LOTO).",
                "2. Depressurize hydraulic and pneumatic circuits by opening relief valve V-102 until the gauge reads 0 bar.",
                "3. Wait 20 minutes if the housing exceeds 65 °C and wear cut-resistant gloves and safety glasses."
            ]
        },
        "es": {
            "name": "Protocolo General de Seguridad LOTO",
            "spare": "Candado personal LOTO, etiqueta de bloqueo, guantes anticorte y gafas de seguridad",
            "symptoms": "Obligatorio antes de intervenir en cualquier máquina (model1, model2, model3 o model4)",
            "steps": [
                "1. Cortar el interruptor general trifásico (400V AC) y colocar tu candado personal y etiqueta LOTO.",
                "2. Despresurizar el circuito abriendo la válvula de alivio V-102 hasta que el manómetro marque 0 bar.",
                "3. Esperar 20 minutos si la carcasa supera los 65 °C y utilizar guantes anticorte y gafas de protección."
            ]
        },
        "eu": {
            "name": "LOTO Segurtasun Protokolo Orokorra",
            "spare": "LOTO segurtasun-giltzarrapoa, blokeo-etiketa, ebaki-aurkako eskularruak eta betaurrekoak",
            "symptoms": "Derrigorrezkoa edozein makina (model1, model2, model3 edo model4) ireki aurretik",
            "steps": [
                "1. Etengailu orokor trifasikoa (400V AC) itzali eta zure segurtasun kandatua eta LOTO etiketa jarri.",
                "2. Zirkuitua despresurizatu V-102 arintze-balbula irekiz manometroak 0 bar markatu arte.",
                "3. Itxaron 20 minutu karkasak 65 °C gainditzen baditu eta erabili ebakiak sahiesteko eskularruak eta betaurrekoak."
            ]
        }
    },
    "Page 12": {
        "comp": "comp1",
        "torque": "85 Nm",
        "hours": 4.0,
        "prev_cost": 700,
        "fail_cost": 5200,
        "en": {
            "name": "Main Electromechanical Drive Unit (comp1)",
            "spare": "Main drive cartridge and brush kit `REF-C1-DRIVE-840D`",
            "symptoms": "Sustained high voltage (`volt > 180 V`), unstable rotation speed (`rotate`), and frequent **`error1`** alarms (drive inverter electrical overload)",
            "steps": [
                "1. Lock the vertical axis in the middle position using safety block CM-04.",
                "2. Disconnect the 6-pin Harting power plug and the stator cooling hose.",
                "3. Loosen the 8 front flange M12 bolts in a cross pattern.",
                "4. Extract the damaged comp1 cartridge using the hydraulic puller and clean the housing with residue-free solvent.",
                "5. Install the new comp1 unit applying a tightening torque of 85 Nm with a calibrated torque wrench, and verify radial runout (< 0.004 mm)."
            ]
        },
        "es": {
            "name": "Unidad Motriz Electromecánica Principal (comp1)",
            "spare": "Cartucho de unidad motriz principal y kit de escobillas `REF-C1-DRIVE-840D`",
            "symptoms": "Subida sostenida de voltaje (`volt > 180 V`), giro inestable (`rotate`) y aparición de la alarma **`error1`** (sobrecarga eléctrica en el inversor)",
            "steps": [
                "1. Bloquear el eje vertical en posición intermedia mediante el calzo de seguridad CM-04.",
                "2. Desconectar el conector de potencia Harting de 6 pines y la manguera de refrigeración del estátor.",
                "3. Aflojar los 8 tornillos M12 de la brida frontal en secuencia cruzada.",
                "4. Extraer el cartucho comp1 dañado con extractor hidráulico y limpiar el alojamiento con disolvente.",
                "5. Instalar la nueva unidad comp1 aplicando un par de apriete de 85 Nm con llave dinamométrica y verificar salto radial (< 0.004 mm)."
            ]
        },
        "eu": {
            "name": "Unitate Eragile Elektromekaniko Nagusia (comp1)",
            "spare": "Unitate eragile nagusiaren kartutxoa eta eskuila-kita `REF-C1-DRIVE-840D`",
            "symptoms": "Tentsio igoera iraunkorra (`volt > 180 V`), biraketa ezegonkorra (`rotate`) eta **`error1`** alarma (gainkarga elektrikoa inbertsorean)",
            "steps": [
                "1. Ardatz bertikala erdiko posizioan blokeatu CM-04 segurtasun-ziriarekin.",
                "2. 6 pineko Harting potentzia-konektorea eta estatorearen hozte mangera deskonektatu.",
                "3. Aurreko bridako 8 M12 torlojuak gurutzatuta soltatu.",
                "4. Hondatutako comp1 kartutxoa erauzgailu hidraulikoarekin atera eta alojamendua disolbatzailearekin garbitu.",
                "5. comp1 unitate berria instalatu giltza dinamometrikoarekin 85 Nm-ko pare bat estutze aplikatuz eta jauzi erradiala egiaztatu (< 0.004 mm)."
            ]
        }
    },
    "Page 27": {
        "comp": "comp2",
        "torque": "24 Nm",
        "hours": 3.0,
        "prev_cost": 500,
        "fail_cost": 4400,
        "en": {
            "name": "High-Pressure Hydraulic Valve Assembly (comp2)",
            "spare": "Proportional hydraulic valve `4WREE-10` + 5-micron filter kit `REF-C2-HYD` (with Viton O-rings `NBR-90` and `ISO VG 46` hydraulic oil)",
            "symptoms": "Sharp spikes or fluctuations in pressure (`pressure > 115 bar`) and triggering of **`error2`** (pressure loop deviation) and **`error3`** (hydraulic filter clogging)",
            "steps": [
                "1. Fully depressurize the nitrogen accumulator by opening purge valve V-102 to 0 bar.",
                "2. Place an oil drip tray under the manifold block and remove the 4 M8 Allen bolts holding the valve.",
                "3. Replace the Viton O-rings (NBR-90) lubricated with clean ISO VG 46 hydraulic oil.",
                "4. Mount the new comp2 valve applying a tightening torque of 24 Nm and replace the high-pressure filter element.",
                "5. Bleed trapped air by running 10 manual clamping cycles and calibrate nominal pressure to 100.0 ± 1.5 bar."
            ]
        },
        "es": {
            "name": "Grupo de Válvula Hidráulica de Alta Presión (comp2)",
            "spare": "Válvula hidráulica proporcional `4WREE-10` + kit de filtro de 5 micras `REF-C2-HYD` (con juntas Viton `NBR-90` y aceite `ISO VG 46`)",
            "symptoms": "Picos bruscos o fluctuaciones de presión (`pressure > 115 bar`) y disparo de las alarmas **`error2`** (desviación de presión) y **`error3`** (filtro hidráulico obstruido)",
            "steps": [
                "1. Despresurizar por completo el acumulador de nitrógeno abriendo la válvula de purga V-102 hasta 0 bar.",
                "2. Colocar bandeja recolectora bajo el bloque colector y retirar los 4 tornillos Allen M8 de la válvula.",
                "3. Sustituir las juntas tóricas de Viton (NBR-90) lubricadas con aceite hidráulico limpio ISO VG 46.",
                "4. Montar la nueva válvula comp2 aplicando un par de apriete de 24 Nm y cambiar el elemento filtrante.",
                "5. Purgar el aire ejecutando 10 ciclos manuales de amarre y calibrar la presión nominal a 100.0 ± 1.5 bar."
            ]
        },
        "eu": {
            "name": "Presio Handiko Balbula Hidraulikoaren Multzoa (comp2)",
            "spare": "`4WREE-10` balbula hidrauliko proportzionala + 5 mikrako filtro-kita `REF-C2-HYD` (`NBR-90` Viton junturekin eta `ISO VG 46` olioarekin)",
            "symptoms": "Presio-igoera handiak (`pressure > 115 bar`) eta **`error2`** zein **`error3`** alarmak (presio-desbideratzea eta iragazkiaren buxadura)",
            "steps": [
                "1. Nitrogeno-metagailua erabat despresurizatu V-102 purga-balbula 0 bar-era irekiz.",
                "2. Olio-erretilua bloke kolektorearen azpian jarri eta balbulako 4 M8 Allen torlojuak kendu.",
                "3. Vitoneko junta torikoak (NBR-90) ordezkatu ISO VG 46 olio hidrauliko garbiarekin lubrifikatuta.",
                "4. comp2 balbula berria muntatu 24 Nm-ko estutze-parea aplikatuz eta presio handiko iragazkia aldatu.",
                "5. Airea purgatu 10 eskuzko lotura-ziklo eginez eta presio nominala 100.0 ± 1.5 bar-ean kalibratu."
            ]
        }
    },
    "Page 41": {
        "comp": "comp3",
        "torque": "42 Nm",
        "hours": 5.0,
        "prev_cost": 800,
        "fail_cost": 5800,
        "en": {
            "name": "Feed Axis Servomotor and Ball Screw Coupling (comp3)",
            "spare": "Preloaded ball nut and flexible servo coupling assembly `REF-C3-SERVO-Z` (lubricated with `Kluber Isoflex Topas NCA 52` lithium grease)",
            "symptoms": "Drop in effective rotation speed (`rotate < 400 RPM`) due to mechanical backlash/wear, triggering **`error4`** (axis contour following error)",
            "steps": [
                "1. Secure the carriage with a certified lifting sling (minimum capacity 1,500 kg) before releasing the motor coupling.",
                "2. Remove the bellows coupling (R+W BK5) and inspect the keyway and optical encoder shaft.",
                "3. Install the new comp3 support and coupling assembly applying a tightening torque of 42 Nm on the radial clamping bolts.",
                "4. Lubricate the ball screw with synthetic lithium grease Kluber Isoflex Topas NCA 52.",
                "5. Run CNC reference routine G74 to reset machine zero and verify backlash compensation."
            ]
        },
        "es": {
            "name": "Servomotor del Eje de Avance y Acoplamiento de Husillo a Bolas (comp3)",
            "spare": "Conjunto de tuerca de bolas pretensada y acoplamiento flexible de servomotor `REF-C3-SERVO-Z` (con grasa de litio `Kluber Isoflex Topas NCA 52`)",
            "symptoms": "Caída acusada en la velocidad de rotación (`rotate < 400 RPM`) por holgura mecánica, disparando la alarma **`error4`** (error de posicionamiento en encóder)",
            "steps": [
                "1. Asegurar el carro con eslinga de carga certificada (mínimo 1.500 kg) antes de soltar el acoplamiento.",
                "2. Retirar el acoplamiento de fuelle (R+W BK5) e inspeccionar el chavetero y el eje del encóder óptico.",
                "3. Instalar el nuevo soporte y acoplamiento comp3 aplicando un par de apriete de 42 Nm en los tornillos radiales.",
                "4. Lubricar el husillo a bolas con grasa sintética de litio Kluber Isoflex Topas NCA 52.",
                "5. Ejecutar la rutina CNC G74 de referenciado de cero máquina y verificar la compensación de holgura."
            ]
        },
        "eu": {
            "name": "Aitzinapen-ardatzeko Serbomotorra eta Bola-torlojuaren Akoplamendua (comp3)",
            "spare": "Aurrez teinkatutako bola-azkoina eta serbomotorraren akoplamendu malgua `REF-C3-SERVO-Z` (`Kluber Isoflex Topas NCA 52` litiozko koipearekin)",
            "symptoms": "Biraketa-abiaduraren jaitsiera (`rotate < 400 RPM`) lasaiera mekanikoagatik eta **`error4`** alarma (posizionamendu-errorea enkoderrean)",
            "steps": [
                "1. Karroa ziurtatutako karga-eslingarekin lotu (gutxienez 1.500 kg) motorraren akoplamendua askatu aurretik.",
                "2. Hauspo-akoplamendua (R+W BK5) kendu eta txabetazuloa zein enkoder optikoaren ardatza ikuskatu.",
                "3. comp3 euskarri eta akoplamendu berria instalatu torloju erradialetan 42 Nm-ko estutze-parea aplikatuz.",
                "4. Bola-torlojua Kluber Isoflex Topas NCA 52 litiozko koipe sintetikoarekin lubrifikatu.",
                "5. G74 CNC erreferentzia-errutina exekutatu makina-zeroa berrezartzeko eta lasaiera-konpentsazioa egiaztatu."
            ]
        }
    },
    "Page 58": {
        "comp": "comp4",
        "torque": "65 Nm",
        "hours": 4.5,
        "prev_cost": 600,
        "fail_cost": 4800,
        "en": {
            "name": "High-Speed Angular Contact Bearings (comp4)",
            "spare": "Matched ceramic bearing set **SKF Super-Precision `7014 CD/HCP4A`** (`REF-C4-SKF`) + locknut `KMT 14`",
            "symptoms": "Exponential rise in vibration (`vibration > 48 mm/s`) and high 24h vibration standard deviation, triggering **`error5`** (critical shaft vibration alarm)",
            "steps": [
                "1. Remove the front labyrinth cover and extract the worn comp4 bearings using an induction puller (never hit with a hammer).",
                "2. Inspect the shaft journal to ensure there is no fretting corrosion or scoring.",
                "3. Heat the new SKF bearings to 85 °C on an induction heater and mount them in back-to-back (DB) arrangement matching the V-marks.",
                "4. Tighten precision locknut KMT 14 to a tightening torque of 65 Nm and secure the bronze locking pins.",
                "5. Execute the mandatory 45-minute grease run-in cycle stepping from 1,000 to 8,000 RPM while monitoring bearing temperature."
            ]
        },
        "es": {
            "name": "Rodamientos Axiales de Contacto Angular de Alta Velocidad (comp4)",
            "spare": "Juego emparejado de rodamientos cerámicos **SKF Super-Precision `7014 CD/HCP4A`** (`REF-C4-SKF`) + tuerca de precisión `KMT 14`",
            "symptoms": "Subida exponencial de la vibración (`vibration > 48 mm/s`) y alta desviación típica en 24h, disparando la alarma **`error5`** (umbral crítico de vibración)",
            "steps": [
                "1. Desmontar la tapa laberíntica frontal y extraer los rodamientos comp4 dañados con extractor de inducción (nunca golpear con martillo).",
                "2. Inspeccionar el asiento del eje verificando que no exista corrosión de contacto ni marcas.",
                "3. Calentar los nuevos rodamientos SKF a 85 °C en placa de inducción y montarlos en disposición espalda con espalda (DB) alineando las marcas en V.",
                "4. Apretar la tuerca de precisión KMT 14 aplicando un par de apriete de 65 Nm y asegurar los prisioneros de bronce.",
                "5. Ejecutar el ciclo obligatorio de rodaje de grasa de 45 minutos escalonando de 1.000 a 8.000 RPM controlando la temperatura."
            ]
        },
        "eu": {
            "name": "Abiadura Handiko Kontaktu Angeluarreko Errodamenduak (comp4)",
            "spare": "**SKF Super-Precision `7014 CD/HCP4A`** errodamendu zeramikoen joko parekatua (`REF-C4-SKF`) + `KMT 14` doitasun-azkoina",
            "symptoms": "Bibrazioaren igoera handia (`vibration > 48 mm/s`) azken 24 orduetan eta **`error5`** alarma (ardatzaren bibrazio kritikoa)",
            "steps": [
                "1. Aurreko estalki labirintikoa kendu eta higatutako comp4 errodamenduak indukzio-erauzgailuarekin atera (inoiz ez jo mailuarekin).",
                "2. Ardatzaren euskarria ikuskatu korrosiorik edo markarik ez dagoela ziurtatzeko.",
                "3. SKF errodamendu berriak 85 °C-ra berotu indukzio-plakan eta bizkarrez bizkar (DB) muntatu V-markak lerrokatuz.",
                "4. KMT 14 doitasun-azkoina estutu 65 Nm-ko estutze-parea aplikatuz eta brontzezko torlojuak finkatu.",
                "5. Derrigorrezko 45 minutuko koipe-rodaje zikloa egin 1.000tik 8.000 RPM-ra mailakatuz tenperatura kontrolatzen den bitartean."
            ]
        }
    }
}


class MaintenanceRAGCopilot:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.manual_path = os.path.join(base_dir, "docs", "technical_manual.md")
        self.schedule_path = os.path.join(base_dir, "reports", "schedule.md")

        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self._load_and_index_manual()
        self.df_schedule = self._load_schedule_md()

    def _load_and_index_manual(self):
        """Split the technical manual into sections and build the TF-IDF vector index."""
        with open(self.manual_path, "r", encoding="utf-8") as f:
            text = f.read()

        raw_sections = re.split(r"\n(?=##+ )", text)
        for idx, sec in enumerate(raw_sections):
            sec_clean = sec.strip()
            if len(sec_clean) < 40:
                continue
            first_line = sec_clean.splitlines()[0].replace("#", "").strip()
            page_match = re.search(r"Page\s*(\d+)", sec_clean)
            page_ref = f"Page {page_match.group(1)}" if page_match else "Page 4"
            self.chunks.append({
                "chunk_id": f"SEC_{idx:02d}",
                "title": first_line,
                "page": page_ref,
                "content": sec_clean
            })

        corpus = [c["title"] + " " + c["content"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def _load_schedule_md(self) -> pd.DataFrame:
        """Read the MILP schedule directly from reports/schedule.md."""
        if not os.path.exists(self.schedule_path):
            return pd.DataFrame()
        with open(self.schedule_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if "|" in line]
        if len(lines) < 3:
            return pd.DataFrame()

        headers = [col.strip() for col in lines[0].strip("|").split("|")]
        rows = [[col.strip() for col in line.strip("|").split("|")] for line in lines[2:]]
        df = pd.DataFrame(rows, columns=headers)
        df["machineID"] = df["machineID"].astype(int)
        df["repair_hours"] = df["repair_hours"].astype(float)
        df["prev_cost"] = df["prev_cost"].astype(float)
        df["real_reactive_cost"] = df["real_reactive_cost"].astype(float)
        df["real_net_savings"] = df["real_net_savings"].astype(float)
        return df

    def retrieve_context(self, query: str, machine_id: int = None, top_k: int = 2):
        """Retrieve the top_k most relevant manual sections (supporting EN, ES, and EU queries)."""
        enriched_query = query
        machine_context = None

        multilingual_map = {
            "seguridad": "LOTO safety lockout breaker 0 bar",
            "segurtasun": "LOTO safety lockout breaker 0 bar",
            "blokeo": "LOTO safety lockout breaker 0 bar",
            "bloqueo": "LOTO safety lockout breaker 0 bar",
            "antes de": "LOTO safety lockout breaker 0 bar",
            "aurretik": "LOTO safety lockout breaker 0 bar",
            "before": "LOTO safety lockout breaker 0 bar",
            "husillo": "comp1 main electromechanical drive volt error1",
            "torloju": "comp1 main electromechanical drive volt error1",
            "hidráulic": "comp2 hydraulic pressure valve 4WREE error2 error3",
            "hidraulik": "comp2 hydraulic pressure valve 4WREE error2 error3",
            "válvula": "comp2 hydraulic pressure valve 4WREE",
            "balbula": "comp2 hydraulic pressure valve 4WREE",
            "presio": "comp2 hydraulic pressure valve",
            "servomotor": "comp3 feed axis servomotor ball screw coupling error4",
            "akoplamendu": "comp3 feed axis servomotor ball screw coupling error4",
            "rodamiento": "comp4 angular contact bearings SKF vibration error5",
            "errodamendu": "comp4 angular contact bearings SKF vibration error5",
            "vibración": "comp4 bearings SKF vibration error5",
            "bibrazio": "comp4 bearings SKF vibration error5",
            "apriete": "tightening torque Nm",
            "estutze": "tightening torque Nm",
        }
        q_lower = query.lower()
        for term, eng_keywords in multilingual_map.items():
            if term in q_lower:
                enriched_query += " " + eng_keywords

        if machine_id is not None and not self.df_schedule.empty:
            m_row = self.df_schedule[self.df_schedule["machineID"] == machine_id]
            if not m_row.empty:
                r = m_row.iloc[0]
                comp = r["pred_comp"]
                is_safety_only = any(k in q_lower for k in ["loto", "seguridad", "segurtasun", "safety", "lockout", "blokeo", "bloqueo"])
                other_comp = any(c in q_lower for c in ["comp1", "comp2", "comp3", "comp4"] if c != comp)
                if not is_safety_only and not other_comp:
                    enriched_query += f" {comp}"
                machine_context = r.to_dict()

        q_vec = self.vectorizer.transform([enriched_query])
        sims = cosine_similarity(q_vec, self.tfidf_matrix).ravel()
        top_indices = np.argsort(sims)[::-1][:top_k]

        retrieved = []
        for i in top_indices:
            chunk_copy = self.chunks[i].copy()
            chunk_copy["similarity_score"] = round(float(sims[i]), 3)
            retrieved.append(chunk_copy)

        return retrieved, machine_context

    def _detect_intents(self, query: str) -> set:
        """Detect what specific topics the user is asking about in EN, ES, or EU."""
        q = query.lower()
        intents = set()

        if any(w in q for w in ["loto", "safety", "lockout", "seguridad", "bloqueo", "candado", "segurtasun", "blokeo", "giltzarrapo", "before opening", "antes de abrir", "ireki aurretik"]):
            intents.add("safety")
        if any(w in q for w in ["torque", "nm", "tighten", "apriete", "apretar", "dinamométrica", "estutze", "pare", "newton"]):
            intents.add("torque")
        if any(w in q for w in ["cost", "price", "money", "sav", "eur", "expensive", "cuesta", "coste", "costo", "precio", "dinero", "ahorr", "económ", "kostu", "prezio", "diru", "aurrez", "balio"]):
            intents.add("cost")
        if any(w in q for w in ["shift", "when", "schedule", "time", "long", "hour", "duration", "turno", "cuándo", "cuando", "calendario", "tiempo", "tarda", "hora", "duración", "txanda", "noiz", "denbora", "ordu", "iraupen"]):
            intents.add("schedule")
        if any(w in q for w in ["why", "symptom", "sensor", "error", "alarm", "volt", "rotate", "pressure", "vibration", "diagnos", "real", "false alarm", "por qué", "porque", "síntoma", "alarma", "falla", "fallo", "falsa", "zergatik", "sintoma", "matxura"]):
            intents.add("diagnosis")
        if any(w in q for w in ["which spare", "what spare", "which part", "what part", "spare part", "kit", "ref", "skf", "which valve", "which grease", "qué repuesto", "que repuesto", "qué pieza", "que pieza", "recambio", "qué válvula", "qué grasa", "zein ordezko", "ordezko pieza", "zein balbula", "zein koipe"]):
            intents.add("spare")
        if any(w in q for w in ["step", "how to", "how do i", "procedure", "paso", "cómo", "como ", "procedimiento", "pauso", "urrats", "nola", "prozedura"]):
            intents.add("steps")

        if not intents:
            intents = {"diagnosis"}
        return intents

    def ask_copilot(self, query: str, machine_id: int = None, lang: str = "en", api_key_override: str = None):
        """Answer the technician's specific question in English ('en'), Spanish ('es'), or Basque ('eu')."""
        load_dotenv(os.path.expanduser("~/.env"), override=True)
        load_dotenv(os.path.join(self.base_dir, ".env"), override=True)

        retrieved, m_ctx = self.retrieve_context(query, machine_id=machine_id, top_k=3)
        top_chunk = retrieved[0]
        page = top_chunk["page"]
        if page not in MANUAL_KNOWLEDGE:
            page = "Page 4"

        lang_names = {"en": "English", "es": "Spanish (Castellano)", "eu": "Basque (Euskara)"}
        target_lang = lang_names.get(lang, "English")

        # 1. If a valid GEMINI_API_KEY is available, call Gemini 3.5 Flash-Lite
        api_key = (api_key_override or os.environ.get("GEMINI_API_KEY") or "").strip()
        if len(api_key) > 15:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                ctx_text = "\n\n".join([f"[{c['title']} - {c['page']}]\n{c['content']}" for c in retrieved])
                m_info = (
                    f"Selected Machine Context (from MILP Schedule): Machine #{m_ctx['machineID']}, "
                    f"Model: {m_ctx['model']}, Predicted Component at Risk: {m_ctx['pred_comp']}, "
                    f"Assigned 8h Shift: {m_ctx['shift']}, Repair Duration: {m_ctx['repair_hours']} hours, "
                    f"Preventive Cost: {m_ctx['prev_cost']} EUR, Unplanned Breakdown Cost: {m_ctx['real_reactive_cost']} EUR, "
                    f"Real Audit Outcome: {m_ctx['outcome']} (Net Savings: {m_ctx['real_net_savings']} EUR)."
                    if m_ctx else "General shop-floor query."
                )
                prompt = (
                    f"You are an expert Industrial Maintenance AI Copilot assisting a shop-floor technician.\n"
                    f"You MUST write your entire response strictly in {target_lang} (do not mix languages).\n"
                    f"Answer ONLY what the user is actually asking in a natural, direct, conversational way "
                    f"(do NOT dump the entire manual if they only ask a specific question like cost, torque, shift, or safety).\n"
                    f"Ground all technical facts in the provided Official Manual Context and Selected Machine Context, "
                    f"and cite the Page number when referencing manual specs.\n\n"
                    f"{m_info}\n\n"
                    f"Official Manual Context:\n{ctx_text}\n\n"
                    f"Technician Question ({target_lang}): {query}"
                )
                resp = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
                # Prevent Basque ordinal numbers at start of line (e.g. "24. makina") from triggering Markdown <ol start="24">
                clean_text = re.sub(r"(?m)^(\s*)(\d+)\.\s+(?=[a-zA-ZáéíóúñÁÉÍÓÚÑ]*makin)", r"\1**\2.** ", resp.text)
                return {
                    "answer": f"🤖 **[Gemini AI · RAG ({page})]**\n\n" + clean_text,
                    "retrieved_chunks": retrieved[:2],
                    "machine_context": m_ctx,
                    "engine": "Gemini 3.5 Flash-Lite + TF-IDF RAG"
                }
            except Exception:
                pass

        # 2. Intent-aware local conversational responder (fallback if offline or no API key)
        intents = self._detect_intents(query)
        kb = MANUAL_KNOWLEDGE[page]
        kb_lang = kb.get(lang, kb["en"])
        comp_kb = MANUAL_KNOWLEDGE.get(
            {"comp1": "Page 12", "comp2": "Page 27", "comp3": "Page 41", "comp4": "Page 58"}.get(
                m_ctx["pred_comp"] if m_ctx else "", page
            ),
            kb
        )
        comp_lang = comp_kb.get(lang, comp_kb["en"])

        parts = []
        if lang == "es":
            parts.append(f"🔧 **[Copiloto IA de Mantenimiento · Fuente: {top_chunk['title']} ({page})]**")
            if "safety" in intents:
                loto_steps = "\n  ".join(MANUAL_KNOWLEDGE["Page 4"]["es"]["steps"])
                parts.append(f"**Protocolo obligatorio de seguridad LOTO (Page 4):**\n  {loto_steps}")
            if "diagnosis" in intents:
                if m_ctx:
                    parts.append(
                        f"**Diagnóstico de la Máquina #{m_ctx['machineID']} (`{m_ctx['model']}`):** El modelo LightGBM detectó riesgo de fallo en **`{m_ctx['pred_comp']}`** ({comp_lang['name']}). "
                        f"Según el manual ({page}), los síntomas típicos son: {comp_lang['symptoms']}. "
                        f"*(En la auditoría real, esta intervención resultó ser: **{m_ctx['outcome']}**)*."
                    )
                else:
                    parts.append(f"**Síntomas y diagnóstico ({page}):** {kb_lang['symptoms']}.")
            if "schedule" in intents:
                if m_ctx:
                    parts.append(
                        f"**Turno y duración de la reparación:** El optimizador MILP ha asignado la **Máquina #{m_ctx['machineID']}** al turno **`{m_ctx['shift']}`**, "
                        f"y cambiar `{m_ctx['pred_comp']}` requiere **`{m_ctx['repair_hours']} horas`** de trabajo (dentro del turno de 8h)."
                    )
                else:
                    parts.append(f"**Tiempo estándar de intervención ({page}):** `{comp_kb.get('hours', 4.0)} horas`.")
            if "cost" in intents:
                if m_ctx:
                    parts.append(
                        f"**Coste y ahorro económico:** La sustitución preventiva de `{m_ctx['pred_comp']}` en la **Máquina #{m_ctx['machineID']}** cuesta **`{m_ctx['prev_cost']:.0f} EUR`**, "
                        f"frente a los **`{comp_kb.get('fail_cost', 5000)} EUR`** que cuesta si se rompe en producción "
                        f"(balance neto real de esta orden: **`{m_ctx['real_net_savings']:+.0f} EUR`**, *{m_ctx['outcome']}*)."
                    )
                else:
                    parts.append(
                        f"**Coste estimado ({page}):** `{comp_kb.get('prev_cost', 600)} EUR` en mantenimiento preventivo frente a `{comp_kb.get('fail_cost', 5000)} EUR` por avería imprevista."
                    )
            if "spare" in intents:
                parts.append(f"**Pieza de recambio oficial ({page}):** {kb_lang['spare']}.")
            if "torque" in intents:
                parts.append(f"**Par de apriete especificado ({page}):** Debes apretar a **`{kb['torque']}`** con llave dinamométrica certificada.")
            if "steps" in intents and "safety" not in intents:
                steps_txt = "\n  ".join(kb_lang["steps"])
                parts.append(f"**Procedimiento paso a paso ({page}, tras bloqueo LOTO de Page 4):**\n  {steps_txt}")

        elif lang == "eu":
            parts.append(f"🔧 **[Mantentze-lanetako IA Kopilotua · Iturria: {top_chunk['title']} ({page})]**")
            if "safety" in intents:
                loto_steps = "\n  ".join(MANUAL_KNOWLEDGE["Page 4"]["eu"]["steps"])
                parts.append(f"**Derrigorrezko LOTO segurtasun-protokoloa (Page 4):**\n  {loto_steps}")
            if "diagnosis" in intents:
                if m_ctx:
                    parts.append(
                        f"**#{m_ctx['machineID']} Makinaren Diagnostikoa (`{m_ctx['model']}`):** LightGBM modeloak matxura-arriskua detektatu du **`{m_ctx['pred_comp']}`** osagaian ({comp_lang['name']}). "
                        f"Eskuliburuaren arabera ({page}), sintoma nagusiak hauek dira: {comp_lang['symptoms']}. "
                        f"*(Benetako auditorian: **{m_ctx['outcome']}**)*."
                    )
                else:
                    parts.append(f"**Sintomak eta diagnostikoa ({page}):** {kb_lang['symptoms']}.")
            if "schedule" in intents:
                if m_ctx:
                    parts.append(
                        f"**Txanda eta konponketaren iraupena:** MILP optimizatzaileak **#{m_ctx['machineID']} Makina** **`{m_ctx['shift']}`** txandara esleitu du, "
                        f"eta `{m_ctx['pred_comp']}` aldatzeak **`{m_ctx['repair_hours']} ordu`** behar ditu (8 orduko txandaren barruan)."
                    )
                else:
                    parts.append(f"**Konponketaren iraupen estandarra ({page}):** `{comp_kb.get('hours', 4.0)} ordu`.")
            if "cost" in intents:
                if m_ctx:
                    parts.append(
                        f"**Kostua eta aurrezpen ekonomikoa:** **#{m_ctx['machineID']} Makinan** `{m_ctx['pred_comp']}` prebentzioz aldatzeak **`{m_ctx['prev_cost']:.0f} EUR`** balio du, "
                        f"eta ustekabean apurtzeak **`{comp_kb.get('fail_cost', 5000)} EUR`** "
                        f"(benetako aurrezpen garbia: **`{m_ctx['real_net_savings']:+.0f} EUR`**, *{m_ctx['outcome']}*)."
                    )
                else:
                    parts.append(
                        f"**Kostu estandarra ({page}):** `{comp_kb.get('prev_cost', 600)} EUR` prebentzioz vs `{comp_kb.get('fail_cost', 5000)} EUR` matxura larrian."
                    )
            if "spare" in intents:
                parts.append(f"**Beharrezko ordezko pieza ofiziala ({page}):** {kb_lang['spare']}.")
            if "torque" in intents:
                parts.append(f"**Estutze-pare kritikoa ({page}):** **`{kb['torque']}`**-ra estutu behar da giltza dinamometrikoarekin.")
            if "steps" in intents and "safety" not in intents:
                steps_txt = "\n  ".join(kb_lang["steps"])
                parts.append(f"**Urratsez urratseko prozedura ({page}, Page 4-ko LOTO blokeoaren ondoren):**\n  {steps_txt}")

        else:
            parts.append(f"🔧 **[Maintenance RAG Copilot · Source: {top_chunk['title']} ({page})]**")
            if "safety" in intents:
                loto_steps = "\n  ".join(MANUAL_KNOWLEDGE["Page 4"]["en"]["steps"])
                parts.append(f"**Mandatory LOTO Safety Protocol (Page 4):**\n  {loto_steps}")
            if "diagnosis" in intents:
                if m_ctx:
                    parts.append(
                        f"**Machine #{m_ctx['machineID']} (`{m_ctx['model']}`) Diagnosis:** LightGBM flagged a failure risk in **`{m_ctx['pred_comp']}`** ({comp_lang['name']}). "
                        f"According to the manual ({page}), typical symptoms are: {comp_lang['symptoms']}. "
                        f"*(Real audit outcome: **{m_ctx['outcome']}**)*."
                    )
                else:
                    parts.append(f"**Symptoms & Diagnosis ({page}):** {kb_lang['symptoms']}.")
            if "schedule" in intents:
                if m_ctx:
                    parts.append(
                        f"**Assigned Shift & Repair Duration:** The MILP optimizer scheduled **Machine #{m_ctx['machineID']}** in shift **`{m_ctx['shift']}`**, "
                        f"and replacing `{m_ctx['pred_comp']}` takes **`{m_ctx['repair_hours']} hours`** (within the 8h shift limit)."
                    )
                else:
                    parts.append(f"**Standard Repair Duration ({page}):** `{comp_kb.get('hours', 4.0)} hours`.")
            if "cost" in intents:
                if m_ctx:
                    parts.append(
                        f"**Cost & Financial Impact:** Preventive replacement of `{m_ctx['pred_comp']}` on **Machine #{m_ctx['machineID']}** costs **`{m_ctx['prev_cost']:.0f} EUR`**, "
                        f"compared to **`{comp_kb.get('fail_cost', 5000)} EUR`** for an unplanned breakdown "
                        f"(real net savings: **`{m_ctx['real_net_savings']:+.0f} EUR`**, *{m_ctx['outcome']}*)."
                    )
                else:
                    parts.append(
                        f"**Estimated Cost ({page}):** `{comp_kb.get('prev_cost', 600)} EUR` preventive vs. `{comp_kb.get('fail_cost', 5000)} EUR` unplanned breakdown."
                    )
            if "spare" in intents:
                parts.append(f"**Required Official Spare Part ({page}):** {kb_lang['spare']}.")
            if "torque" in intents:
                parts.append(f"**Specified Tightening Torque ({page}):** Tighten to **`{kb['torque']}`** using a calibrated torque wrench.")
            if "steps" in intents and "safety" not in intents:
                steps_txt = "\n  ".join(kb_lang["steps"])
                parts.append(f"**Step-by-Step Replacement Procedure ({page}, after Page 4 LOTO lockout):**\n  {steps_txt}")

        return {
            "answer": "\n\n".join(parts),
            "retrieved_chunks": retrieved[:2],
            "machine_context": m_ctx,
            "engine": "Intent-Aware RAG Responder"
        }


if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            import runpy
            _app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "app.py")
            runpy.run_path(_app_path, run_name="__main__")
    except Exception:
        pass

