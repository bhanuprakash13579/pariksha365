#!/usr/bin/env python3
"""Insert chapter-summary mermaid diagrams into GK subject files.
Run from the _build/ directory: python3 add_chapter_diagrams.py [subject ...]
  e.g.  python3 add_chapter_diagrams.py biology polity
        python3 add_chapter_diagrams.py --all
"""
import re
import sys
from pathlib import Path

NOTES = Path(__file__).resolve().parent.parent

CD = """    classDef key fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef trap fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef date fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef proc fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef root fill:#f3e8ff,stroke:#9333ea,color:#4c1d95"""


def wrap(diagram: str) -> str:
    body = diagram.rstrip() + "\n" + CD
    return (
        '\n<div class="chapter-summary">\n'
        '<div class="mermaid">\n'
        + body + "\n"
        "</div>\n"
        "</div>\n"
    )


def insert_diagrams(filepath: Path, diagrams: dict) -> int:
    """Insert diagrams after each matching chapter heading. Returns count inserted."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    count = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        stripped = line.strip()
        # Check if this line matches a chapter heading we have a diagram for
        diagram_code = diagrams.get(stripped)
        if diagram_code is not None:
            i += 1
            # Collect all lines until the next ## heading or EOF
            section: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                section.append(lines[i])
                i += 1
            result.extend(section)
            result.append(wrap(diagram_code))
            count += 1
        else:
            i += 1
    filepath.write_text("\n".join(result), encoding="utf-8")
    return count


# ─────────────────────────────────────────────────────────────────────────────
# BIOLOGY
# ─────────────────────────────────────────────────────────────────────────────
BIOLOGY = {

"## Chapter A1 — Classification of Life": """\
flowchart TD
    R["CLASSIFICATION OF LIFE"]:::root
    R --> K["5 Kingdoms — Whittaker 1969"]:::key
    R --> T["Taxonomic Ranks"]:::proc
    R --> BN["Binomial Nomenclature<br>Linnaeus 1735"]:::date
    R --> TR["TRAP: Virus not in any kingdom<br>Prions = proteins only — no DNA"]:::trap
    K --> K1["Monera: Bacteria + Cyanobacteria<br>Prokaryotes — no nucleus"]:::key
    K --> K2["Protista: Amoeba, Paramecium<br>Unicellular eukaryotes"]:::key
    K --> K3["Fungi: Chitin cell wall<br>Decomposers — Mushroom, Yeast"]:::key
    K --> K4["Plantae: Cellulose cell wall<br>Multicellular, photosynthetic"]:::key
    K --> K5["Animalia: No cell wall<br>Heterotrophic multicellular"]:::key
    T --> T1["Kingdom-Phylum-Class-Order<br>-Family-Genus-Species<br>King Philip Came Over For Great Supper"]:::proc
    BN --> BN1["Homo sapiens = Human<br>Mangifera indica = Mango<br>Panthera tigris = Tiger"]:::key""",

"## Chapter A2 — The Cell": """\
flowchart TD
    R["THE CELL"]:::root
    R --> P["Prokaryote<br>No nucleus — Bacteria, Archaea"]:::key
    R --> E["Eukaryote<br>True nucleus — Plants, Animals, Fungi"]:::key
    R --> O["KEY ORGANELLES"]:::proc
    R --> W["CELL WALL MATERIAL"]:::proc
    R --> D["CELL DIVISION"]:::proc
    O --> O1["Mitochondria: Powerhouse — ATP<br>Has own DNA"]:::key
    O --> O2["Ribosome: Protein factory<br>Present even in prokaryotes"]:::key
    O --> O3["Lysosome: Suicide bags<br>Digestive enzymes — cleanup"]:::trap
    O --> O4["Chloroplast: Photosynthesis<br>Plants only — has own DNA"]:::key
    O --> O5["Nucleus: Control centre<br>Contains DNA blueprint"]:::key
    W --> W1["Plant: Cellulose"]:::key
    W --> W2["Fungi: Chitin"]:::key
    W --> W3["Bacteria: Peptidoglycan"]:::key
    D --> D1["Mitosis: 2 daughter cells<br>Same chromosomes — growth/repair"]:::key
    D --> D2["Meiosis: 4 daughter cells<br>Half chromosomes — gametes only"]:::key""",

"## Chapter B1 — Mendelian Genetics": """\
flowchart TD
    R["MENDELIAN GENETICS"]:::root
    R --> L["Mendel's Two Laws"]:::proc
    R --> P["Pea Plant Traits"]:::key
    R --> C["Cross Ratios"]:::key
    R --> BL["Blood Groups: Co-dominance"]:::key
    L --> L1["Law of Segregation<br>Allele pairs separate during gamete formation"]:::key
    L --> L2["Law of Independent Assortment<br>Genes on diff. chromosomes sort independently"]:::key
    P --> P1["Dominant: Tall, Round, Yellow<br>Recessive: Dwarf, Wrinkled, Green"]:::key
    C --> C1["Monohybrid cross: 3:1 phenotype<br>Genotype ratio: 1:2:1"]:::key
    C --> C2["Dihybrid cross: 9:3:3:1<br>Two traits simultaneously"]:::key
    BL --> BL1["A + B = co-dominant<br>O = recessive; AB = universal recipient<br>O = universal donor"]:::key""",

"## Chapter B2 — DNA & Molecular Genetics": """\
flowchart TD
    R["DNA and MOLECULAR GENETICS"]:::root
    R --> S["DNA Structure"]:::key
    R --> C["Central Dogma"]:::proc
    R --> D["DNA vs RNA"]:::key
    R --> T["TRAP: Mismatched base pairs"]:::trap
    S --> S1["Double Helix: Watson and Crick 1953<br>Nobel Prize 1962"]:::date
    S --> S2["A-T: 2 hydrogen bonds<br>G-C: 3 hydrogen bonds"]:::key
    S --> S3["Semi-conservative replication<br>Meselson-Stahl experiment proved it"]:::key
    C --> C1["DNA --transcription-- RNA<br>RNA --translation-- Protein"]:::proc
    D --> D1["RNA: single-strand, ribose, Uracil instead of Thymine<br>3 types: mRNA, tRNA, rRNA"]:::key
    T --> T1["A pairs with T not G<br>G pairs with C not A<br>Swapping = mutation"]:::trap""",

"## Chapter B3 — Evolution": """\
flowchart TD
    R["EVOLUTION"]:::root
    R --> D["Darwin 1859"]:::date
    R --> E["Evidence for Evolution"]:::proc
    R --> CM["Chromosomal Disorders"]:::key
    R --> L["Lamarck: WRONG theory"]:::trap
    D --> D1["Origin of Species 1859<br>Natural Selection: fit survive and reproduce"]:::date
    D --> D2["Miller-Urey 1953<br>Amino acids from primordial soup"]:::date
    E --> E1["Fossil record: past life forms preserved"]:::key
    E --> E2["Homologous organs: same structure<br>different function — common ancestor<br>e.g. human arm = whale flipper = bat wing"]:::key
    E --> E3["Analogous organs: different structure<br>same function — convergent evolution<br>e.g. bat wing vs butterfly wing"]:::key
    CM --> CM1["Down Syndrome: Trisomy 21<br>47 chromosomes (extra chr 21)"]:::key
    CM --> CM2["Turner Syndrome: 45, X0 (female)<br>Klinefelter: 47, XXY (male)"]:::key
    L --> L1["Lamarck: acquired traits inherited<br>e.g. giraffe neck stretched longer<br>DISPROVED — not heritable"]:::trap""",

"## Chapter C1 — Plant Kingdom Overview": """\
flowchart TD
    R["PLANT KINGDOM OVERVIEW"]:::root
    R --> D["5 Plant Divisions"]:::proc
    R --> MC["Monocot vs Dicot Angiosperms"]:::key
    R --> TR["TRAP: Gymnosperms vs Angiosperms"]:::trap
    D --> D1["Thallophyta: Algae — in water<br>no roots/stems/leaves"]:::key
    D --> D2["Bryophyta: Mosses, Liverworts<br>First land plants — no vascular tissue"]:::key
    D --> D3["Pteridophyta: Ferns<br>Vascular — no seeds"]:::key
    D --> D4["Gymnosperms: Pine, Cycas<br>Naked seeds — no fruit"]:::key
    D --> D5["Angiosperms: LARGEST group<br>Enclosed seeds in fruit — flowers present"]:::key
    MC --> MC1["Monocot: 1 cotyledon<br>parallel veins — Rice, Wheat, Maize, Grass"]:::key
    MC --> MC2["Dicot: 2 cotyledons<br>reticulate veins — Pea, Mango, Mustard"]:::key
    TR --> TR1["Gymnosperms: seeds exposed on cone<br>Angiosperms: seeds inside fruit<br>TRAP — both have seeds"]:::trap""",

"## Chapter C2 — Photosynthesis": """\
flowchart TD
    R["PHOTOSYNTHESIS"]:::root
    R --> EQ["Core Equation"]:::key
    R --> PH["Two Phases"]:::proc
    R --> PG["Chlorophyll Pigments"]:::key
    R --> CT["C3 / C4 / CAM Plants"]:::key
    EQ --> EQ1["6CO2 + 6H2O + sunlight<br>--chlorophyll-- C6H12O6 + 6O2<br>Glucose + Oxygen released"]:::key
    PH --> PH1["Light Reactions: in THYLAKOID<br>Water split; O2 released; ATP + NADPH formed"]:::proc
    PH --> PH2["Dark Reactions (Calvin Cycle): in STROMA<br>CO2 fixed using ATP + NADPH — glucose made"]:::proc
    PG --> PG1["Chlorophyll a: primary pigment<br>Absorbs red + blue; reflects GREEN"]:::key
    PG --> PG2["Chlorophyll b, carotenoids: accessory<br>Expand light absorption range"]:::key
    CT --> CT1["C3 plants: first product = 3-PGA (3C)<br>Rice, Wheat, Oat — less efficient in heat"]:::key
    CT --> CT2["C4 plants: first product = 4C (OAA)<br>Sugarcane, Maize, Jowar — more efficient"]:::key
    CT --> CT3["CAM plants: open stomata at NIGHT<br>Cacti, Pineapple — desert adaptation"]:::key""",

"## Chapter C3 — Plant Hormones": """\
flowchart TD
    R["PLANT HORMONES"]:::root
    R --> H1["Auxin (IAA)"]:::key
    R --> H2["Gibberellin (GA)"]:::key
    R --> H3["Cytokinin"]:::key
    R --> H4["Abscisic Acid (ABA)"]:::key
    R --> H5["Ethylene"]:::key
    H1 --> H1a["Cell elongation — phototropism<br>Apical dominance (tip suppresses buds)<br>Unequal distribution causes bending toward light"]:::key
    H2 --> H2a["Stem elongation — bolting<br>Seed germination; fruit enlargement<br>Dwarfism reversed by GA treatment"]:::key
    H3 --> H3a["Cell division — delays leaf aging<br>Promotes lateral bud growth"]:::key
    H4 --> H4a["Stress hormone — closes stomata<br>Promotes dormancy of seeds/buds<br>Called abscisic = causes abscission"]:::key
    H5 --> H5a["ONLY GASEOUS plant hormone<br>Fruit ripening — used commercially<br>Promotes leaf + fruit fall"]:::key""",

"## Chapter C4 — Plant Reproduction": """\
flowchart TD
    R["PLANT REPRODUCTION"]:::root
    R --> PO["Pollination Agents"]:::proc
    R --> DF["Double Fertilization<br>Unique to Angiosperms"]:::key
    R --> FR["Fruit Types"]:::key
    R --> TR["TRAP: True vs False Fruit"]:::trap
    PO --> PO1["Anemophily: Wind<br>Light pollen — Grass, Maize, Pine"]:::key
    PO --> PO2["Entomophily: Insects<br>Colourful + fragrant flowers — Sunflower, Rose"]:::key
    PO --> PO3["Hydrophily: Water<br>Aquatic plants — Vallisneria"]:::key
    DF --> DF1["Sperm 1 + Egg = Zygote (2n) -- embryo<br>Sperm 2 + 2 Polar nuclei = Endosperm (3n)"]:::key
    DF --> DF2["Only in flowering plants (Angiosperms)<br>Gymnosperms: single fertilization"]:::key
    FR --> FR1["True fruit: from OVARY only<br>Mango, Tomato, Grape"]:::key
    TR --> TR1["False fruit: from Receptacle + Ovary<br>Apple, Strawberry, Cashew<br>TRAP: Apple = false fruit!"]:::trap""",

"## Chapter D1 — Digestive System": """\
flowchart TD
    R["DIGESTIVE SYSTEM"]:::root
    R --> PT["Digestive Path"]:::proc
    R --> EN["Key Enzymes + Sites"]:::key
    R --> AB["Absorption Sites"]:::key
    R --> TR["TRAP: Bile has NO enzyme"]:::trap
    PT --> PT1["Mouth-Oesophagus-Stomach<br>Small Intestine-Large Intestine<br>Rectum-Anus"]:::proc
    EN --> EN1["Salivary amylase: Mouth<br>Starch -- maltose"]:::key
    EN --> EN2["Pepsin: Stomach (pH 1.5-2.5)<br>Protein -- peptides; activated by HCl"]:::key
    EN --> EN3["Trypsin: Small Intestine<br>Protein -- amino acids (from pancreas)"]:::key
    EN --> EN4["Lipase: Small Intestine<br>Fat -- fatty acids + glycerol"]:::key
    AB --> AB1["Small Intestine: nutrients via villi<br>Large Intestine: water + salts"]:::key
    TR --> TR1["Bile: liver produces, gallbladder stores<br>Emulsifies fat — NO digestive enzyme<br>TRAP: students think bile digests fat"]:::trap""",

"## Chapter D2 — Respiratory System": """\
flowchart TD
    R["RESPIRATORY SYSTEM"]:::root
    R --> AP["Air Path"]:::proc
    R --> LV["Lung Volumes"]:::key
    R --> GE["Gas Exchange"]:::key
    R --> MO["Mechanism of Breathing"]:::proc
    AP --> AP1["Nasal cavity-Pharynx-Larynx<br>Trachea-Bronchi<br>Bronchioles-Alveoli"]:::proc
    LV --> LV1["Tidal Volume: 500 mL (normal breath)<br>Vital Capacity: 4500 mL<br>Total Lung Capacity: 6000 mL"]:::key
    GE --> GE1["Alveoli: ~700 million; area = 70 sq m<br>Single-cell thick; maximum diffusion"]:::key
    GE --> GE2["O2 carried by Haemoglobin (97%)<br>CO2 as bicarbonate ion (70%) in plasma"]:::key
    MO --> MO1["Inspiration: Diaphragm contracts + flattens<br>Ribs move up + out; volume increases; air enters"]:::proc
    MO --> MO2["Expiration: Diaphragm relaxes + domes<br>Ribs move down + in; air pushed out"]:::proc""",

"## Chapter D3 — Circulatory System": """\
flowchart TD
    R["CIRCULATORY SYSTEM"]:::root
    R --> DC["Double Circulation"]:::proc
    R --> HT["Heart Facts"]:::key
    R --> BG["Blood Groups"]:::date
    R --> BC["Blood Cell Lifespans"]:::key
    DC --> DC1["Pulmonary: Heart-Lungs-Heart<br>Deoxygenated blood gets oxygenated"]:::proc
    DC --> DC2["Systemic: Heart-Body-Heart<br>Oxygenated blood delivered to all organs"]:::proc
    HT --> HT1["4 chambers: RA, RV, LA, LV<br>SA Node = natural pacemaker (60-100 bpm)<br>Blood pressure: 120/80 mmHg"]:::key
    BG --> BG1["Landsteiner discovered 1901 — Nobel 1930<br>A, B, AB, O groups; Rh factor positive/negative"]:::date
    BG --> BG2["O negative: Universal DONOR<br>AB positive: Universal RECIPIENT"]:::key
    BC --> BC1["RBC: 120 days; no nucleus<br>WBC: days to years (variable)<br>Platelets: 10 days — clotting"]:::key""",

"## Chapter D4 — Nervous System": """\
flowchart TD
    R["NERVOUS SYSTEM"]:::root
    R --> DIV["Divisions"]:::proc
    R --> BR["Brain Parts + Functions"]:::key
    R --> REF["Reflex Arc"]:::proc
    R --> NT["Key Neurotransmitters"]:::key
    DIV --> DIV1["CNS: Brain + Spinal Cord"]:::key
    DIV --> DIV2["PNS: Somatic (voluntary)<br>+ Autonomic (involuntary)"]:::key
    BR --> BR1["Cerebrum: Thinking, memory<br>voluntary movement, speech"]:::key
    BR --> BR2["Cerebellum: Balance + coordination<br>posture; damaged = staggering gait"]:::key
    BR --> BR3["Medulla Oblongata: Involuntary actions<br>breathing, heart rate, swallowing"]:::key
    REF --> REF1["Receptor-Sensory neuron-Spinal cord<br>Motor neuron-Effector<br>No brain involvement — faster response"]:::proc
    NT --> NT1["Acetylcholine: muscle contraction<br>Dopamine: reward, pleasure<br>Serotonin: mood; Adrenaline: fight-or-flight"]:::key""",

"## Chapter D5 — Endocrine System": """\
flowchart TD
    R["ENDOCRINE SYSTEM"]:::root
    R --> PG["Pituitary — Master Gland"]:::key
    R --> TH["Thyroid Gland"]:::key
    R --> PN["Pancreas"]:::key
    R --> AD["Adrenal Gland"]:::key
    R --> OT["Other Glands"]:::key
    PG --> PG1["Anterior: GH, TSH, FSH, LH, ACTH, PRL<br>Posterior: ADH (water reabsorption), Oxytocin"]:::key
    TH --> TH1["Hormones T3, T4 — control BMR<br>Deficiency: Goitre (iodine deficiency)<br>Cretinism (childhood hypothyroidism)"]:::key
    TH --> TH2["Excess: Exophthalmic Goitre<br>Largest endocrine gland in body"]:::trap
    PN --> PN1["Insulin: lowers blood glucose<br>Glucagon: raises blood glucose<br>Deficiency of insulin: Diabetes Mellitus"]:::key
    AD --> AD1["Cortex: Cortisol (stress), Aldosterone (Na+)<br>Medulla: Adrenaline (fight-or-flight)"]:::key
    OT --> OT1["Pineal: Melatonin (sleep-wake cycle)<br>Testes: Testosterone; Ovaries: Estrogen"]:::key""",

"## Chapter D6 — Excretory System": """\
flowchart TD
    R["EXCRETORY SYSTEM"]:::root
    R --> OR["Organs"]:::proc
    R --> NP["Nephron — functional unit"]:::key
    R --> UR["Urine Composition"]:::key
    R --> HO["Hormonal Control"]:::key
    OR --> OR1["2 Kidneys-2 Ureters<br>1 Urinary Bladder-1 Urethra"]:::proc
    NP --> NP1["Bowman's capsule: filtration<br>Glomerulus: blood filtered here<br>PCT: selective reabsorption"]:::key
    NP --> NP2["Loop of Henle: water + salt reabsorption<br>DCT: fine-tuning; Collecting duct: final urine<br>1 million nephrons per kidney"]:::key
    UR --> UR1["95% water; 2.5% urea<br>Uric acid, creatinine, salts<br>pH 6 (slightly acidic)"]:::key
    HO --> HO1["ADH (Vasopressin): increases water reabsorption<br>Aldosterone: increases Na+ reabsorption<br>Both increase urine concentration"]:::key""",

"## Chapter D7 — Skeletal & Muscular System": """\
flowchart TD
    R["SKELETAL AND MUSCULAR SYSTEM"]:::root
    R --> BN["Bone Facts"]:::key
    R --> JT["Types of Joints"]:::key
    R --> MS["Muscle Types"]:::key
    R --> TR["TRAP: Smallest vs Largest bone"]:::trap
    BN --> BN1["Adult: 206 bones<br>Infant: 270-300 (fuse over time)<br>Longest + largest: FEMUR (thigh bone)"]:::key
    BN --> BN2["Bone composition: Calcium phosphate<br>Vitamin D needed for Ca absorption<br>Rickets = Vitamin D deficiency in children"]:::key
    JT --> JT1["Hinge joint: Elbow, Knee (one direction)<br>Ball-socket: Shoulder, Hip (all directions)<br>Pivot: Atlas-Axis in neck (rotation)"]:::key
    JT --> JT2["Gliding: Wrist/Ankle carpals<br>Immovable: Skull sutures (fixed)"]:::key
    MS --> MS1["Striated (Skeletal): Voluntary<br>Smooth (Visceral): Involuntary (gut, blood vessels)<br>Cardiac: Involuntary + striated (heart only)"]:::key
    TR --> TR1["Smallest bone: STAPES (middle ear)<br>Longest bone: FEMUR<br>TRAP: do not confuse smallest with lightest"]:::trap""",

"## Chapter E1 — Vitamins (Complete Table)": """\
flowchart TD
    R["VITAMINS"]:::root
    R --> FS["Fat-Soluble: A D E K<br>Stored in liver + fatty tissue"]:::key
    R --> WS["Water-Soluble: B complex + C<br>Not stored — must eat daily"]:::key
    FS --> A["Vitamin A (Retinol)<br>Deficiency: Night blindness<br>+ Xerophthalmia (dry eyes)"]:::key
    FS --> D["Vitamin D (Calciferol)<br>Deficiency: Rickets (children)<br>+ Osteomalacia (adults)"]:::key
    FS --> E["Vitamin E (Tocopherol)<br>Antioxidant; fertility<br>Deficiency: rare"]:::key
    FS --> K["Vitamin K (Phylloquinone)<br>Blood clotting<br>Deficiency: excessive bleeding"]:::key
    WS --> B1["Vitamin B1 (Thiamine)<br>Deficiency: BERIBERI<br>Affects nervous system + heart"]:::key
    WS --> B3["Vitamin B3 (Niacin)<br>Deficiency: PELLAGRA (3Ds:<br>Dermatitis, Diarrhoea, Dementia)"]:::key
    WS --> B12["Vitamin B12 (Cobalamin)<br>Deficiency: Pernicious Anaemia<br>Only in animal sources"]:::key
    WS --> C["Vitamin C (Ascorbic Acid)<br>Deficiency: SCURVY<br>Bleeding gums, loose teeth"]:::key""",

"## Chapter E2 — Essential Minerals": """\
flowchart TD
    R["ESSENTIAL MINERALS"]:::root
    R --> MC["Macro-minerals"]:::key
    R --> TR["Trace minerals"]:::key
    R --> TP["TRAP: Deficiency diseases"]:::trap
    MC --> Ca["Calcium (Ca)<br>Bones + teeth; blood clotting<br>Nerve + muscle function"]:::key
    MC --> Fe["Iron (Fe)<br>Haemoglobin synthesis<br>Deficiency: Iron-deficiency ANAEMIA"]:::key
    MC --> P["Phosphorus (P)<br>Bones, ATP, DNA backbone<br>Energy transfer"]:::key
    MC --> Na["Sodium (Na)<br>Fluid balance; nerve impulse<br>Excess causes hypertension"]:::key
    TR --> I["Iodine (I)<br>Thyroid hormones T3 + T4<br>Deficiency: GOITRE"]:::key
    TR --> F["Fluoride (F)<br>Tooth enamel strength<br>Excess: FLUOROSIS (mottled teeth)"]:::key
    TR --> Zn["Zinc (Zn)<br>Enzyme co-factor; immune function<br>Stores insulin in pancreas"]:::key
    TP --> TP1["Fe deficiency = Anaemia<br>I deficiency = Goitre<br>Ca deficiency = Rickets/Osteoporosis<br>F excess = Fluorosis"]:::trap""",

"## Chapter F1 — Disease Classification": """\
flowchart TD
    R["DISEASE CLASSIFICATION<br>and CAUSATIVE AGENTS"]:::root
    R --> BA["Bacterial Diseases"]:::key
    R --> VI["Viral Diseases"]:::key
    R --> PR["Protozoan Diseases"]:::key
    R --> VE["VECTORS — must know"]:::trap
    BA --> BA1["TB: Mycobacterium tuberculosis<br>Typhoid: Salmonella typhi<br>Cholera: Vibrio cholerae"]:::key
    BA --> BA2["Plague: Yersinia pestis (rat flea)<br>Leprosy: Mycobacterium leprae<br>Tetanus: Clostridium tetani"]:::key
    VI --> VI1["AIDS: HIV (retrovirus)<br>Dengue: Flavivirus (Aedes aegypti)<br>Rabies: Rhabdovirus (dog bite)"]:::key
    VI --> VI2["Smallpox: Variola — ERADICATED 1980<br>Polio: Enterovirus<br>Hepatitis B: via blood/body fluids"]:::key
    PR --> PR1["Malaria: Plasmodium<br>Vector: Anopheles FEMALE mosquito<br>4 species; P. falciparum deadliest"]:::key
    PR --> PR2["Sleeping sickness: Trypanosoma<br>Vector: Tsetse fly<br>Amoebic dysentery: Entamoeba histolytica"]:::key
    VE --> VE1["Malaria: Anopheles female<br>Dengue/Chikungunya/Zika: Aedes aegypti<br>Filaria: Culex; Plague: Rat flea<br>TRAP: Dengue vector is AEDES not Anopheles"]:::trap""",

"## Chapter F2 — Immunity": """\
flowchart TD
    R["IMMUNITY"]:::root
    R --> IN["Innate (Non-specific)"]:::key
    R --> AC["Acquired (Specific)"]:::key
    R --> VA["Vaccine Types"]:::key
    R --> PA["Active vs Passive"]:::key
    IN --> IN1["First line: Skin, mucus membranes<br>Tears (lysozyme), saliva, HCl in stomach"]:::key
    IN --> IN2["Second line: Fever, inflammation<br>Phagocytes (neutrophils, macrophages)<br>NK cells — kill infected cells"]:::key
    AC --> AC1["B lymphocytes: HUMORAL immunity<br>Produce antibodies (immunoglobulins)<br>Memory B cells for faster 2nd response"]:::key
    AC --> AC2["T lymphocytes: CELL-MEDIATED immunity<br>T-helper, T-killer, T-suppressor<br>HIV destroys T-helper (CD4) cells"]:::trap
    VA --> VA1["Live attenuated: BCG (TB), MMR, OPV (oral polio)<br>Killed/inactivated: Salk polio, Covaxin<br>Subunit/recombinant: Hepatitis B"]:::key
    VA --> VA2["Toxoid: Tetanus, Diphtheria<br>mRNA vaccine: Pfizer/Moderna COVID-19"]:::key
    PA --> PA1["Active: Body makes own antibodies<br>Long-lasting — via infection or vaccine"]:::key
    PA --> PA2["Passive: Borrowed antibodies<br>Short-lived — mother's milk, antivenom<br>Immediate effect but no memory"]:::key""",

"## Chapter G1 — Ecosystem & Energy Flow": """\
flowchart TD
    R["ECOSYSTEM and ENERGY FLOW"]:::root
    R --> TL["Trophic Levels"]:::proc
    R --> TR["10% Rule — Lindeman's Law"]:::key
    R --> EP["Ecological Pyramids"]:::key
    R --> DC["Decomposers"]:::key
    TL --> TL1["Producers (autotrophs: plants, algae)<br>-Primary consumers (herbivores)<br>-Secondary consumers (small carnivores)<br>-Tertiary consumers (top predators)"]:::proc
    TR --> TR1["Only 10% energy passes to next level<br>90% lost as heat at every step<br>Shorter food chain = more energy available"]:::key
    TR --> TR2["TRAP: Biomass pyramid can be INVERTED<br>in aquatic ecosystems<br>Energy pyramid is ALWAYS upright"]:::trap
    EP --> EP1["Pyramid of Energy: always upright<br>Pyramid of Number: can be inverted<br>e.g. 1 tree supports 1000s of insects"]:::key
    EP --> EP2["Pyramid of Biomass: inverted in ocean<br>phytoplankton (small mass) support<br>large zooplankton biomass at any time"]:::key
    DC --> DC1["Decomposers: Bacteria + Fungi<br>Break down dead organic matter<br>Return minerals to soil — nutrient cycling"]:::key""",

"## Chapter G2 — Biodiversity": """\
flowchart TD
    R["BIODIVERSITY"]:::root
    R --> HS["Hotspots — Global + India"]:::key
    R --> IU["IUCN Red List Categories"]:::key
    R --> IN["India Facts"]:::key
    R --> TR["TRAP: Hotspot criteria"]:::trap
    HS --> HS1["36 hotspots globally (2024)<br>Must have 1500+ endemic plant sp.<br>AND lost over 70% original habitat"]:::date
    HS --> HS2["India's 4 hotspots:<br>1. Eastern Himalayas<br>2. Western Ghats + Sri Lanka<br>3. Indo-Burma (NE India)<br>4. Sundaland (Andaman-Nicobar)"]:::key
    IU --> IU1["EX-Extinct; EW-Extinct in Wild<br>CR-Critically Endangered<br>EN-Endangered; VU-Vulnerable<br>NT-Near Threatened; LC-Least Concern"]:::key
    IU --> IU2["Indian examples: CR=Great Indian Bustard<br>EN=Bengal Tiger, Asiatic Lion<br>VU=Indian Rhinoceros"]:::key
    IN --> IN1["India: 17th megadiverse country globally<br>8.1% of global species in 2.4% of area<br>2nd in Asia for biodiversity"]:::key
    TR --> TR1["TRAP: Megadiverse vs Hotspot are different<br>17th megadiverse — top 17 countries<br>4 hotspots — within those 17"]:::trap""",

"## Chapter G3 — Indian Wildlife & Conservation": """\
flowchart TD
    R["INDIAN WILDLIFE and CONSERVATION"]:::root
    R --> NP["First + Key National Parks"]:::key
    R --> PR["Conservation Projects"]:::date
    R --> PA["Protected Area Network"]:::key
    R --> WP["Wildlife Protection Act 1972"]:::key
    NP --> NP1["First NP in India: Corbett NP 1936<br>(Uttarakhand; Jim Corbett established it)"]:::date
    NP --> NP2["Kaziranga NP: Assam — UNESCO WHS<br>70% of world's Indian rhinoceros"]:::key
    NP --> NP3["Gir Forest NP: Gujarat<br>ONLY wild habitat of Asiatic Lion"]:::key
    NP --> NP4["Sundarbans NP: West Bengal — UNESCO WHS<br>Largest mangrove; Bengal Tiger"]:::key
    PR --> PR1["Project Tiger: 1973 — PM Indira Gandhi<br>53 Tiger Reserves (2024); tigers: 3167"]:::date
    PR --> PR2["Project Elephant: 1992<br>32 Elephant Reserves in India"]:::date
    PA --> PA1["18 Biosphere Reserves; 12 UNESCO listed<br>First BR: Nilgiri 1986<br>Largest BR: Pachmarhi (MP)"]:::key
    PA --> PA2["106 National Parks; 565 Sanctuaries<br>Total PAs cover 5% of India's area"]:::key
    WP --> WP1["Schedule I: highest protection<br>Tiger, Elephant, Rhino, Lion, Snow Leopard<br>Hunting = up to 7 years imprisonment"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# POLITY
# ─────────────────────────────────────────────────────────────────────────────
POLITY = {

"## Chapter 1 — The Story of How India Got Its Constitution": """\
flowchart TD
    R["MAKING OF THE CONSTITUTION"]:::root
    R --> CA["Constituent Assembly"]:::date
    R --> DC["Drafting + Adoption"]:::date
    R --> SR["Sources of the Constitution"]:::key
    R --> TR["TRAP: Dates to know exactly"]:::trap
    CA --> CA1["Formed: December 1946<br>Members: 299 (final)<br>Chaired by: Dr Rajendra Prasad"]:::date
    CA --> CA2["Drafting Committee Chair:<br>Dr B.R. Ambedkar<br>'Father of the Constitution'"]:::date
    DC --> DC1["Adopted: 26 November 1949<br>'Constitution Day' / Law Day<br>Enforced: 26 January 1950 (Republic Day)"]:::date
    DC --> DC2["Original: 395 articles, 8 Schedules<br>Currently: ~470+ articles, 12 Schedules<br>Longest written constitution in the world"]:::key
    SR --> SR1["USA: Fundamental Rights, Judicial Review<br>UK: Westminster model, Parliamentary system<br>Ireland: Directive Principles (DPSP)"]:::key
    SR --> SR2["Australia: Concurrent List, joint sitting<br>Canada: Federation, residuary with Centre<br>USSR: Fundamental Duties"]:::key
    TR --> TR1["TRAP: 26 Nov = adoption, NOT enforcement<br>26 Jan = Republic Day = enforcement date<br>Constituent Assembly: 2 yrs 11 months 18 days"]:::trap""",

"## Chapter 2 — The Preamble": """\
flowchart TD
    R["THE PREAMBLE"]:::root
    R --> KW["Key Words"]:::key
    R --> AM["Words added by 42nd Amendment 1976"]:::date
    R --> JU["Judicial Status"]:::key
    R --> OB["Four Objectives"]:::proc
    KW --> KW1["WE THE PEOPLE OF INDIA<br>Sovereign: supreme authority<br>Democratic: elected government<br>Republic: elected head of state"]:::key
    AM --> AM1["'Socialist' added by 42nd Amendment 1976<br>'Secular' added by 42nd Amendment 1976<br>PM Indira Gandhi during Emergency"]:::date
    JU --> JU1["NOT justiciable: cannot be enforced in court<br>Berubari Case 1960: not part of Constitution<br>Kesavananda Bharati 1973: CAN be amended<br>BUT basic structure cannot be destroyed"]:::key
    OB --> OB1["JUSTICE: Social, Economic, Political"]:::proc
    OB --> OB2["LIBERTY: Expression, belief, faith, worship"]:::proc
    OB --> OB3["EQUALITY: Status and opportunity"]:::proc
    OB --> OB4["FRATERNITY: Dignity of individual<br>Unity and integrity of the Nation"]:::proc""",

"## Chapter 3 — Salient Features of the Indian Constitution": """\
flowchart TD
    R["SALIENT FEATURES"]:::root
    R --> S1["Structural Features"]:::key
    R --> S2["Political Features"]:::key
    R --> S3["Judicial Features"]:::key
    R --> TR["TRAP: Federal vs Unitary"]:::trap
    S1 --> S1a["Longest written constitution globally<br>Originally 395 Art; 8 Sch; 22 Parts<br>Drawn from many world constitutions"]:::key
    S1 --> S1b["Federal with UNITARY BIAS<br>Strong centre in emergencies<br>Single citizenship for all"]:::key
    S1 --> S1c["Universal Adult Franchise<br>Age 18+ (lowered from 21 by 61st Amendment 1989)"]:::date
    S2 --> S2a["Parliamentary government (Westminster)<br>PM is real executive; President = nominal<br>Cabinet collectively responsible to Lok Sabha"]:::key
    S2 --> S2b["Fundamental Rights (Part III)<br>+ Directive Principles (Part IV)<br>+ Fundamental Duties (Part IVA, Art 51A)"]:::key
    S3 --> S3a["Single integrated judiciary<br>Supreme Court at apex<br>Judicial Review: can strike down laws"]:::key
    TR --> TR1["India is QUASI-FEDERAL not fully federal<br>No dual citizenship (unlike USA)<br>Centre can override states in emergency"]:::trap""",

"## Chapter 4 — The Schedules + the Parts (the map of the Constitution)": """\
flowchart LR
    R["12 SCHEDULES"]:::root
    R --> S1["1st: 28 States + 8 UTs names"]:::key
    R --> S2["2nd: Salaries of constitutional posts"]:::key
    R --> S3["3rd: Forms of Oaths and Affirmations"]:::key
    R --> S4["4th: Seats in Rajya Sabha per state"]:::key
    R --> S5["5th: Admin of Scheduled Tribe areas"]:::key
    R --> S6["6th: Admin of NE tribal areas<br>Assam, Meghalaya, Tripura, Mizoram"]:::key
    R --> S7["7th: 3 Lists<br>Union (100), State (61), Concurrent (52)"]:::key
    R --> S8["8th: 22 Official Languages"]:::key
    R --> S9["9th: Land reform laws<br>Added by 1st Amendment 1951"]:::date
    R --> S10["10th: Anti-defection law<br>Added by 52nd Amendment 1985"]:::date
    R --> S11["11th: Panchayati Raj subjects (29)<br>Added by 73rd Amendment 1992"]:::date
    R --> S12["12th: Municipality subjects (18)<br>Added by 74th Amendment 1992"]:::date""",

"## Chapter 5 — Citizenship (Part II, Articles 5–11)": """\
flowchart TD
    R["CITIZENSHIP (Art 5-11)"]:::root
    R --> AC["Acquisition of Citizenship"]:::proc
    R --> LO["Loss of Citizenship"]:::key
    R --> OV["Overseas Indians"]:::key
    R --> TR["TRAP: No Dual Citizenship"]:::trap
    AC --> AC1["By BIRTH: born in India before 26 Jan 1950<br>OR at least one parent a citizen + born after 1987"]:::key
    AC --> AC2["By DESCENT: parent citizen + born abroad<br>By REGISTRATION: living in India 7+ years<br>By NATURALISATION: 11+ years residence"]:::key
    LO --> LO1["Renunciation: voluntary giving up (Form)<br>Termination: obtaining foreign citizenship<br>Deprivation: Govt cancels — fraud/disloyalty"]:::key
    OV --> OV1["NRI: Non-Resident Indian (Indian citizen abroad)<br>PIO: Person of Indian Origin (foreign citizen)<br>OCI: Overseas Citizen of India — dual citizenship-like<br>but no political rights (can't vote/hold office)"]:::key
    TR --> TR1["India has SINGLE citizenship only<br>No dual citizenship allowed<br>OCI is NOT citizenship — it is a status"]:::trap""",

"## Chapter 6 — Fundamental Rights (Articles 12–35)": """\
flowchart TD
    R["FUNDAMENTAL RIGHTS<br>Part III, Art 12-35"]:::root
    R --> SX["6 Fundamental Rights"]:::key
    R --> WR["5 Writs — Art 32 and Art 226"]:::key
    R --> AM["Key Amendments"]:::date
    R --> TR["TRAP: 7th FR removed"]:::trap
    SX --> SX1["Art 14: Equality before law<br>Art 15: No discrimination (religion/race/caste/sex)<br>Art 17: Untouchability abolished"]:::key
    SX --> SX2["Art 19: 6 freedoms (speech, assemble, move...)<br>Art 21: Right to Life + Personal Liberty<br>Art 21A: Right to Education (86th Amend 2002)"]:::key
    SX --> SX3["Art 25-28: Freedom of Religion<br>Art 29-30: Cultural + Educational Rights<br>Art 32: Right to Constitutional Remedies"]:::key
    WR --> WR1["Habeas Corpus: produce the body (illegal detention)<br>Mandamus: command to perform duty<br>Prohibition: stop lower court overstepping"]:::key
    WR --> WR2["Certiorari: quash lower court order<br>Quo Warranto: by what authority (challenge post)<br>SC issues all 5; HC issues all 5 + extra"]:::key
    AM --> AM1["Art 32: 'Heart and Soul' — Dr Ambedkar<br>Art 21: expanded by courts to include privacy,<br>livelihood, dignity, education"]:::key
    TR --> TR1["7th FR = Right to Property (Art 31)<br>Removed by 44th Amendment 1978<br>Now legal right under Art 300A only"]:::trap""",

"## Chapter 7 — Directive Principles of State Policy (Articles 36–51)": """\
flowchart TD
    R["DIRECTIVE PRINCIPLES<br>Part IV, Art 36-51"]:::root
    R --> BA["Basic Nature"]:::key
    R --> KA["Key Articles to Know"]:::key
    R --> TR["TRAP: DPSP vs FR conflict"]:::trap
    R --> SO["Source"]:::date
    BA --> BA1["NOT justiciable: courts cannot enforce them<br>Moral obligations on the state<br>But have constitutional importance"]:::key
    BA --> BA2["Cannot be struck down for violating FRs<br>Art 31C (42nd Amend): laws for Art 39(b)(c)<br>cannot be challenged on FR grounds"]:::key
    KA --> KA1["Art 39: Equal pay for equal work<br>Art 40: Panchayati Raj — village panchayats<br>Art 44: Uniform Civil Code (UCC)"]:::key
    KA --> KA2["Art 45: Early childhood care (0-6 yrs)<br>Art 48A: Protect environment + wildlife<br>Art 50: Separate judiciary from executive"]:::key
    TR --> TR1["TRAP: DPSP 'supplements' FRs, doesn't override<br>Kesavananda 1973: Both FRs + DPSP have equal value<br>Minerva Mills 1980: Balance is basic structure"]:::trap
    SO --> SO1["Inspired by: Irish Constitution<br>Spanish Constitution also similar<br>Both influenced by socialist + welfare principles"]:::date""",

"## Chapter 8 — Fundamental Duties (Article 51-A, Part IV-A)": """\
flowchart TD
    R["FUNDAMENTAL DUTIES<br>Art 51A, Part IV-A"]:::root
    R --> AD["Addition History"]:::date
    R --> DU["Key Duties (11 total)"]:::key
    R --> NA["Nature of Duties"]:::key
    R --> TR["TRAP: Not justiciable"]:::trap
    AD --> AD1["Added by 42nd Amendment 1976<br>Swaran Singh Committee recommended<br>Based on: USSR Constitution"]:::date
    AD --> AD2["Originally 10 duties (1976)<br>11th added by 86th Amendment 2002:<br>Duty of parents to provide education<br>to children aged 6-14 years"]:::date
    DU --> DU1["Abide by Constitution + respect ideals<br>Defend country if called upon<br>Promote harmony and brotherhood"]:::key
    DU --> DU2["Protect environment, forests, wildlife<br>Develop scientific temper<br>Safeguard public property"]:::key
    NA --> NA1["Moral obligations — NOT enforceable<br>No penalty for non-compliance<br>Guide citizens in their conduct"]:::key
    TR --> TR1["TRAP: FRs are justiciable; FDs are NOT<br>DPSPs are NOT justiciable; FDs are NOT<br>Only Fundamental RIGHTS are enforceable in court"]:::trap""",

"## Chapter 9 — FRs + DPSPs + FDs — The Big Picture": """\
flowchart TD
    R["FRs + DPSPs + FDs<br>THE BIG PICTURE"]:::root
    R --> CM["Comparison Matrix"]:::key
    R --> LC["Landmark Cases"]:::date
    R --> AM["Constitutional Amendments"]:::date
    R --> TR["TRAP: Justiciability"]:::trap
    CM --> CM1["Fundamental Rights: JUSTICIABLE<br>Directive Principles: NOT justiciable<br>Fundamental Duties: NOT justiciable"]:::key
    CM --> CM2["FRs: protect individuals from state<br>DPSPs: guide state towards welfare<br>FDs: obligations of citizens"]:::key
    LC --> LC1["Kesavananda Bharati 1973: 13-judge bench<br>Parliament cannot destroy BASIC STRUCTURE<br>Established 'basic structure doctrine'"]:::date
    LC --> LC2["Minerva Mills 1980: Balance of FRs + DPSPs<br>is itself part of basic structure<br>Cannot prioritise one completely over other"]:::date
    LC --> LC3["Maneka Gandhi 1978: Art 21 expanded<br>Procedure must be 'just fair and reasonable'<br>Not just 'procedure established by law'"]:::date
    AM --> AM1["42nd Amendment 1976 (Mini Constitution):<br>Added Socialist + Secular to Preamble<br>+ 10 FDs + expanded DPSPs"]:::date
    TR --> TR1["TRAP: Preamble is NOT justiciable<br>TRAP: Right to Property moved from FR to<br>legal right (Art 300A) by 44th Amendment"]:::trap""",
}


# ─────────────────────────────────────────────────────────────────────────────
# SUBJECT → FILE + DIAGRAMS MAPPING
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# GEOGRAPHY
# ─────────────────────────────────────────────────────────────────────────────
GEOGRAPHY = {

"## Chapter 1 — The Universe + the Solar System": """\
flowchart TD
    R["UNIVERSE AND SOLAR SYSTEM"]:::root
    R --> U["Universe Facts"]:::date
    R --> P["Planets — 8 in order"]:::key
    R --> EX["Extremes"]:::key
    R --> TR["TRAP: Hottest planet"]:::trap
    U --> U1["Big Bang: 13.8 billion years ago<br>Solar System: 4.6 billion years old<br>Milky Way: spiral galaxy; 100,000 light years wide"]:::date
    U --> U2["Sun: G-type main-sequence star<br>Distance from Earth: 150 million km = 1 AU<br>Light travel: 8 min 20 sec"]:::key
    P --> P1["Mercury-Venus-Earth-Mars (inner)<br>Jupiter-Saturn-Uranus-Neptune (outer)<br>Largest: Jupiter; Smallest: Mercury"]:::key
    P --> P2["Brightest in sky: Venus<br>Red planet: Mars (iron oxide)<br>Blue planet: Earth (water)"]:::key
    EX --> EX1["Nearest star: Proxima Centauri (4.2 light-years)<br>Moon distance: 384,400 km; light: 1.28 sec<br>Earth's satellite: Moon"]:::key
    TR --> TR1["TRAP: Hottest planet = VENUS not Mercury<br>Reason: Venus has thick CO2 atmosphere<br>greenhouse effect traps heat (460 degrees C)"]:::trap""",

"## Chapter 2 — Earth's Interior + Rocks": """\
flowchart TD
    R["EARTH'S INTERIOR AND ROCKS"]:::root
    R --> L["3 Layers"]:::proc
    R --> D["Discontinuities"]:::key
    R --> RK["Rock Types"]:::key
    R --> TR["TRAP: Which rock has fossils?"]:::trap
    L --> L1["Crust: 5-70 km thick<br>Oceanic = basalt (SIMA)<br>Continental = granite (SIAL)"]:::key
    L --> L2["Mantle: 2900 km thick<br>Asthenosphere: semi-molten; tectonic plates ride on it<br>Lithosphere = Crust + upper Mantle"]:::key
    L --> L3["Core: Outer core = liquid iron-nickel<br>Inner core = solid iron-nickel<br>Source of Earth's magnetic field"]:::key
    D --> D1["Mohorovicic (Moho): Crust-Mantle boundary<br>Gutenberg: Mantle-Outer Core<br>Lehmann: Outer-Inner Core"]:::key
    RK --> RK1["Igneous: from magma<br>Intrusive: granite (slow-cool, coarse)<br>Extrusive: basalt (fast-cool, fine)"]:::key
    RK --> RK2["Sedimentary: layers of sediment<br>Limestone, sandstone, shale<br>FOSSILS found ONLY here"]:::key
    RK --> RK3["Metamorphic: heat + pressure transform existing rock<br>Limestone-Marble; Shale-Slate<br>Coal-Graphite; Graphite-Diamond"]:::key
    TR --> TR1["TRAP: Fossils in SEDIMENTARY rocks ONLY<br>Not in igneous (formed from magma)<br>Not in metamorphic (heat destroys fossils)"]:::trap""",

"## Chapter 3 — Plate Tectonics, Earthquakes, Volcanoes": """\
flowchart TD
    R["PLATE TECTONICS"]:::root
    R --> CT["Continental Drift Theory"]:::date
    R --> PB["Plate Boundaries"]:::proc
    R --> EQ["Earthquakes"]:::key
    R --> VO["Volcanoes"]:::key
    CT --> CT1["Alfred Wegener 1915: 'Continental Drift'<br>Evidence: Jigsaw fit of continents<br>Glossopteris fossil on S. America + Africa"]:::date
    PB --> PB1["Divergent: plates move apart<br>Mid-Atlantic Ridge; new crust formed<br>Rift valleys + undersea mountains"]:::proc
    PB --> PB2["Convergent: plates collide<br>Ocean-ocean: island arc + trench<br>Ocean-continent: subduction + trench (deepest)"]:::proc
    PB --> PB3["Transform: plates slide past each other<br>San Andreas Fault, California<br>Earthquakes — no volcanic activity"]:::proc
    EQ --> EQ1["Richter scale: logarithmic (1-9+)<br>Moment Magnitude Scale (MMS): modern standard<br>Focus = underground point; Epicentre = surface above"]:::key
    EQ --> EQ2["Seismograph measures earthquake waves<br>P-waves (primary), S-waves (secondary), Surface waves<br>S-waves cannot pass through liquid outer core"]:::key
    VO --> VO1["Pacific Ring of Fire: 75% of world's volcanoes<br>+ 90% of world's earthquakes<br>Surrounds Pacific Ocean"]:::key
    VO --> VO2["Mariana Trench: deepest point on Earth<br>11,034 m in Pacific Ocean<br>Formed by subduction zone"]:::date""",

"## Chapter 4 — Atmosphere + Climate": """\
flowchart TD
    R["ATMOSPHERE AND CLIMATE"]:::root
    R --> L["5 Atmospheric Layers"]:::key
    R --> TR["TRAP: Temperature changes per layer"]:::trap
    R --> OZ["Ozone Layer"]:::key
    L --> L1["Troposphere: 0-16 km<br>Weather occurs here<br>Temp DECREASES with altitude (-6.5 C per km)"]:::key
    L --> L2["Stratosphere: 16-50 km<br>Ozone layer (15-35 km) absorbs UV<br>Temp INCREASES with altitude — stable, no weather"]:::key
    L --> L3["Mesosphere: 50-80 km<br>Meteors burn here<br>Temp DECREASES — coldest layer"]:::key
    L --> L4["Thermosphere: 80-600 km<br>Aurora borealis and aurora australis<br>ISS orbits here (400 km); very hot but low density"]:::key
    L --> L5["Exosphere: 600+ km<br>Satellites; merges into outer space<br>Mostly hydrogen + helium"]:::key
    OZ --> OZ1["Ozone = O3; protects from UV-B radiation<br>CFC (chlorofluorocarbon) destroys ozone<br>Montreal Protocol 1987: phase out CFCs"]:::key
    OZ --> OZ2["Ozone hole: over Antarctica<br>Discovered 1985; still healing<br>Freon (CFC-12) was main culprit"]:::key
    TR --> TR1["TRAP: Remember alternating temp pattern<br>Troposphere: decreases; Stratosphere: increases<br>Mesosphere: decreases; Thermosphere: increases"]:::trap""",

"## Chapter 5 — Oceans + Currents + Tides": """\
flowchart TD
    R["OCEANS, CURRENTS, TIDES"]:::root
    R --> OC["5 Oceans"]:::key
    R --> CU["Ocean Currents"]:::key
    R --> TI["Tides"]:::key
    R --> TR["TRAP: Spring vs Neap tides"]:::trap
    OC --> OC1["Pacific: largest + deepest<br>Atlantic: 2nd largest; S-shaped<br>Indian: 3rd; surrounds India"]:::key
    OC --> OC2["Deepest point: Mariana Trench 11,034 m<br>Challenger Deep — Pacific Ocean"]:::date
    CU --> CU1["WARM currents: move toward poles<br>Gulf Stream: N Atlantic; warms W Europe<br>Kuroshio: N Pacific"]:::key
    CU --> CU2["COLD currents: move toward equator<br>Labrador: N Atlantic (cold fog on Newfoundland)<br>Peru/Humboldt: S Pacific (makes Chile coast dry)"]:::key
    CU --> CU3["TRAP: California current = COLD<br>Gulf Stream = WARM<br>Benguela current (off W Africa) = COLD"]:::trap
    TI --> TI1["Caused by: Moon's gravity (mainly) + Sun<br>Spring tides: Sun-Earth-Moon aligned<br>Full Moon or New Moon — HIGHEST tides"]:::key
    TI --> TI2["Neap tides: Moon at right angle to Sun-Earth<br>Quarter Moon phase — LOWEST tidal range<br>2 high tides + 2 low tides per day (semidiurnal)"]:::key
    TR --> TR1["TRAP: Spring tide = NOT spring season<br>Spring = Latin 'springing up' (bigger tides)<br>Neap = Old English 'scanty' (smaller)"]:::trap""",

"## Chapter 6 — India: Location + Extent + Borders": """\
flowchart TD
    R["INDIA: LOCATION AND BORDERS"]:::root
    R --> LL["Latitudes + Longitudes"]:::key
    R --> BO["Neighbouring Countries"]:::key
    R --> EX["Extremes of India"]:::key
    R --> TR["TRAP: Standard Time Meridian"]:::trap
    LL --> LL1["Latitude: 8 degree 4N to 37 degree 6N<br>Longitude: 68 degree 7E to 97 degree 25E<br>Tropic of Cancer (23.5N) through 8 states"]:::key
    LL --> LL2["States on Tropic of Cancer:<br>Raj, Gujarat, MP, Chhattisgarh, Jharkhand<br>WB, Tripura, Mizoram (8 states)"]:::key
    BO --> BO1["Land borders (7 countries):<br>Pakistan, Afghanistan, China, Nepal<br>Bhutan, Bangladesh, Myanmar"]:::key
    BO --> BO2["Total land border: 15,106 km<br>Total coastline: 7,516 km<br>Maritime border: Sri Lanka + Maldives"]:::key
    EX --> EX1["Northernmost: Indira Col (Ladakh)<br>Southernmost: Indira Point (Great Nicobar)<br>Easternmost: Kibithu (Arunachal Pradesh)"]:::key
    EX --> EX2["Westernmost: Ghuar Mota (Gujarat)<br>India-Pakistan sea boundary: Sir Creek<br>India-China boundary: McMahon Line (NE) + LAC"]:::key
    TR --> TR1["India's Standard Time: IST = UTC+5:30<br>Based on 82.5 degree E longitude (through Mirzapur, UP)<br>TRAP: IST is 30 min offset — not a full hour"]:::trap""",

"## Chapter 7 — Physiography of India": """\
flowchart TD
    R["PHYSIOGRAPHY OF INDIA"]:::root
    R --> HM["Himalayas"]:::key
    R --> NP["Northern Plains"]:::key
    R --> PP["Peninsular Plateau"]:::key
    R --> CG["Coastal Plains + Ghats"]:::key
    HM --> HM1["3 parallel ranges:<br>Himadri (Great Himalaya) — highest peaks<br>Himachal (Middle) — hill stations<br>Shiwaliks (Outer) — newest; terai"]:::key
    HM --> HM2["Highest peak in India: K2 (8611 m, PoK)<br>Mt Everest (8848 m) in Nepal<br>Youngest fold mountains — still rising"]:::key
    NP --> NP1["Formed by alluvial deposits of Himalayan rivers<br>Most fertile plain in world<br>Bhangar (old alluvium) vs Khadar (new flood plain)"]:::key
    PP --> PP1["Ancient (1.5 billion years old)<br>Deccan Trap: basalt rock from volcanic eruptions<br>Average height 600-900 m"]:::key
    PP --> PP2["Highest peak on Deccan: Anamudi 2695 m<br>(Western Ghats, Kerala)<br>Highest in Eastern Ghats: Mahendragiri"]:::key
    CG --> CG1["Western Ghats (Sahyadri): continuous range<br>Biodiversity hotspot; rainfall interceptor<br>Palghat Gap: only major break"]:::key
    CG --> CG2["Eastern Ghats: discontinuous hills<br>Coromandel Coast (E): smooth + straight<br>Malabar Coast (W): lagoons + backwaters (Kerala)"]:::key""",

"## Chapter 8 — Rivers of India": """\
flowchart TD
    R["RIVERS OF INDIA"]:::root
    R --> HS["2 River Systems"]:::proc
    R --> GN["Ganga + Brahmaputra"]:::key
    R --> PN["Peninsular Rivers"]:::key
    R --> TR["TRAP: West-flowing peninsular rivers"]:::trap
    HS --> HS1["Himalayan rivers: PERENNIAL<br>Fed by snow melt + monsoon rain<br>Deep gorges; young; still cutting"]:::key
    HS --> HS2["Peninsular rivers: SEASONAL<br>Depend only on monsoon<br>Old; shallow; can only flow in rainy season"]:::key
    GN --> GN1["Ganga: longest in India (2525 km)<br>Source: Gangotri glacier<br>Flows: E into Bay of Bengal"]:::key
    GN --> GN2["Brahmaputra: originates in Tibet as Tsangpo<br>Enters India through Arunachal<br>Largest river island: Majuli (Assam)"]:::key
    PN --> PN1["East-flowing into Bay of Bengal:<br>Mahanadi, Godavari (Dakshin Ganga)<br>Krishna, Kaveri (Dakshina Ganga)"]:::key
    PN --> PN2["Longest peninsular river: Godavari (1465 km)<br>Kaveri dispute: Karnataka vs Tamil Nadu<br>Sacred rivers: Ganga, Yamuna, Godavari, Kaveri"]:::key
    TR --> TR1["TRAP: Narmada + Tapi flow WESTWARD<br>Both flow through rift valleys (structural faults)<br>Drain into Arabian Sea not Bay of Bengal"]:::trap""",

"## Chapter 9 — Indian Climate + Monsoon": """\
flowchart TD
    R["INDIAN CLIMATE AND MONSOON"]:::root
    R --> SE["4 Seasons"]:::proc
    R --> MO["Monsoon Mechanism"]:::key
    R --> RF["Rainfall Extremes"]:::key
    R --> EL["El Nino and La Nina"]:::key
    SE --> SE1["Winter: Dec-Feb (NE trade winds blow offshore)<br>Summer/Pre-monsoon: Mar-May (hot dry)<br>SW Monsoon: Jun-Sep (wet)<br>Retreating Monsoon: Oct-Nov (NE monsoon)"]:::proc
    MO --> MO1["SW Monsoon arrives Kerala by June 1<br>2 branches: Arabian Sea + Bay of Bengal<br>Low pressure over Thar Desert pulls monsoon in"]:::key
    MO --> MO2["Bay of Bengal branch: hits NE India first<br>Arabian Sea branch: hits Kerala coast first<br>Both branches meet over North India"]:::key
    RF --> RF1["Highest rainfall: Mawsynram, Meghalaya<br>11,000+ mm/year; also Cherrapunji nearby<br>Orographic rainfall — Khasi hills face monsoon"]:::key
    RF --> RF2["Lowest rainfall: Jaisalmer, Rajasthan<br>Less than 100 mm/year<br>Rain shadow zone + far from sea"]:::key
    EL --> EL1["El Nino: warm water in E Pacific<br>Weakens Indian Ocean temp gradient<br>Result: WEAK or LATE Indian monsoon"]:::key
    EL --> EL2["La Nina: cool water in E Pacific<br>Strengthens monsoon circulation<br>Result: STRONG above-normal monsoon"]:::key""",

"## Chapter 10 — Soils of India": """\
flowchart TD
    R["SOILS OF INDIA"]:::root
    R --> A["Alluvial Soil"]:::key
    R --> B["Black Soil (Regur)"]:::key
    R --> C["Red Soil"]:::key
    R --> D["Laterite Soil"]:::key
    R --> TR["TRAP: Soil-crop associations"]:::trap
    A --> A1["Most widespread: Indo-Gangetic plains<br>Khadar (new alluvium, fertile)<br>Bhangar (old alluvium, less fertile)"]:::key
    A --> A2["Rich in potash; poor in nitrogen<br>Best for: Rice, Wheat, Sugarcane<br>Found in: Punjab, UP, Bihar, WB, Coastal deltas"]:::key
    B --> B1["Black cotton soil = Regur = Tropical Chernozem<br>Formed from Deccan Trap basalt<br>High clay content — swells with moisture"]:::key
    B --> B2["BEST for: Cotton (Maharashtra, MP, Gujarat)<br>Also: sugarcane, wheat, linseed<br>Black colour from titanite iron compound"]:::key
    C --> C1["Formed from weathering of old crystalline rocks<br>Red due to presence of iron oxide<br>Deficient in: nitrogen, phosphorus, humus"]:::key
    C --> C2["Found in: Telangana, Andhra, TN, Odisha, Jharkhand<br>Best for: groundnut, millets, cotton"]:::key
    D --> D1["Formed by intense leaching (heavy rainfall)<br>Iron + aluminium oxides remain; silica leached out<br>Hard when dry; found in WG, Karnataka, Kerala"]:::key
    TR --> TR1["TRAP: Cotton = Black soil (NOT red soil)<br>Rice = Alluvial soil (NOT black)<br>Tea/Coffee = Laterite + Red soil (hill areas)"]:::trap""",

"## Chapter 11 — Population": """\
flowchart TD
    R["POPULATION OF INDIA"]:::root
    R --> C["Census 2011 Key Figures"]:::date
    R --> ST["State Rankings"]:::key
    R --> LI["Literacy"]:::key
    R --> TR["TRAP: Density — state vs UT"]:::trap
    C --> C1["Total population: 121.1 crore (2011)<br>2nd most populous after China<br>Population density: 382 per sq km"]:::date
    C --> C2["Sex ratio: 943 females per 1000 males<br>Decadal growth rate: 17.7% (2001-2011)<br>Urban population: 31.2%"]:::key
    ST --> ST1["Most populous state: Uttar Pradesh<br>Least populous state: Sikkim<br>Highest density: Bihar (1106/sq km)"]:::key
    ST --> ST2["Lowest density state: Arunachal Pradesh (17/sq km)<br>TRAP: Highest density UT = Delhi<br>Highest density overall: Delhi (11,320/sq km)"]:::trap
    LI --> LI1["Overall literacy rate: 74.04% (2011)<br>Male: 82.14%; Female: 65.46%<br>Highest literacy state: Kerala (93.9%)"]:::key
    LI --> LI2["Lowest literacy state: Bihar (61.8%)<br>Highest female literacy: Kerala<br>Lowest female literacy: Rajasthan"]:::key
    TR --> TR1["TRAP: Most dense state = Bihar<br>Most dense overall = Delhi (UT)<br>Smallest state = Goa; Smallest UT = Lakshadweep"]:::trap""",

"## Chapter 12 — Agriculture": """\
flowchart TD
    R["AGRICULTURE IN INDIA"]:::root
    R --> KH["Kharif vs Rabi"]:::key
    R --> CR["Key Crops + States"]:::key
    R --> RE["Agricultural Revolutions"]:::date
    R --> TR["TRAP: India's top productions"]:::trap
    KH --> KH1["Kharif: sown in June, harvested Oct<br>Monsoon crops: Rice, Jute, Cotton<br>Groundnut, Soyabean, Bajra, Maize"]:::key
    KH --> KH2["Rabi: sown in Nov, harvested Mar-Apr<br>Winter crops: Wheat, Barley, Mustard<br>Gram (chickpea), Peas, Linseed"]:::key
    KH --> KH3["Zaid: summer between rabi and kharif<br>Vegetables: cucumber, melon, watermelon<br>Short duration, needs irrigation"]:::key
    CR --> CR1["Rice: WB, UP, Andhra, Punjab (paddy belt)<br>Wheat: Punjab, Haryana, UP (bread basket)<br>Sugarcane: UP (largest), Maharashtra, Karnataka"]:::key
    CR --> CR2["Cotton: Maharashtra, Gujarat, Andhra<br>Jute: WB (90% of India's jute); tea: Assam<br>Coffee: Karnataka (70%); Rubber: Kerala"]:::key
    RE --> RE1["Green Revolution: 1960s; Norman Borlaug (Father)<br>M.S. Swaminathan (India); HYV seeds<br>Punjab + Haryana = wheat bowl of India"]:::date
    RE --> RE2["White Revolution (Milk): Operation Flood<br>Verghese Kurien: father of White Revolution<br>AMUL co-operative model; India = world's top milk producer"]:::date
    TR --> TR1["TRAP: India LARGEST producer of:<br>Milk, Spices, Jute, Ginger, Chickpea, Banana<br>2ND largest: Rice, Wheat, Sugarcane, Fruits, Vegetables"]:::trap""",

"## Chapter 13 — Minerals + Energy": """\
flowchart TD
    R["MINERALS AND ENERGY"]:::root
    R --> CO["Coal"]:::key
    R --> IR["Iron + Steel Metals"]:::key
    R --> NU["Nuclear Minerals"]:::key
    R --> OT["Other Key Minerals"]:::key
    CO --> CO1["India: 4th largest coal reserves globally<br>Types: Anthracite (best) > Bituminous > Lignite > Peat<br>95% coal in Gondwana rock formations"]:::key
    CO --> CO2["Major coal states: Jharkhand (largest reserves)<br>Chhattisgarh, Odisha, WB, Madhya Pradesh<br>Singrauli, Raniganj, Jharia = major coalfields"]:::key
    IR --> IR1["Iron ore: Jharkhand, Odisha, Chhattisgarh<br>Hematite (Fe2O3) = best grade<br>India exports iron ore to Japan + Korea"]:::key
    IR --> IR2["Bauxite (aluminium ore): Odisha (Kalahandi)<br>Manganese: Odisha, Maharashtra<br>Copper: Rajasthan (Khetri = copper city)"]:::key
    NU --> NU1["Uranium: Jaduguda, Jharkhand (only mine)<br>Thorium: Monazite sands, Kerala-Tamil Nadu coast<br>India = world's largest thorium reserves"]:::key
    OT --> OT1["Mica: Jharkhand (Kodarma = mica capital)<br>India was world's largest mica exporter<br>Petroleum: Mumbai High offshore (largest)"]:::key""",

"## Chapter 14 — Transport + Communication": """\
flowchart TD
    R["TRANSPORT AND COMMUNICATION"]:::root
    R --> RD["Roads"]:::key
    R --> RL["Railways"]:::key
    R --> WW["Waterways"]:::key
    R --> PT["Ports"]:::key
    RD --> RD1["Longest NH: NH-44 Srinagar to Kanyakumari<br>3,745 km; passes through 11 states<br>Old name: NH-7 (Varanasi-Kanyakumari)"]:::key
    RD --> RD2["Golden Quadrilateral: NH connecting<br>Delhi-Mumbai-Chennai-Kolkata (5846 km)<br>NHDP: National Highway Development Project"]:::key
    RL --> RL1["Indian Railways: 4th largest network globally<br>After USA, Russia, China<br>HQ: Rail Bhavan, New Delhi"]:::key
    RL --> RL2["Broadest gauge (1676 mm): Broad gauge<br>Meter gauge (1000 mm); Narrow gauge (762/610 mm)<br>First railway: 1853 (Mumbai to Thane, 34 km)"]:::date
    WW --> WW1["NW-1: Ganga (Allahabad to Haldia, 1620 km)<br>NW-2: Brahmaputra (Sadiya to Dhubri, 891 km)<br>NW-3: West Coast (Kottapuram to Kollam, 205 km)"]:::key
    PT --> PT1["Major ports (12 major + 200 minor)<br>Busiest: Mumbai (JNPT = Jawaharlal Nehru Port)<br>Oldest: Kolkata (Syama Prasad Mookerjee)"]:::key""",

"## Chapter 15 — Continents + Countries + Oceans (key facts)": """\
flowchart TD
    R["CONTINENTS, COUNTRIES, OCEANS"]:::root
    R --> CT["7 Continents by Size"]:::key
    R --> CO["Countries — Superlatives"]:::key
    R --> RV["Rivers + Mountains"]:::key
    R --> LK["Lakes"]:::key
    CT --> CT1["Asia (largest: 44.6M km2)<br>Africa (2nd: 30.3M km2)<br>North America (3rd), South America (4th)"]:::key
    CT --> CT2["Antarctica (5th: 14M km2; covered in ice)<br>Europe (6th), Australia (smallest: 7.7M km2)<br>TRAP: Australia = smallest continent not country"]:::trap
    CO --> CO1["Largest country: Russia (17.1M km2)<br>2nd: Canada; 3rd: USA; 4th: China; 5th: Brazil<br>India: 7th largest country"]:::key
    CO --> CO2["Smallest country: Vatican City (0.44 sq km)<br>Most populous: China then India<br>Densest: Monaco; then Singapore"]:::key
    RV --> RV1["Longest river: Nile (6650 km, Africa)<br>2nd: Amazon (6400 km, S America)<br>Highest mountain: Mt Everest (8848.86 m)"]:::key
    LK --> LK1["Largest lake: Caspian Sea (saline)<br>Largest freshwater: Lake Superior (N America)<br>Deepest lake: Baikal (Russia, 1642 m)"]:::key""",

"## Chapter 16 — Biomes (Natural Vegetation)": """\
flowchart TD
    R["BIOMES AND NATURAL VEGETATION"]:::root
    R --> TR["Tropical Forests"]:::key
    R --> GR["Grasslands"]:::key
    R --> TA["Taiga and Tundra"]:::key
    R --> DE["Deserts"]:::key
    TR --> TR1["Tropical Rainforest: near equator<br>Amazon (lungs of Earth), Congo, SE Asia<br>Highest biodiversity; evergreen; > 2000 mm rain"]:::key
    TR --> TR2["Tropical Deciduous (Monsoon): India's main forest<br>Sal, teak, bamboo trees; shed leaves in dry season<br>India = major teak exporter"]:::key
    GR --> GR1["Tropical savanna: Africa (Serengeti)<br>Scattered trees + grassland; seasonal rainfall<br>Wildlife: lions, elephants, wildebeest"]:::key
    GR --> GR2["Temperate grasslands:<br>Prairies (N America), Steppes (Eurasia)<br>Pampas (S America), Veld (S Africa), Downs (Australia)"]:::key
    TA --> TA1["Taiga/Boreal: largest terrestrial biome<br>Coniferous: pine, spruce, fir<br>Russia + Canada; cold; acidic soil"]:::key
    TA --> TA2["Tundra: Arctic zone; permafrost (frozen soil)<br>No trees; only mosses, lichens, sedges<br>Brief summer; reindeer, polar bear"]:::key
    DE --> DE1["Hot desert: Sahara = largest hot desert<br>Cold desert: Antarctica = largest cold desert<br>Thar = Great Indian Desert (Rajasthan)"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────────────────────
HISTORY = {

"## Chapter 1 — Prehistory + Stone Ages": """\
flowchart TD
    R["PREHISTORY AND STONE AGES"]:::root
    R --> ST["Stone Age Divisions"]:::key
    R --> SN["Key Sites in India"]:::date
    R --> TR["TRAP: Which age did farming begin?"]:::trap
    ST --> ST1["Palaeolithic (Old Stone Age): 2.5 mya - 10,000 BCE<br>Hunter-gatherers; hand axes (Acheulian culture)<br>Cave art; no farming; Homo erectus + Homo sapiens"]:::date
    ST --> ST2["Mesolithic (Middle Stone Age): 10,000-6000 BCE<br>Microliths (tiny stone tools)<br>Semi-nomadic; fishing + gathering; dogs domesticated"]:::date
    ST --> ST3["Neolithic (New Stone Age): 6000-4000 BCE<br>FARMING BEGINS; animals domesticated<br>Polished stone tools; pottery; permanent settlements"]:::date
    ST --> ST4["Chalcolithic (Copper-Stone Age): 4000-1500 BCE<br>First use of copper (+ stone)<br>Harappan Civ starts in Chalcolithic period"]:::date
    SN --> SN1["Bhimbetka caves: Raisen, Madhya Pradesh<br>UNESCO World Heritage Site<br>Cave paintings from 30,000 years ago; Palaeolithic-Mesolithic"]:::date
    TR --> TR1["TRAP: Farming begins in NEOLITHIC age<br>NOT in Palaeolithic (hunting only)<br>NOT in Mesolithic (semi-nomadic, beginning of farming)"]:::trap""",

"## Chapter 2 — Indus Valley / Harappan Civilisation (c. 3300 – 1300 BCE)": """\
flowchart TD
    R["HARAPPAN CIVILISATION<br>3300-1300 BCE"]:::root
    R --> SI["Major Sites"]:::key
    R --> FE["Key Features"]:::key
    R --> EX["Excavators + Dates"]:::date
    R --> TR["TRAP: What was absent at Harappa"]:::trap
    SI --> SI1["Mohenjo-daro: Sindh (Pakistan)<br>Harappa: Punjab (Pakistan)<br>Dholavira: Gujarat — water management"]:::key
    SI --> SI2["Lothal: Gujarat — India's ONLY ancient dockyard<br>Kalibangan: Rajasthan — fire altars found<br>Rakhigarhi: Haryana — largest Harappan site in India"]:::key
    FE --> FE1["Grid-pattern town planning; covered drains<br>Great Bath at Mohenjo-daro (12m x 7m)<br>Granaries for surplus storage"]:::key
    FE --> FE2["Script: Undeciphered (written right to left)<br>No iron tools; bronze weapons<br>Trade with Mesopotamia (Iraq)"]:::key
    EX --> EX1["Harappa discovered: Daya Ram Sahni 1921<br>Mohenjo-daro: R.D. Banerji 1922<br>John Marshall: first to use term 'Indus Civilization'"]:::date
    EX --> EX2["Dholavira: R.S. Bisht (modern excavation)<br>Civilisation DECLINED c.1900 BCE<br>Reason: climate change + Saraswati river drying"]:::date
    TR --> TR1["TRAP: NO iron tools (bronze age)<br>NO clear temples or priest-king<br>NO signs of warfare or army<br>NO horses in early phase (came in late)"]:::trap""",

"## Chapter 3 — The Vedic Age (c. 1500 – 600 BCE)": """\
flowchart TD
    R["THE VEDIC AGE<br>1500-600 BCE"]:::root
    R --> EV["Early vs Later Vedic"]:::key
    R --> VE["4 Vedas"]:::key
    R --> SC["Social Structure"]:::key
    R --> TR["TRAP: Which Veda is oldest?"]:::trap
    EV --> EV1["Early Vedic (1500-1000 BCE): Rig Veda period<br>Pastoral + semi-nomadic Aryans<br>Relatively equal status of women; cattle wealth"]:::key
    EV --> EV2["Later Vedic (1000-600 BCE): Settled agriculture<br>Rigid caste system hardened<br>Kings more powerful; ritual sacrifices grew"]:::key
    VE --> VE1["RIG VEDA: oldest text (1500 BCE+)<br>10 mandalas; 1028 hymns; Gayatri Mantra<br>Knowledge of hymns to gods"]:::key
    VE --> VE2["SAMA VEDA: melodies + chants<br>YAJUR VEDA: rituals + sacrificial formulae<br>ATHARVA VEDA: magic, spells, everyday life"]:::key
    SC --> SC1["4 Varnas: Brahmin (priest), Kshatriya (warrior)<br>Vaishya (merchant), Shudra (servant)<br>NOT birth-based originally; became rigid later"]:::key
    SC --> SC2["Political units: Jana (tribe), Rashtra (kingdom)<br>Sabba + Samiti: tribal assemblies (early democracy)<br>Raja: chief selected by sabha"]:::key
    TR --> TR1["TRAP: RIG VEDA is oldest of the 4 Vedas<br>NOT Sama or Atharva<br>Vedanta = end of Vedas = Upanishads (philosophy)"]:::trap""",

"## Chapter 4 — The 16 Mahajanapadas + the Rise of Magadha": """\
flowchart TD
    R["16 MAHAJANAPADAS<br>600-300 BCE"]:::root
    R --> MJ["Key Mahajanapadas"]:::key
    R --> MG["Rise of Magadha"]:::key
    R --> DY["Magadha Dynasties"]:::date
    R --> TR["TRAP: Pataliputra location"]:::trap
    MJ --> MJ1["16 Mahajanapadas (600-300 BCE)<br>Republics (Ganas): Vajji (Licchavi), Malla, Shakya<br>Kingdoms: Magadha, Kosala, Vatsa, Avanti"]:::key
    MJ --> MJ2["4 most powerful: Magadha, Kosala, Vatsa, Avanti<br>Magadha finally conquered all others<br>Capital of Magadha: Rajagriha then Pataliputra"]:::key
    MG --> MG1["Magadha's advantages:<br>Iron ore deposits nearby<br>Ganga + Son rivers for agriculture + trade<br>Strategic central location"]:::key
    DY --> DY1["Haryanka: Bimbisara (founder; contemporary of Buddha)<br>Killed by son Ajatashatru<br>Moved capital to Pataliputra (Patna)"]:::date
    DY --> DY2["Shishunaga dynasty: overthrew Haryanka<br>Nanda dynasty: Dhana Nanda (last Nanda)<br>Wealthy but cruel; Alexander reached Punjab (326 BCE)"]:::date
    DY --> DY3["Maurya dynasty: Chandragupta Maurya (322 BCE)<br>Overthrew Dhana Nanda with Chanakya's help<br>First pan-Indian empire"]:::date
    TR --> TR1["TRAP: Pataliputra = modern Patna, Bihar<br>Rajagriha = capital BEFORE Pataliputra<br>Ajatashatru moved capital to Pataliputra"]:::trap""",

"## Chapter 5 — Buddhism": """\
flowchart TD
    R["BUDDHISM"]:::root
    R --> LI["Life of the Buddha"]:::date
    R --> TE["Core Teachings"]:::key
    R --> CO["Buddhist Councils"]:::date
    R --> TR["TRAP: Four sites must memorise"]:::trap
    LI --> LI1["Born: c.563 BCE at Lumbini, Nepal<br>Clan: Shakya; Family: Kshatriya Gautama<br>Father: Suddhodana; Wife: Yashodhara"]:::date
    LI --> LI2["Enlightenment: Bodh Gaya (under Peepal/Bodhi tree)<br>First Sermon: Sarnath (Deer Park) — Dhammachakka<br>Death/Parinirvana: Kushinagar; c.483 BCE"]:::date
    TE --> TE1["4 Noble Truths:<br>1. Dukkha (suffering exists)<br>2. Samudaya (craving is cause)<br>3. Nirodha (end of craving = nirvana)<br>4. Magga (follow the 8-fold path)"]:::key
    TE --> TE2["8-fold Path: Right View, Intention, Speech<br>Action, Livelihood, Effort, Mindfulness, Concentration<br>Middle Path: avoid extreme asceticism + luxury"]:::key
    TE --> TE3["Tripitaka: 3 baskets of Buddhist scripture<br>Vinaya Pitaka (rules for monks)<br>Sutta Pitaka, Abhidhamma Pitaka"]:::key
    CO --> CO1["1st Council: Rajagriha (Ajatashatru's reign)<br>2nd Council: Vaishali (schism began)<br>3rd Council: Pataliputra (Ashoka; Theravada vs Mahayana)"]:::date
    CO --> CO2["4th Council: Kashmir (Kanishka; Mahayana codified)<br>Hinayana vs Mahayana split<br>Buddhism spread to SE Asia by Ashoka's son Mahendra"]:::date
    TR --> TR1["TRAP: 4 holy sites —<br>Lumbini (birth), Bodh Gaya (enlightenment)<br>Sarnath (first sermon), Kushinagar (death)"]:::trap""",

"## Chapter 6 — Jainism": """\
flowchart TD
    R["JAINISM"]:::root
    R --> MV["Mahavira's Life"]:::date
    R --> TE["Core Teachings"]:::key
    R --> SC["Sects"]:::key
    R --> TR["TRAP: Tirthankaras"]:::trap
    MV --> MV1["Vardhamana Mahavira: 24th and LAST Tirthankara<br>Born: c.599 BCE Vaishali, Bihar<br>Clan: Kshatriya; Father: Siddhartha"]:::date
    MV --> MV2["Enlightenment: near river Rijupalika<br>After 12 years of asceticism<br>Death: Pawapuri, Bihar; c.527 BCE"]:::date
    TE --> TE1["5 Great Vows (Panchamahavratas):<br>Ahimsa (non-violence — most important)<br>Satya, Asteya, Brahmacharya, Aparigraha"]:::key
    TE --> TE2["3 Jewels (Triratna):<br>Right Faith, Right Knowledge, Right Conduct<br>All life is sacred — wear mask (Digambara monks)"]:::key
    TE --> TE3["Anekantavada: reality is multifaceted<br>Syadvada: conditional predication<br>Jainism rejected Vedic authority + caste"]:::key
    SC --> SC1["Digambara: sky-clad (naked) monks<br>Believe women cannot attain moksha<br>Shvetambara: white-clad monks; allow nuns"]:::key
    TR --> TR1["TRAP: 24 Tirthankaras total<br>1st Tirthankara: Rishabhanatha<br>23rd: Parshvanatha; 24th: Mahavira<br>Mahavira did NOT found Jainism — he was 24th"]:::trap""",

"## Chapter 7 — Mauryan Empire (322 – 185 BCE)": """\
flowchart TD
    R["MAURYAN EMPIRE<br>322-185 BCE"]:::root
    R --> FO["Foundation"]:::date
    R --> AS["Ashoka the Great"]:::date
    R --> AD["Ashoka's Edicts + Legacy"]:::key
    R --> TR["TRAP: Kalinga War — what changed"]:::trap
    FO --> FO1["Founded: 322 BCE by Chandragupta Maurya<br>Overthrew Dhana Nanda with Chanakya's help<br>Chanakya wrote Arthashastra — first political economy book"]:::date
    FO --> FO2["Chandragupta defeated Seleucus Nicator (325 BCE)<br>Got NW India including Pakistan + Afghanistan<br>Bindusara (son): expanded to Deccan"]:::date
    AS --> AS1["Ashoka: 268-232 BCE; son of Bindusara<br>Kalinga War: 261 BCE — massive bloodshed<br>Converted to Buddhism after witnessing destruction"]:::date
    AS --> AS2["Ashoka spread Buddhism: sent missions to<br>Sri Lanka (son Mahendra + daughter Sanghamitra)<br>SE Asia, Central Asia, West Asia"]:::date
    AD --> AD1["Ashoka's pillars: Lion Capital at Sarnath<br>= India's NATIONAL EMBLEM<br>Dharma Chakra = 24-spoked wheel on national flag"]:::key
    AD --> AD2["Rock edicts: carved on rocks + pillars<br>Brahmi script (decoded by James Prinsep 1837)<br>Message: dhamma, non-violence, religious tolerance"]:::key
    TR --> TR1["TRAP: Kalinga = modern Odisha<br>Kalinga War (261 BCE) transformed Ashoka<br>Result: Dhammavijaya (moral conquest) replaced Digvijaya"]:::trap""",

"## Chapter 8 — Gupta Age (320 – 550 CE) — India's Classical Golden Age": """\
flowchart TD
    R["GUPTA AGE<br>320-550 CE - Golden Age"]:::root
    R --> RU["Key Rulers"]:::date
    R --> AC["Achievements in Arts + Science"]:::key
    R --> SC["Scholars at Court"]:::key
    R --> TR["TRAP: Vikramaditya identity"]:::trap
    RU --> RU1["Chandragupta I: 320 CE; founded Gupta Era<br>Married Lichchhavi princess Kumaradevi<br>Title: Maharajadhiraja (king of kings)"]:::date
    RU --> RU2["Samudragupta (335-375 CE):<br>'Napoleon of India' (V.A. Smith)<br>Allahabad Pillar Inscription by Harishena"]:::date
    RU --> RU3["Chandragupta II Vikramaditya (375-415 CE):<br>Defeated Shakas of W India<br>Chinese pilgrim Fa-hien visited during his reign"]:::date
    AC --> AC1["Aryabhata (499 CE): Aryabhatiya<br>Pi value (3.14), Earth rotates on axis<br>Decimal system; value of zero"]:::key
    AC --> AC2["Kalidasa: greatest Sanskrit poet-playwright<br>Works: Shakuntala, Meghaduta, Kumarasambhava<br>Nine Gems (Navaratnas) in Vikramaditya's court"]:::key
    SC --> SC1["Varahamihira: astronomy + astrology (Brihatsamhita)<br>Brahmagupta: mathematics<br>Dhanvantari: medicine (Ayurveda)"]:::key
    TR --> TR1["TRAP: Vikramaditya = TITLE not a name<br>Chandragupta II had this title<br>Vikram Samvat calendar: attributed to legendary Vikramaditya"]:::trap""",

"## Chapter 9 — Harsha + Chalukyas + Rashtrakutas + Pallavas": """\
flowchart TD
    R["POST-GUPTA DYNASTIES<br>600-900 CE"]:::root
    R --> HR["Harsha of Kanauj"]:::date
    R --> CH["Chalukyas of Vatapi"]:::date
    R --> PA["Pallavas of Kanchi"]:::key
    R --> RT["Rashtrakutas"]:::key
    HR --> HR1["Harsha (606-647 CE): Pushyabhuti dynasty<br>Capital: Kanauj (UP)<br>Chinese visitor Xuanzang (Hiuen Tsang) wrote about him"]:::date
    HR --> HR2["Battle of Narmada: Harsha defeated by<br>Pulakeshin II (Chalukya) c.618 CE<br>Could NOT expand into South India"]:::key
    CH --> CH1["Pulakeshin II: greatest Chalukya king<br>Capital: Vatapi (Badami, Karnataka)<br>Aihole inscription praises his victories"]:::date
    CH --> CH2["Chalukyas: patrons of cave temples<br>Pattadakal, Aihole, Badami cave temples<br>UNESCO World Heritage Sites"]:::key
    PA --> PA1["Pallavas: Kanchi (Kanchipuram), Tamil Nadu<br>Narasimhavarman I: built Mahabalipuram Shore Temple<br>Rajasimha: built Kailasanatha temple"]:::key
    PA --> PA2["Rathas (monolithic chariots) at Mahabalipuram<br>Carved from single rock<br>Important for Dravidian architecture origin"]:::key
    RT --> RT1["Rashtrakutas: Deccan; founded 753 CE by Dantidurga<br>Ellora caves patron (Kailasa temple = largest monolithic)<br>Literary tradition in Sanskrit + Kannada"]:::key""",

"## Chapter 10 — Chola Empire + South Indian Kingdoms": """\
flowchart TD
    R["CHOLA EMPIRE<br>9th-13th Century CE"]:::root
    R --> FO["Foundation"]:::date
    R --> RJ["Rajaraja I and Rajendra I"]:::date
    R --> AD["Administration"]:::key
    R --> AR["Architecture"]:::key
    FO --> FO1["Imperial Cholas: founded by Vijayalaya (9th century)<br>Capital: Thanjavur (Tanjore), Tamil Nadu<br>Arose from earlier Sangam age Cholas"]:::date
    RJ --> RJ1["Rajaraja I (985-1014 CE):<br>Built Brihadeeshwara Temple (Tanjore)<br>Conquered Sri Lanka; extended to Malabar"]:::date
    RJ --> RJ2["Rajendra I (1014-1044 CE): greatest Chola<br>'Gangaikonda Chola' — brought Ganga water<br>Naval expedition to Sumatra + Malaysia"]:::date
    RJ --> RJ3["Chola NAVY: strongest in Indian history<br>Reached Malaysia, Indonesia, Cambodia<br>Spread Hindu culture + Tamil language to SE Asia"]:::key
    AD --> AD1["Local self-government: unique feature<br>Ur (hamlet), Nadu (district), Mandalam (province)<br>Inscriptions show elections in villages (Uttaramerur)"]:::key
    AR --> AR1["Brihadeeshwara Temple: UNESCO World Heritage<br>61-meter vimana (tower); entirely of granite<br>Rajendra I built Gangaikondacholapuram"]:::key
    AR --> AR2["TRAP: Brihadeeshwara = Tanjore; Rajaraja I<br>Gangaikondacholapuram = Rajendra I<br>Do NOT confuse the two temples + builders"]:::trap""",
}


# ─────────────────────────────────────────────────────────────────────────────
# ECONOMICS
# ─────────────────────────────────────────────────────────────────────────────
ECONOMICS = {

"## Chapter 1 — Economic Systems and Sectors": """\
flowchart TD
    R["ECONOMIC SYSTEMS AND SECTORS"]:::root
    R --> SE["3 Sectors of Economy"]:::key
    R --> SY["Types of Economic Systems"]:::key
    R --> IN["India's Economic Profile"]:::key
    SE --> SE1["Primary sector: agriculture, mining, fishing<br>Secondary: manufacturing, construction<br>Tertiary (Services): banking, IT, trade, transport"]:::key
    SE --> SE2["India GDP share (approx 2024):<br>Services: ~55% (largest)<br>Industry: ~29%; Agriculture: ~16%"]:::key
    SE --> SE3["Agriculture employs ~46% of workforce<br>IT + services = largest GDP contributor<br>TRAP: employment share NOT same as GDP share"]:::trap
    SY --> SY1["Market economy: prices by supply-demand; USA<br>Planned (Socialist) economy: state controls; USSR<br>Mixed economy: both public + private; India"]:::key
    IN --> IN1["India: Mixed economy since 1947<br>LPG reforms 1991: Liberalisation, Privatisation, Globalisation<br>PM Narasimha Rao + FM Manmohan Singh"]:::date""",

"## Chapter 2 — GDP, GNP, and National Income": """\
flowchart TD
    R["GDP, GNP AND NATIONAL INCOME"]:::root
    R --> DE["Key Definitions"]:::key
    R --> CA["Calculation Chain"]:::proc
    R --> IN["India Specifics"]:::key
    R --> TR["TRAP: Real vs Nominal GDP"]:::trap
    DE --> DE1["GDP: market value of all FINAL goods + services<br>produced WITHIN a country in a year<br>Includes output of foreigners in India"]:::key
    DE --> DE2["GNP: GDP + Net Factor Income from Abroad<br>Income of all nationals (wherever located)<br>Excludes output of foreigners in India"]:::key
    CA --> CA1["GNP - Depreciation = NNP at market price<br>NNP at market price - indirect taxes + subsidies<br>= NNP at factor cost = National Income"]:::proc
    CA --> CA2["Per Capita Income = NNP / population<br>Real GDP: constant prices (removes inflation effect)<br>Nominal GDP: current prices (includes inflation)"]:::proc
    IN --> IN1["India's GDP base year: 2011-12<br>GDP measured by: CSO (Central Statistics Office)<br>4 quarterly estimates per year"]:::key
    TR --> TR1["TRAP: Real GDP growth removes inflation<br>If inflation = 10% and nominal GDP grows 12%<br>Real GDP growth = only 2%"]:::trap""",

"## Chapter 3 — The Reserve Bank of India (RBI)": """\
flowchart TD
    R["RESERVE BANK OF INDIA (RBI)"]:::root
    R --> FO["Foundation + HQ"]:::date
    R --> FN["Functions"]:::key
    R --> MT["Monetary Policy Tools"]:::key
    R --> TR["TRAP: CRR vs SLR"]:::trap
    FO --> FO1["Founded: April 1, 1935 (under RBI Act 1934)<br>Nationalised: January 1, 1949<br>HQ: Mumbai; Governor: Sanjay Malhotra (from Dec 2024)"]:::date
    FN --> FN1["Issues currency notes (except Re 1 coin — Govt)<br>Banker to Government (central + state)<br>Banker to banks (lender of last resort)"]:::key
    FN --> FN2["Manages foreign exchange reserves<br>Regulates credit + money supply<br>Supervises commercial banks (CRR, SLR, repo)"]:::key
    MT --> MT1["Repo Rate: rate at which RBI lends to banks<br>Reverse Repo: rate at which RBI borrows from banks<br>Raise Repo Rate = credit expensive = control inflation"]:::key
    MT --> MT2["CRR (Cash Reserve Ratio): % of deposits<br>banks must keep with RBI as cash<br>SLR (Statutory Liquidity Ratio): % kept as liquid assets"]:::key
    MT --> MT3["MPC (Monetary Policy Committee): 6 members<br>RBI Governor chairs; meets every 2 months<br>Inflation target: 4% (±2%)"]:::key
    TR --> TR1["TRAP: CRR = kept with RBI (cash only)<br>SLR = kept by bank (cash+gold+govt securities)<br>Raising both reduces money banks can lend"]:::trap""",

"## Chapter 4 — Banking in India": """\
flowchart TD
    R["BANKING IN INDIA"]:::root
    R --> HI["History"]:::date
    R --> TY["Types of Banks"]:::key
    R --> IN["Key Institutions"]:::key
    R --> SC["Key Schemes"]:::key
    HI --> HI1["Imperial Bank (1921) converted to SBI in 1955<br>Bank Nationalisation: 14 banks July 1969<br>6 more nationalised in 1980 (PM Indira Gandhi)"]:::date
    TY --> TY1["Public sector: SBI + 11 other nationalised banks<br>Private sector: HDFC, ICICI, Axis, Kotak<br>Foreign banks: Citibank, HSBC, Standard Chartered"]:::key
    TY --> TY2["RRBs: Regional Rural Banks (1975)<br>Co-operative banks: agriculture credit<br>Small Finance Banks + Payment Banks (2015)"]:::key
    IN --> IN1["NABARD: 1982; agriculture + rural credit<br>SIDBI: small industry development<br>NHB: National Housing Bank; EXIM Bank: trade"]:::key
    SC --> SC1["PMJDY (Jan Dhan Yojana): zero-balance accounts<br>Financial inclusion for unbanked population<br>Launched Aug 28, 2014"]:::date
    SC --> SC2["NPA: Non-Performing Asset<br>Loan overdue for more than 90 days<br>Insolvency + Bankruptcy Code 2016: resolution"]:::key""",

"## Chapter 5 — Inflation": """\
flowchart TD
    R["INFLATION"]:::root
    R --> DE["Definition + Measurement"]:::key
    R --> TY["Types of Inflation"]:::key
    R --> EF["Effects"]:::key
    R --> TR["TRAP: CPI vs WPI"]:::trap
    DE --> DE1["Inflation: sustained rise in general price level<br>Purchasing power of money falls<br>India measures: CPI (Consumer Price Index)"]:::key
    DE --> DE2["CPI: based on retail prices; basket of goods/services<br>WPI: Wholesale Price Index; producer prices<br>CPI = official inflation measure (since 2014)"]:::key
    TY --> TY1["Demand-pull: excess money chasing same goods<br>Cost-push: input cost rises (oil shock)<br>Built-in: workers demand higher wages as prices rise"]:::key
    TY --> TY2["Hyperinflation: very high (Germany 1923, Zimbabwe 2008)<br>Stagflation: inflation + stagnation together<br>Deflation: falling prices (reduces spending)"]:::key
    EF --> EF1["Debtors gain: pay back less in real terms<br>Creditors lose: receive less in real terms<br>Fixed income earners lose most purchasing power"]:::key
    TR --> TR1["TRAP: WPI is NOT official inflation measure now<br>CPI replaced WPI as headline inflation in 2014<br>RBI's MPC targets CPI inflation of 4% ± 2%"]:::trap""",

"## Chapter 6 — Union Budget": """\
flowchart TD
    R["UNION BUDGET"]:::root
    R --> PR["Presentation"]:::key
    R --> ST["Budget Structure"]:::proc
    R --> DE["Key Deficits"]:::key
    R --> TR["TRAP: Revenue vs Capital"]:::trap
    PR --> PR1["Presented by Finance Minister on February 1<br>(Earlier: last working day of February)<br>Interim budget in election year"]:::key
    ST --> ST1["Revenue Budget: recurring in nature<br>Revenue Receipts (taxes, dividends)<br>Revenue Expenditure (salaries, interest, subsidies)"]:::proc
    ST --> ST2["Capital Budget: long-term / asset-building<br>Capital Receipts (loans, disinvestment)<br>Capital Expenditure (infrastructure, repayment of loans)"]:::proc
    DE --> DE1["Fiscal Deficit: Total expenditure minus<br>total receipts EXCLUDING borrowings<br>Shows how much government needs to borrow"]:::key
    DE --> DE2["Revenue Deficit: Revenue exp - Revenue receipts<br>Primary Deficit: Fiscal deficit - Interest payments<br>FRBM Act 2003: targets to reduce fiscal deficit"]:::key
    TR --> TR1["TRAP: Revenue expenditure = no asset creation<br>Capital expenditure = asset creation<br>Interest payment = Revenue expenditure NOT capital"]:::trap""",

"## Chapter 7 — GST": """\
flowchart TD
    R["GOODS AND SERVICES TAX (GST)"]:::root
    R --> IN["Introduction"]:::date
    R --> SL["GST Slabs"]:::key
    R --> ST["Structure"]:::key
    R --> TR["TRAP: Exempted goods"]:::trap
    IN --> IN1["Introduced: July 1, 2017<br>101st Constitutional Amendment Act<br>One Nation One Tax — replaced 17 indirect taxes"]:::date
    IN --> IN2["Replaced: VAT, Service Tax, Excise Duty<br>Central Sales Tax, Entertainment Tax, etc.<br>Destination-based tax (tax goes to where consumed)"]:::key
    SL --> SL1["0%: Essential items — milk, salt, fresh vegetables<br>grains, fresh meat, books, newspapers<br>5%: Packaged food, coal, medicines, transport"]:::key
    SL --> SL2["12%: Processed food, computers, mobile phones<br>18%: Capital goods, electronics, most services<br>28%: Luxury + sin goods (AC, premium cars, tobacco)"]:::key
    ST --> ST1["CGST: Central GST (goes to Centre)<br>SGST: State GST (goes to state)<br>IGST: Integrated GST (interstate trade; goes to Centre)"]:::key
    ST --> ST2["GST Council: Finance Minister chairs<br>1/3 vote weightage to Centre; 2/3 to States<br>Decisions by 3/4 majority"]:::key
    TR --> TR1["TRAP: Petrol, diesel, alcohol NOT under GST<br>Real estate partially under GST<br>Electricity NOT under GST — biggest exclusions"]:::trap""",

"## Chapter 8 — Finance Commissions": """\
flowchart TD
    R["FINANCE COMMISSIONS"]:::root
    R --> BA["Basic Facts"]:::key
    R --> KE["Key Finance Commissions"]:::date
    R --> CR["Criteria for Devolution"]:::key
    BA --> BA1["Constitutional body under Article 280<br>Constituted every 5 years by President<br>Recommends Centre-State revenue sharing"]:::key
    BA --> BA2["Two types of distribution:<br>Vertical: how much to all states combined<br>Horizontal: how to divide among individual states"]:::key
    KE --> KE1["1st Finance Commission: 1951 — K.C. Niyogi<br>13th FC: 2010-15 — Vijay Kelkar<br>14th FC: 2015-20 — Y.V. Reddy (raised state share to 42%)"]:::date
    KE --> KE2["15th FC: 2020-25 — N.K. Singh<br>Recommended 41% to states (minus J&K as UT)<br>16th FC: 2026-31 — Arvind Panagariya (constituted 2023)"]:::date
    CR --> CR1["Criteria include: Population (2011 census)<br>Income distance from richest state<br>Area, forest cover, demographic performance (fertility)"]:::key
    CR --> CR2["TRAP: 14th FC raised state share from 32% to 42%<br>15th FC gave 41% (J&K bifurcation reduced it by 1%)<br>Richer states get less; poorer states get more (horizontal)"]:::trap""",

"## Chapter 9 — Five-Year Plans and NITI Aayog": """\
flowchart TD
    R["FIVE-YEAR PLANS AND NITI AAYOG"]:::root
    R --> PC["Planning Commission"]:::date
    R --> NA["NITI Aayog"]:::date
    R --> KP["Key Plans"]:::key
    R --> TR["TRAP: Last Five-Year Plan"]:::trap
    PC --> PC1["Planning Commission: established 1950<br>PM = ex-officio Chairman<br>First Chairman: Jawaharlal Nehru"]:::date
    PC --> PC2["Based on Soviet model of central planning<br>Nehru-Mahalanobis model: heavy industry emphasis<br>12 Five-Year Plans: 1951 to 2017"]:::key
    NA --> NA1["NITI Aayog: replaced Planning Commission<br>January 1, 2015<br>Full form: National Institution for Transforming India"]:::date
    NA --> NA2["PM = Chairperson; no voting powers<br>Think tank; not funding body (unlike Planning Commission)<br>Atal Innovation Mission, Aspirational Districts Programme"]:::key
    KP --> KP1["1st Plan (1951-56): agriculture + irrigation<br>2nd Plan (1956-61): heavy industry (Mahalanobis)<br>5th Plan (1974-79): poverty eradication (Garibi Hatao)"]:::key
    KP --> KP2["7th Plan (1985-90): food, work, productivity<br>8th Plan (1992-97): LPG reforms context<br>12th Plan (2012-17): Faster More Inclusive Sustainable Growth"]:::key
    TR --> TR1["TRAP: 12th Plan (2012-17) = LAST Five-Year Plan<br>After that: 3-year Action Agenda + Vision 2022/2047<br>No 13th Five-Year Plan was ever made"]:::trap""",

"## Chapter 10 — Poverty, Unemployment, and Human Development": """\
flowchart TD
    R["POVERTY, UNEMPLOYMENT AND HDI"]:::root
    R --> PO["Poverty Line"]:::key
    R --> UN["Types of Unemployment"]:::key
    R --> HD["Human Development Index"]:::key
    R --> SC["Key Schemes"]:::key
    PO --> PO1["Tendulkar Committee (2009): Rural Rs 816/month<br>Urban Rs 1000/month (2011-12 prices)<br>Based on: caloric intake + other needs"]:::key
    PO --> PO2["Rangarajan Committee (2014): higher estimates<br>Rural Rs 972/month; Urban Rs 1407/month<br>India poverty declined from 55% (1970s) to ~22%"]:::key
    UN --> UN1["Structural: industry shift (e.g. farmers to factories)<br>Frictional: between jobs (short-term)<br>Seasonal: farming off-season idle workers"]:::key
    UN --> UN2["Disguised unemployment: more workers than needed<br>Classic example: Indian agriculture<br>Remove worker, no drop in output"]:::key
    HD --> HD1["HDI: UNDP since 1990<br>3 dimensions: Long life, Education, GNI per capita<br>Scale 0-1; India ~0.644 (Medium HDI)"]:::key
    SC --> SC1["MGNREGS (NREGA 2005): 100 days guaranteed employment<br>Demand-driven; Rs 207/day wage (avg)<br>Focus: rural household; Rs 1 lakh crore+ annual budget"]:::date""",

"## Chapter 11 — Balance of Payments and Forex": """\
flowchart TD
    R["BALANCE OF PAYMENTS AND FOREX"]:::root
    R --> BO["Balance of Payments (BOP)"]:::proc
    R --> CA["Current Account"]:::key
    R --> FX["Forex Reserves"]:::key
    R --> TR["TRAP: Trade deficit vs Current Account deficit"]:::trap
    BO --> BO1["BOP: record of all economic transactions<br>between residents of a country and the rest<br>BOP = Current Account + Capital Account"]:::proc
    BO --> BO2["Current Account Deficit (CAD): most common<br>India usually runs a CAD<br>Financed by capital account surpluses (FDI, FII)"]:::key
    CA --> CA1["Current Account = Trade balance (goods)<br>+ Trade in services + Income + Transfers<br>Trade deficit: imports > exports (India typical)"]:::key
    CA --> CA2["India: largest remittance recipient globally<br>NRI remittances ~$120 billion/year<br>Helps offset trade deficit partially"]:::key
    FX --> FX1["India's Forex Reserves: ~$620 billion (2024)<br>4th largest in the world<br>Held by RBI; includes gold + SDRs"]:::key
    TR --> TR1["TRAP: Trade deficit = only goods imbalance<br>Current Account deficit = goods + services + income<br>India can have CA surplus even with trade deficit"]:::trap""",

"## Chapter 12 — International Economic Institutions": """\
flowchart TD
    R["INTERNATIONAL ECONOMIC INSTITUTIONS"]:::root
    R --> IM["IMF"]:::date
    R --> WB["World Bank Group"]:::date
    R --> WT["WTO"]:::date
    R --> OT["Others"]:::key
    IM --> IM1["IMF: International Monetary Fund<br>Founded: 1944 Bretton Woods; 190 members<br>HQ: Washington DC; helps BOP crisis countries"]:::date
    IM --> IM2["IMF creates SDR (Special Drawing Rights)<br>Surveillance of member economies<br>Conditionality on loans: austerity measures"]:::key
    WB --> WB1["World Bank: founded 1944 Bretton Woods<br>HQ: Washington DC<br>IBRD (middle income) + IDA (poor countries)"]:::date
    WB --> WB2["IFC: private sector; MIGA: investment guarantees<br>Focus: poverty reduction + sustainable development<br>Funds infrastructure in developing nations"]:::key
    WT --> WT1["WTO: World Trade Organization<br>Replaced GATT in 1995; HQ Geneva<br>164 members; settles trade disputes"]:::date
    WT --> WT2["Doha Development Agenda: 2001 (still incomplete)<br>Most Favoured Nation (MFN) principle<br>India: active in agriculture protection debates"]:::key
    OT --> OT1["ADB: Asian Development Bank; HQ Manila; 1966<br>AIIB: HQ Beijing; 2016; China-led; 106 members<br>NDB: New Development Bank (BRICS); HQ Shanghai"]:::key""",

"## Chapter 13 — Agriculture": """\
flowchart TD
    R["AGRICULTURE IN ECONOMICS"]:::root
    R --> SC["India's Scale"]:::key
    R --> KP["Key Products + Rank"]:::key
    R --> RE["Reforms"]:::key
    R --> TR["TRAP: Largest vs 2nd Largest"]:::trap
    SC --> SC1["India: 2nd largest agricultural land globally<br>After USA (by area under cultivation)<br>Agriculture employs ~46% of workforce"]:::key
    SC --> SC2["Contributes ~16% of GDP<br>~13% of total exports<br>Allied sectors: Animal Husbandry, Fisheries, Forestry"]:::key
    KP --> KP1["LARGEST PRODUCER in world:<br>Milk, Spices, Jute, Banana, Mango<br>Chickpea, Buffalo, Freshwater fish"]:::key
    KP --> KP2["2ND LARGEST PRODUCER:<br>Rice, Wheat, Sugar, Cotton<br>Vegetables, Fruits, Oilseeds, Tea"]:::key
    RE --> RE1["MSP (Minimum Support Price): guaranteed price<br>Announced by CCEA; CACP recommends<br>23 crops covered under MSP"]:::key
    RE --> RE2["e-NAM: electronic National Agriculture Market<br>APMC reform: direct farm-to-buyer linkage<br>PM-KISAN: Rs 6000/year (3 installments) to farmers"]:::key
    TR --> TR1["TRAP: India = LARGEST milk producer globally<br>India = 2ND largest rice producer (after China)<br>India = 2ND largest wheat producer (after China)"]:::trap""",

"## Chapter 14 — Key Government Schemes": """\
flowchart LR
    R["KEY GOVERNMENT SCHEMES"]:::root
    R --> HE["Health + Social"]:::key
    R --> AG["Agriculture"]:::key
    R --> EN["Energy + Environment"]:::key
    R --> IN["Infrastructure + Finance"]:::key
    HE --> H1["Ayushman Bharat PM-JAY: Rs 5 lakh/year<br>health cover; 50 crore beneficiaries (poorest 40%)"]:::key
    HE --> H2["PMJAY: world's largest health insurance<br>Ujjwala Yojana: free LPG to BPL households<br>PM Awas Yojana: housing for all (rural + urban)"]:::key
    AG --> A1["PM-KISAN: Rs 6000/year direct cash to farmers<br>MGNREGS: 100 days employment rural<br>PMFBY: crop insurance"]:::key
    EN --> E1["PM Surya Ghar Muft Bijli: rooftop solar<br>1 crore households; 300 units free/month<br>National Solar Mission: 500 GW renewable by 2030"]:::key
    IN --> I1["PMJDY: zero-balance bank accounts<br>PM Gati Shakti: multimodal infrastructure<br>Make in India (2014): boost manufacturing"]:::key
    IN --> I2["Start-Up India (2016): ease of doing business<br>Digital India: internet + governance<br>Swachh Bharat Mission (2014): ODF + cleanliness"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# PHYSICS
# ─────────────────────────────────────────────────────────────────────────────
PHYSICS = {

"## Chapter A1 — SI Units": """\
flowchart TD
    R["SI UNITS"]:::root
    R --> B["7 Base SI Units"]:::key
    R --> D["Key Derived Units"]:::key
    R --> P["Prefixes"]:::key
    B --> B1["Metre (m): length<br>Kilogram (kg): mass<br>Second (s): time"]:::key
    B --> B2["Ampere (A): electric current<br>Kelvin (K): temperature<br>Mole (mol): amount of substance<br>Candela (cd): luminous intensity"]:::key
    D --> D1["Newton (N) = kg m/s2 (force)<br>Joule (J) = N m (energy/work)<br>Watt (W) = J/s (power)"]:::key
    D --> D2["Pascal (Pa) = N/m2 (pressure)<br>Hertz (Hz) = 1/s (frequency)<br>Coulomb (C) = A s (charge)"]:::key
    P --> P1["micro (mu) = 10^-6; milli (m) = 10^-3<br>centi (c) = 10^-2; kilo (k) = 10^3<br>mega (M) = 10^6; giga (G) = 10^9"]:::key""",

"## Chapter A2 — Newton's Laws of Motion": """\
flowchart TD
    R["NEWTON'S LAWS OF MOTION"]:::root
    R --> L1["1st Law: Inertia"]:::key
    R --> L2["2nd Law: F = ma"]:::key
    R --> L3["3rd Law: Action-Reaction"]:::key
    R --> MO["Momentum"]:::key
    L1 --> L1a["Object at rest stays at rest<br>Object in motion stays in motion<br>UNLESS external force acts on it<br>Seatbelts, coin-on-card demo"]:::key
    L2 --> L2a["F = ma (Force = mass x acceleration)<br>1 Newton: accelerates 1 kg by 1 m/s2<br>Net force proportional to acceleration"]:::key
    L3 --> L3a["Every action has equal + opposite reaction<br>Rocket thrust: gases pushed down; rocket goes up<br>Swimming: push water back; body moves forward"]:::key
    MO --> MO1["Momentum p = mv (mass x velocity)<br>Law of Conservation of Momentum: no external force<br>Impulse = Force x time = change in momentum"]:::key""",

"## Chapter A3 — Gravitation": """\
flowchart TD
    R["GRAVITATION"]:::root
    R --> UG["Universal Gravitation"]:::key
    R --> EG["Earth's Gravity (g)"]:::key
    R --> ES["Escape and Orbital Velocity"]:::key
    R --> TR["TRAP: g variation"]:::trap
    UG --> UG1["F = G m1 m2 / r2<br>G = 6.67 x 10^-11 N m2 / kg2<br>Newton's law — universal gravitational constant"]:::key
    EG --> EG1["g = 9.8 m/s2 at Earth's surface<br>g decreases with altitude (away from centre)<br>g slightly more at poles than equator"]:::key
    EG --> EG2["Weightlessness: g = 0 in free fall<br>Astronauts in orbit = free fall around Earth<br>Weight = mg; mass never changes"]:::key
    ES --> ES1["Escape velocity (Earth): 11.2 km/s<br>Orbital velocity (LEO ~300 km): 8 km/s<br>Moon escape velocity: 2.4 km/s (no atmosphere)"]:::key
    TR --> TR1["TRAP: g at poles GREATER than at equator<br>Earth is slightly flattened at poles<br>Poles closer to centre, equator bulges out"]:::trap""",

"## Chapter A4 — Work, Energy, Power": """\
flowchart TD
    R["WORK, ENERGY, POWER"]:::root
    R --> WK["Work"]:::key
    R --> EN["Energy Types"]:::key
    R --> PW["Power"]:::key
    R --> CE["Conservation"]:::key
    WK --> WK1["Work W = F x d x cos(theta)<br>Unit: Joule (J)<br>Work done = 0 if force perpendicular to motion"]:::key
    EN --> EN1["Kinetic Energy (KE) = 0.5 mv2<br>Potential Energy (PE) = mgh<br>Elastic PE: compressed spring"]:::key
    PW --> PW1["Power = Work / time = F x v<br>Unit: Watt (W); 1 W = 1 J/s<br>1 horsepower (hp) = 746 W"]:::key
    CE --> CE1["Conservation of Energy: KE + PE = constant<br>Energy cannot be created or destroyed<br>Only converted from one form to another"]:::key
    CE --> CE2["Efficiency = useful output / total input x 100%<br>No machine is 100% efficient<br>Losses due to friction + heat"]:::key""",

"## Chapter B1 — Pressure, Fluids, Buoyancy": """\
flowchart TD
    R["PRESSURE, FLUIDS, BUOYANCY"]:::root
    R --> PR["Pressure"]:::key
    R --> AR["Archimedes Principle"]:::key
    R --> PA["Pascal's Law"]:::key
    R --> TR["TRAP: Ice density vs water"]:::trap
    PR --> PR1["Pressure = Force / Area; unit: Pascal (Pa)<br>1 atmosphere = 101,325 Pa = 760 mm Hg<br>Pressure in fluid increases with depth"]:::key
    AR --> AR1["Buoyant force = weight of fluid displaced<br>Object floats if buoyant force >= weight<br>Density of object < density of fluid = floats"]:::key
    AR --> AR2["Density of water = 1000 kg/m3<br>Ship: large hull displaces massive water volume<br>Steel can float if hollow enough"]:::key
    PA --> PA1["Pressure in enclosed fluid transmitted equally<br>Hydraulic press: small force -> large force<br>Hydraulic brakes in cars use Pascal's Law"]:::key
    TR --> TR1["TRAP: Ice is LESS dense than liquid water<br>Ice floats: 9/10 below surface; 1/10 above<br>Water expands on freezing (unusual property)"]:::trap""",

"## Chapter B2 — Surface Tension, Viscosity, Capillarity": """\
flowchart TD
    R["SURFACE TENSION, VISCOSITY, CAPILLARITY"]:::root
    R --> ST["Surface Tension"]:::key
    R --> VI["Viscosity"]:::key
    R --> CA["Capillarity"]:::key
    ST --> ST1["Liquid surface acts like elastic membrane<br>Due to cohesive forces between molecules<br>Examples: water strider walking on water"]:::key
    ST --> ST2["Soap reduces surface tension (surfactant effect)<br>Hot water has lower surface tension than cold<br>Surface tension: Nm (Newtons per metre)"]:::key
    VI --> VI1["Viscosity: resistance to flow<br>Honey > oil > water > air<br>Viscosity of LIQUIDS decreases with temperature rise"]:::key
    VI --> VI2["Viscosity of GASES increases with temperature<br>Newton's law of viscosity: shear stress proportional to velocity gradient<br>Stokes' Law: drag force on sphere in viscous fluid"]:::key
    CA --> CA1["Capillarity: liquid rise/fall in narrow tubes<br>Water rises in glass (wetting liquid)<br>Mercury falls in glass (non-wetting)"]:::key
    CA --> CA2["Plants use capillarity: water rises in xylem<br>Towel absorbs water: capillary action<br>Height of rise inversely proportional to tube radius"]:::key""",

"## Chapter C1 — Temperature Scales": """\
flowchart TD
    R["TEMPERATURE SCALES"]:::root
    R --> SC["3 Main Scales"]:::key
    R --> CO["Conversions"]:::proc
    R --> KV["Key Values"]:::key
    SC --> SC1["Celsius: 0 C = ice point; 100 C = steam point<br>Fahrenheit: 32 F = ice; 212 F = steam<br>Kelvin: absolute scale; 0 K = absolute zero"]:::key
    CO --> CO1["F = (9/5) x C + 32<br>K = C + 273.15<br>-40 degrees: Celsius = Fahrenheit (they cross)"]:::proc
    KV --> KV1["Absolute zero: 0 K = -273.15 C<br>Body temperature: 37 C = 98.6 F = 310 K<br>Boiling point of water at sea level: 100 C = 212 F = 373 K"]:::key
    KV --> KV2["Freezing point of water: 0 C = 32 F = 273 K<br>Liquid nitrogen: -196 C = 77 K<br>Surface of Sun: ~5500 C"]:::key""",

"## Chapter C2 — Heat Transfer": """\
flowchart TD
    R["HEAT TRANSFER"]:::root
    R --> CO["Conduction"]:::key
    R --> CV["Convection"]:::key
    R --> RA["Radiation"]:::key
    R --> TR["TRAP: Which needs no medium?"]:::trap
    CO --> CO1["Conduction: heat transfer through solid<br>Molecule-to-molecule vibration<br>Best conductors: Silver > Copper > Gold > Aluminium"]:::key
    CO --> CO2["Poor conductors (insulators): wood, glass, rubber<br>Thermos flask: vacuum prevents conduction<br>Air is a poor conductor (used in double glazing)"]:::key
    CV --> CV1["Convection: heat transfer through fluid (liquid/gas)<br>Hot fluid rises (less dense); cold fluid sinks<br>Sea breeze + land breeze; monsoon mechanism"]:::key
    CV --> CV2["Convection currents drive plate tectonics<br>Mantle convection moves tectonic plates<br>Thermostat works on convection"]:::key
    RA --> RA1["Radiation: heat transfer without any medium<br>Electromagnetic waves (infrared)<br>Sun's energy reaches Earth through space via radiation"]:::key
    TR --> TR1["TRAP: Only RADIATION needs no medium<br>Conduction needs solid contact<br>Convection needs fluid (liquid or gas)"]:::trap""",

"## Chapter C3 — Specific Heat and Latent Heat": """\
flowchart TD
    R["SPECIFIC HEAT AND LATENT HEAT"]:::root
    R --> SH["Specific Heat Capacity"]:::key
    R --> LH["Latent Heat"]:::key
    R --> AP["Applications"]:::key
    R --> TR["TRAP: Phase change temperature"]:::trap
    SH --> SH1["Specific heat: energy to raise 1 kg by 1 C<br>Water = 4186 J/kg/C (highest of common substances)<br>This is why coastal areas have mild climate"]:::key
    SH --> SH2["Metals have LOW specific heat (heat up fast)<br>Iron = 450 J/kg/C; Copper = 385<br>Aluminium = 900; Lead = 128"]:::key
    LH --> LH1["Latent heat: energy for phase change<br>Temperature does NOT change during phase change<br>Added energy breaks or forms molecular bonds"]:::key
    LH --> LH2["Latent heat of fusion (ice to water): 334,000 J/kg<br>Latent heat of vaporisation (water to steam): 2,260,000 J/kg<br>Vaporisation needs MUCH more energy than melting"]:::key
    AP --> AP1["Sweating: evaporation absorbs body heat (cooling)<br>Steam burns worse than boiling water (releases latent heat)<br>Refrigerator: refrigerant evaporates + condenses in cycle"]:::key
    TR --> TR1["TRAP: During melting or boiling temperature is CONSTANT<br>Despite adding heat — energy breaks bonds<br>Only after all material changes phase does temp rise"]:::trap""",

"## Chapter C4 — Laws of Thermodynamics": """\
flowchart TD
    R["LAWS OF THERMODYNAMICS"]:::root
    R --> Z["Zeroth Law"]:::key
    R --> F["First Law"]:::key
    R --> S["Second Law"]:::key
    R --> T["Third Law"]:::key
    Z --> Z1["Zeroth Law: basis of thermometry<br>If A=B and B=C in temp then A=C<br>Thermal equilibrium = same temperature"]:::key
    F --> F1["First Law: Energy conservation<br>Q = delta_U + W<br>Heat added = internal energy rise + work done by system"]:::key
    S --> S1["Second Law: Entropy always increases<br>Heat flows naturally from hot to cold ONLY<br>No heat engine is 100% efficient"]:::key
    S --> S2["Carnot Engine: maximum possible efficiency<br>Efficiency = 1 - (T_cold / T_hot) [in Kelvin]<br>TRAP: Carnot efficiency is THEORETICAL maximum"]:::trap
    T --> T1["Third Law: Entropy = 0 at absolute zero<br>Absolute zero (0 K) is unattainable<br>Temperature approaches but cannot reach 0 K"]:::key""",

"## Chapter D1 — Sound": """\
flowchart TD
    R["SOUND"]:::root
    R --> NA["Nature of Sound"]:::key
    R --> SP["Speed in Different Media"]:::key
    R --> FR["Frequency Ranges"]:::key
    R --> DO["Doppler Effect and Echo"]:::key
    NA --> NA1["Longitudinal wave: compressions + rarefactions<br>Needs a MEDIUM (cannot travel in vacuum)<br>Moon: no sound because no atmosphere"]:::key
    SP --> SP1["Speed in air at 20 C: 343 m/s<br>Speed in water: 1480 m/s<br>Speed in steel: 5100 m/s<br>Sound faster in denser and more elastic media"]:::key
    FR --> FR1["Audible range: 20 Hz to 20,000 Hz<br>Infrasound: below 20 Hz (elephant, whale communication)<br>Ultrasound: above 20,000 Hz"]:::key
    FR --> FR2["Ultrasound uses: SONAR (depth/submarine detection)<br>Medical ultrasound (imaging body organs)<br>Cleaning delicate instruments; breaking kidney stones"]:::key
    DO --> DO1["Doppler Effect: source moving toward observer<br>--> higher frequency (higher pitch heard)<br>Source moving away --> lower frequency"]:::key
    DO --> DO2["Echo: minimum distance 17 m from reflecting wall<br>(at 20 C) to distinguish echo from original sound<br>Echo used in SONAR; bat navigation"]:::key""",

"## Chapter D2 — Light and Optics": """\
flowchart TD
    R["LIGHT AND OPTICS"]:::root
    R --> NA["Nature of Light"]:::key
    R --> RE["Reflection + Refraction"]:::key
    R --> LN["Lenses"]:::key
    R --> TI["Total Internal Reflection"]:::key
    R --> CO["Colour and Spectrum"]:::key
    NA --> NA1["Speed of light in vacuum: 3 x 10^8 m/s<br>Light year: distance light travels in 1 year<br>Light is electromagnetic wave; no medium needed"]:::key
    RE --> RE1["Reflection: angle of incidence = angle of reflection<br>Laws of reflection — both angles w.r.t. normal<br>Mirrors: plane (virtual/erect), concave (focus), convex (diverge)"]:::key
    RE --> RE2["Refraction: light bends entering different medium<br>Refractive index n = c/v (speed in vacuum / speed in medium)<br>Diamond high refractive index (2.42) = sparkle"]:::key
    LN --> LN1["Convex (converging) lens: focuses light<br>Uses: camera, eye (cornea+lens), magnifying glass, projector<br>Corrects hypermetropia (far-sightedness)"]:::key
    LN --> LN2["Concave (diverging) lens: spreads light<br>Uses: corrects myopia (near-sightedness)<br>Combined with convex in binoculars, telescopes"]:::key
    TI --> TI1["TIR: light goes dense-to-rare medium beyond critical angle<br>Uses: optical fibres (internet backbone), diamonds, mirages<br>Diamond critical angle: 24.4 degrees"]:::key
    CO --> CO1["White light splits into 7 colours in prism: VIBGYOR<br>Violet: shortest wavelength; Red: longest<br>Rainbow: water droplets = natural prisms"]:::key""",

"## Chapter E1 — Current Electricity": """\
flowchart TD
    R["CURRENT ELECTRICITY"]:::root
    R --> OH["Ohm's Law"]:::key
    R --> CI["Circuits"]:::key
    R --> EF["Heating Effect"]:::key
    R --> AC["AC vs DC"]:::key
    OH --> OH1["Ohm's Law: V = IR<br>Voltage = Current x Resistance<br>Unit: V=Volt, I=Ampere, R=Ohm"]:::key
    OH --> OH2["Power P = VI = I2 R = V2/R<br>Unit: Watt (W)<br>1 kWh = 1 unit of electricity = 3.6 MJ"]:::key
    CI --> CI1["Series circuit: R_total = R1 + R2 + R3<br>Same current through all; voltages add<br>Failure of one: whole circuit fails"]:::key
    CI --> CI2["Parallel circuit: 1/R_total = 1/R1 + 1/R2<br>Same voltage across all; currents add<br>Home wiring = parallel (each device independent)"]:::key
    EF --> EF1["Heating effect (Joule's Law): H = I2 R t<br>Used in: electric iron, heater, toaster, incandescent bulb<br>Fuse: low melting point alloy (Sn-Pb) protects circuit"]:::key
    AC --> AC1["AC: alternating current; direction changes<br>India: frequency 50 Hz; voltage 220-240 V<br>DC: direct current; constant direction (battery)"]:::key""",

"## Chapter E2 — Magnetism and Electromagnetic Induction": """\
flowchart TD
    R["MAGNETISM AND EMI"]:::root
    R --> MA["Magnetism Basics"]:::key
    R --> EL["Electromagnetism"]:::key
    R --> FA["Faraday's Law + Lenz's Law"]:::key
    R --> TR["Transformer"]:::key
    MA --> MA1["Magnetic poles: N and S — always in pairs<br>Like poles repel; unlike poles attract<br>Earth: geographic North = magnetic South pole"]:::key
    MA --> MA2["Magnetic field: created by moving charges (current)<br>Right-hand thumb rule: current direction -> field direction<br>Magnetic materials: Fe, Ni, Co (ferromagnetic)"]:::key
    EL --> EL1["Electromagnet: current-carrying coil + iron core<br>Magnetism disappears when current stops<br>Uses: electric bell, speaker, MRI machine, cranes"]:::key
    FA --> FA1["Faraday's Law: changing magnetic flux induces EMF<br>More flux change per second = larger EMF<br>Basis of all electric generators"]:::key
    FA --> FA2["Lenz's Law: induced current opposes the change causing it<br>Conservation of energy principle<br>TRAP: opposing does not mean cancelling"]:::trap
    TR --> TR1["Step-up transformer: increases voltage, decreases current<br>Step-down: decreases voltage, increases current<br>Power = VI constant (ideal transformer)<br>AC transmission at high voltage reduces energy loss"]:::key""",

"## Chapter F1 — Atomic Models": """\
flowchart TD
    R["ATOMIC MODELS"]:::root
    R --> TH["Thomson 1897"]:::date
    R --> RU["Rutherford 1911"]:::date
    R --> BO["Bohr 1913"]:::date
    R --> QM["Quantum Model"]:::key
    TH --> TH1["Plum pudding model<br>Electrons embedded in positive sphere<br>Like raisins in a pudding"]:::date
    RU --> RU1["Gold foil experiment (Geiger-Marsden)<br>Alpha particles: most pass through; few deflect<br>Conclusion: dense positive nucleus; electrons orbit"]:::date
    RU --> RU2["Rutherford's nuclear model flaws:<br>Accelerating electrons should emit radiation + spiral in<br>Couldn't explain atomic emission spectra"]:::key
    BO --> BO1["Bohr model: electrons in FIXED circular orbits<br>Each orbit has fixed energy — no radiation while in orbit<br>Emission/absorption when electron changes orbit"]:::date
    BO --> BO2["Explained hydrogen spectrum perfectly<br>Postulated by Niels Bohr (1913) — Nobel Prize 1922<br>Failed for multi-electron atoms"]:::date
    QM --> QM1["Modern quantum model: probability clouds (orbitals)<br>Heisenberg's Uncertainty Principle<br>Schrodinger wave equation describes electron position"]:::key""",

"## Chapter F2 — Subatomic Particles": """\
flowchart TD
    R["SUBATOMIC PARTICLES"]:::root
    R --> PA["Basic Particles"]:::key
    R --> IS["Isotopes, Isobars, Isotones"]:::key
    R --> TR["TRAP: Atomic number vs Mass number"]:::trap
    PA --> PA1["Proton: +1 charge; 1 amu; in nucleus<br>Neutron: 0 charge; 1 amu; in nucleus<br>Discovered by Chadwick 1932"]:::date
    PA --> PA2["Electron: -1 charge; 1/1836 amu; outside nucleus<br>Discovered by J.J. Thomson 1897<br>Atomic number Z = proton count = electron count (neutral atom)"]:::date
    IS --> IS1["Isotopes: same Z (protons), different A (mass number)<br>Same element, different neutrons<br>H-1 (protium), H-2 (deuterium), H-3 (tritium)"]:::key
    IS --> IS2["Isobars: same A, different Z (different elements)<br>Example: Argon-40 and Calcium-40<br>Isotones: same number of neutrons, different Z"]:::key
    TR --> TR1["TRAP: Atomic number Z = protons = identity of element<br>Mass number A = protons + neutrons<br>Neutrons = A - Z; can vary (isotopes)"]:::trap""",

"## Chapter F3 — Radioactivity": """\
flowchart TD
    R["RADIOACTIVITY"]:::root
    R --> DI["Discovery"]:::date
    R --> RA["Radiation Types"]:::key
    R --> HL["Half-Life"]:::key
    R --> US["Uses"]:::key
    DI --> DI1["Henri Becquerel: discovered 1896 (uranium salts)<br>Marie Curie: coined 'radioactivity'; discovered Po + Ra<br>Nobel Prize in Physics (1903) + Chemistry (1911)"]:::date
    RA --> RA1["Alpha (alpha): 2 protons + 2 neutrons (helium nucleus)<br>Charge: +2; mass: 4 amu; LOW penetration<br>Stopped by: paper or 5 cm air"]:::key
    RA --> RA2["Beta (beta): electron or positron<br>Charge: -1 or +1; medium penetration<br>Stopped by: 3 mm aluminium sheet"]:::key
    RA --> RA3["Gamma (gamma): electromagnetic radiation<br>No charge; no mass; HIGHEST penetration<br>Stopped by: thick lead or concrete"]:::key
    HL --> HL1["Half-life: time for half of radioactive atoms to decay<br>Independent of temperature, pressure, chemical state<br>Carbon-14 half-life = 5,730 years (used in dating)"]:::key
    US --> US1["Carbon-14 dating: archaeology (organic matter up to 50,000 yrs)<br>Uranium-238: age of rocks (billions of years)<br>Technetium-99m: medical imaging (gamma cameras)"]:::key""",

"## Chapter F4 — Nuclear Reactions": """\
flowchart TD
    R["NUCLEAR REACTIONS"]:::root
    R --> FI["Nuclear Fission"]:::key
    R --> FU["Nuclear Fusion"]:::key
    R --> CR["Chain Reaction"]:::key
    R --> TR["TRAP: Fission vs Fusion - which produces more energy per kg"]:::trap
    FI --> FI1["Fission: heavy nucleus splits into smaller nuclei + energy<br>U-235 + neutron -> Ba + Kr + 3 neutrons + energy<br>Controlled fission = nuclear power plant"]:::key
    FI --> FI2["Uncontrolled fission = atomic bomb (Little Boy used U-235)<br>Critical mass: minimum mass for self-sustaining chain reaction<br>Moderator (water/graphite) slows neutrons in reactor"]:::key
    FU --> FU1["Fusion: light nuclei combine into heavier nucleus + energy<br>H + H -> He + energy; happens in the SUN<br>Fusion releases MORE energy per kg than fission"]:::key
    FU --> FU2["Hydrogen bomb: fusion (much more powerful than atomic bomb)<br>Temperature needed: millions of degrees Celsius<br>ITER project (France): experimental fusion reactor"]:::key
    CR --> CR1["Chain reaction: each fission releases 2-3 neutrons<br>Neutrons trigger more fissions -- self-sustaining<br>Controlled: nuclear power; uncontrolled: nuclear bomb"]:::proc
    TR --> TR1["TRAP: Fusion produces MORE energy than fission per unit mass<br>But fusion is much harder to achieve in a controlled way<br>Fission: done in commercial reactors since 1950s"]:::trap""",

"## Chapter F5 — Semiconductors": """\
flowchart TD
    R["SEMICONDUCTORS"]:::root
    R --> CO["Conductors vs Insulators vs SC"]:::key
    R --> TY["Types of Semiconductors"]:::key
    R --> DE["Semiconductor Devices"]:::key
    CO --> CO1["Conductors: very low resistance; metals<br>Silver (best), Copper, Gold, Aluminium<br>Free electrons carry current easily"]:::key
    CO --> CO2["Insulators: very high resistance; no free electrons<br>Glass, rubber, wood, plastic, porcelain<br>Semiconductors: resistance between these two"]:::key
    TY --> TY1["Intrinsic SC: pure silicon or germanium<br>p-type: doped with boron (positive holes dominant)<br>n-type: doped with phosphorus (electrons dominant)"]:::key
    DE --> DE1["p-n junction diode: allows current one way only<br>Rectification: converts AC to DC<br>LED: emits light when forward biased"]:::key
    DE --> DE2["Transistor: p-n-p or n-p-n layers<br>Amplifies weak signals; acts as switch<br>Basis of ALL modern electronics + computers"]:::key
    DE --> DE3["Solar cell: photoelectric effect generates EMF<br>IC (Integrated Circuit): millions of transistors on chip<br>Moore's Law: IC transistor count doubles every 2 years"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# CHEMISTRY
# ─────────────────────────────────────────────────────────────────────────────
CHEMISTRY = {

"## Chapter A1 — States of Matter": """\
flowchart TD
    R["STATES OF MATTER"]:::root
    R --> S["Solid"]:::key
    R --> L["Liquid"]:::key
    R --> G["Gas"]:::key
    R --> CH["Phase Changes"]:::proc
    S --> S1["Fixed shape + volume<br>Particles vibrate in fixed positions<br>Highest density; incompressible"]:::key
    L --> L1["Fixed volume; fluid shape<br>Particles slide past each other<br>Less dense than solid (except water-ice)"]:::key
    G --> G1["No fixed shape or volume<br>Particles move randomly; far apart<br>Highly compressible; lowest density"]:::key
    G --> G2["Plasma: 4th state — ionised gas<br>Present in Sun, lightning, neon signs<br>Electrons separated from nuclei"]:::key
    CH --> CH1["Solid--heat-->Liquid: MELTING<br>Liquid--cool-->Solid: FREEZING<br>Liquid--heat-->Gas: VAPORISATION"]:::proc
    CH --> CH2["Gas--cool-->Liquid: CONDENSATION<br>Solid--heat-->Gas (no liquid): SUBLIMATION<br>Sublimation examples: iodine, camphor, dry ice (CO2)"]:::proc""",

"## Chapter A2 — Atomic Structure": """\
flowchart TD
    R["ATOMIC STRUCTURE"]:::root
    R --> BA["Basic Definitions"]:::key
    R --> EC["Electronic Configuration"]:::key
    R --> IS["Isotopes"]:::key
    R --> TR["TRAP: Valence electrons"]:::trap
    BA --> BA1["Atomic number (Z): number of protons<br>Mass number (A): protons + neutrons<br>Neutrons = A - Z"]:::key
    BA --> BA2["Neutral atom: protons = electrons<br>Ion: gained or lost electrons<br>Cation: lost e- (+); Anion: gained e- (-)"]:::key
    EC --> EC1["Shells: K(2) L(8) M(18) N(32)<br>Max electrons per shell = 2n2<br>Fill from innermost shell first (Aufbau principle)"]:::key
    EC --> EC2["Valence electrons: outermost shell electrons<br>Determine chemical reactivity<br>Noble gas: 8 valence electrons (octet) = stable"]:::key
    IS --> IS1["Isotopes: same Z (element), different A (mass)<br>H isotopes: protium (1), deuterium (2), tritium (3)<br>Carbon isotopes: C-12 (stable), C-14 (radioactive, dating)"]:::key
    TR --> TR1["TRAP: Valence electrons determine bonding ability<br>Group 1 = 1 valence e- (very reactive)<br>Group 18 = 8 valence e- (inert/noble gases)"]:::trap""",

"## Chapter B1 — From Mendeleev to Moseley": """\
flowchart TD
    R["THE PERIODIC TABLE"]:::root
    R --> ME["Mendeleev 1869"]:::date
    R --> MO["Moseley 1913"]:::date
    R --> ST["Structure"]:::key
    R --> TR["TRAP: Metals vs Non-metals position"]:::trap
    ME --> ME1["Arranged elements by ATOMIC MASS<br>Predicted missing elements (Eka-boron = Scandium)<br>Left gaps for undiscovered elements"]:::date
    ME --> ME2["Mendeleev's periodic law: properties are periodic<br>function of atomic mass<br>Anomalies: Ar-K, Co-Ni, Te-I reversed"]:::key
    MO --> MO1["Modern periodic law: properties periodic function<br>of ATOMIC NUMBER (not mass)<br>Fixed Mendeleev's anomalies"]:::date
    ST --> ST1["118 elements; 7 periods; 18 groups<br>Periods 1-3: short (2,8,8 elements)<br>Periods 4-7: long (18-32 elements)"]:::key
    ST --> ST2["s-block: Groups 1-2 (alkali + alkaline earth metals)<br>p-block: Groups 13-18 (includes non-metals, metalloids)<br>d-block: Groups 3-12 (transition metals)<br>f-block: Lanthanides + Actinides (bottom two rows)"]:::key
    TR --> TR1["TRAP: Metals on LEFT; non-metals on RIGHT<br>Metalloids (staircase): B, Si, Ge, As, Sb, Te, At<br>Noble gases: Group 18 (all inert)"]:::trap""",

"## Chapter C1 — How Atoms Bond Together": """\
flowchart TD
    R["CHEMICAL BONDING"]:::root
    R --> IO["Ionic Bond"]:::key
    R --> CO["Covalent Bond"]:::key
    R --> ME["Metallic Bond"]:::key
    R --> TR["TRAP: Properties differ by bond type"]:::trap
    IO --> IO1["Ionic bond: metal GIVES electrons to non-metal<br>Forms cations (+) and anions (-)<br>Example: NaCl (Na gives e- to Cl)"]:::key
    IO --> IO2["Properties: crystalline solid; high melting point<br>Conducts electricity ONLY when dissolved or molten<br>Soluble in water; insoluble in organic solvents"]:::key
    CO --> CO1["Covalent bond: both atoms SHARE electrons<br>Non-metal + non-metal<br>Example: H2O, CO2, NH3, CH4"]:::key
    CO --> CO2["Single bond: 1 shared pair (H-H)<br>Double bond: 2 shared pairs (O=O)<br>Triple bond: 3 shared pairs (N=N)"]:::key
    ME --> ME1["Metallic bond: metal cations in sea of free electrons<br>Explains: conductivity, lustre, ductility, malleability<br>No directional bond: metals can be bent/drawn"]:::key
    TR --> TR1["TRAP: Ionic conducts only when melted or dissolved<br>Covalent compounds generally don't conduct electricity<br>Graphite is COVALENT but conducts (exception)"]:::trap""",

"## Chapter C2 — Types of Chemical Reactions": """\
flowchart TD
    R["TYPES OF CHEMICAL REACTIONS"]:::root
    R --> CO["Combination"]:::key
    R --> DE["Decomposition"]:::key
    R --> SD["Single Displacement"]:::key
    R --> DD["Double Displacement"]:::key
    R --> OX["Oxidation-Reduction"]:::key
    CO --> CO1["A + B -> AB<br>Example: CaO + H2O -> Ca(OH)2<br>Also: C + O2 -> CO2 (combustion is also combination)"]:::key
    DE --> DE1["AB -> A + B (breaks compound)<br>Thermal: CaCO3 -> CaO + CO2 (heating)<br>Electrolytic: 2H2O -> 2H2 + O2 (electrolysis)"]:::key
    SD --> SD1["A + BC -> AC + B (more reactive replaces less reactive)<br>Fe + CuSO4 -> FeSO4 + Cu<br>Zn + 2HCl -> ZnCl2 + H2"]:::key
    DD --> DD1["AB + CD -> AD + CB (ions exchange)<br>NaCl + AgNO3 -> AgCl(precipitate) + NaNO3<br>Neutralisation: acid + base -> salt + water"]:::key
    OX --> OX1["OIL RIG mnemonic:<br>OIL: Oxidation Is Loss (of electrons)<br>RIG: Reduction Is Gain (of electrons)"]:::key
    OX --> OX2["Oxidising agent: accepts electrons (gets reduced)<br>Reducing agent: donates electrons (gets oxidised)<br>Redox always occur together in one reaction"]:::key""",

"## Chapter D1 — Three Theories of Acids and Bases": """\
flowchart TD
    R["THEORIES OF ACIDS AND BASES"]:::root
    R --> AR["Arrhenius Theory"]:::key
    R --> BL["Bronsted-Lowry Theory"]:::key
    R --> LW["Lewis Theory"]:::key
    AR --> AR1["Arrhenius acid: gives H+ ions in water<br>Arrhenius base: gives OH- ions in water<br>Example: HCl -> H+ + Cl-; NaOH -> Na+ + OH-"]:::key
    AR --> AR2["Limitation: only aqueous solutions<br>Cannot explain NH3 acting as base (no OH-)"]:::key
    BL --> BL1["Bronsted-Lowry acid: PROTON DONOR (H+)<br>Bronsted-Lowry base: PROTON ACCEPTOR<br>More general than Arrhenius"]:::key
    BL --> BL2["NH3 + H2O -> NH4+ + OH-<br>NH3 = base (accepts H+); H2O = acid (donates H+)<br>Conjugate acid-base pairs"]:::key
    LW --> LW1["Lewis acid: electron pair ACCEPTOR<br>Lewis base: electron pair DONOR<br>Most general theory — includes non-proton reactions"]:::key
    LW --> LW2["BF3 = Lewis acid (empty orbital accepts e- pair)<br>NH3 = Lewis base (lone pair to donate)<br>BF3 + NH3 -> BF3-NH3 complex"]:::key""",

"## Chapter D2 — The pH Scale": """\
flowchart TD
    R["THE pH SCALE"]:::root
    R --> DE["Definition"]:::key
    R --> VA["pH Values to Know"]:::key
    R --> BL["Blood pH — Critical"]:::trap
    DE --> DE1["pH = -log of hydrogen ion concentration H+<br>pH scale: 0 to 14<br>pH < 7 = acidic; pH 7 = neutral; pH > 7 = basic (alkaline)"]:::key
    VA --> VA1["Stomach acid (HCl): pH 1-2<br>Lemon juice: pH 2-3; Vinegar: pH 3<br>Pure water: pH 7; Milk: pH 6.5-7"]:::key
    VA --> VA2["Baking soda (NaHCO3): pH 8-9<br>Soap: pH 9-10; Bleach: pH 11-12<br>NaOH solution: pH 13-14"]:::key
    BL --> BL1["Blood pH: 7.35-7.45 (slightly ALKALINE)<br>Fall below 7.35 = Acidosis (dangerous)<br>Rise above 7.45 = Alkalosis (dangerous)"]:::trap
    BL --> BL2["TRAP: Students often say blood is neutral (7)<br>Blood is slightly ALKALINE (7.4)<br>Maintained by bicarbonate buffer system"]:::trap""",

"## Chapter D3 — Indicators (Learn the Colour Changes)": """\
flowchart TD
    R["pH INDICATORS"]:::root
    R --> LI["Litmus — universal in exams"]:::key
    R --> OT["Other Common Indicators"]:::key
    R --> UN["Universal Indicator"]:::key
    LI --> LI1["Litmus: natural dye from lichens<br>RED in ACID (pH < 7)<br>BLUE in BASE (pH > 7)"]:::key
    LI --> LI2["Litmus paper: most common test in labs<br>Blue litmus turns red = acid<br>Red litmus turns blue = base"]:::key
    OT --> OT1["Phenolphthalein:<br>COLOURLESS in acid<br>PINK/MAGENTA in base (pH > 8.2)"]:::key
    OT --> OT2["Methyl orange:<br>RED in strong acid<br>ORANGE in neutral<br>YELLOW in base"]:::key
    OT --> OT3["Turmeric (natural indicator):<br>YELLOW in neutral/acid<br>RED/BROWN in base<br>TRAP: not standard lab indicator"]:::trap
    UN --> UN1["Universal indicator: mixture of several indicators<br>Shows rainbow of colours across pH 0-14<br>Red=0-1, Orange=2-3, Yellow=4-5, Green=6-7<br>Blue=8-9, Violet=10-11, Magenta=12-14"]:::key""",

"## Chapter D4 — Common Acids and Their Uses": """\
flowchart LR
    R["COMMON ACIDS AND USES"]:::root
    R --> A1["Hydrochloric Acid (HCl)"]:::key
    R --> A2["Sulphuric Acid (H2SO4)"]:::key
    R --> A3["Nitric Acid (HNO3)"]:::key
    R --> A4["Other Acids"]:::key
    A1 --> A1a["Gastric juice (stomach acid): digestion<br>pH 1-2; kills bacteria in food<br>Industrial: cleaning metals (pickling), PVC"]:::key
    A2 --> A2a["King of Acids: most widely used industrial acid<br>Car batteries (lead-acid); fertilizers (superphosphate)<br>Manufacture of explosives (TNT); paper, paints"]:::key
    A3 --> A3a["Fertilizers (ammonium nitrate)<br>Explosives (TNT, nitroglycerine with H2SO4)<br>Gold and platinum dissolved by Aqua Regia (HNO3 + HCl)"]:::key
    A4 --> A4a["Acetic acid CH3COOH: vinegar (5% solution)<br>Carbonic acid H2CO3: fizzy drinks; blood pH buffering<br>Citric acid: lemons, oranges; food preservative"]:::key""",

"## Chapter D5 — Common Bases and Their Uses": """\
flowchart LR
    R["COMMON BASES AND USES"]:::root
    R --> B1["NaOH — Caustic Soda"]:::key
    R --> B2["Ca(OH)2 — Slaked Lime"]:::key
    R --> B3["Mg(OH)2 — Milk of Magnesia"]:::key
    R --> B4["Others"]:::key
    B1 --> B1a["NaOH: manufacture of soap + detergents<br>Paper + textile industry<br>Drain cleaners (reacts with fat)"]:::key
    B2 --> B2a["Ca(OH)2: plaster + whitewash (walls)<br>Water treatment (soften hard water)<br>Mortar in construction"]:::key
    B3 --> B3a["Mg(OH)2: antacid (neutralises stomach acid)<br>Treats heartburn + indigestion<br>Mild base; safe to consume"]:::key
    B4 --> B4a["NH4OH (ammonia solution): fertilizer; cleaning agent<br>Bleaching powder Ca(OCl)Cl: water treatment + bleaching<br>Baking soda NaHCO3: leavening in baking + fire extinguisher"]:::key""",

"## Chapter D6 — Salts and Their pH": """\
flowchart TD
    R["SALTS AND THEIR pH"]:::root
    R --> FO["Formation"]:::proc
    R --> TY["Salt Types by pH"]:::key
    R --> KS["Key Salts to Know"]:::key
    FO --> FO1["Salt = acid + base neutralisation<br>Strong acid + Strong base -> neutral salt<br>Weak acid + Strong base -> basic salt"]:::proc
    TY --> TY1["Strong acid + Strong base: neutral (pH 7)<br>Example: NaCl (table salt)<br>HCl + NaOH -> NaCl + H2O"]:::key
    TY --> TY2["Weak acid + Strong base: ALKALINE salt<br>Example: Na2CO3 (washing soda), pH ~11<br>Strong acid + Weak base: ACIDIC salt (NH4Cl, pH ~5)"]:::key
    KS --> KS1["NaCl (common salt): table salt; neutral<br>Na2CO3.10H2O (washing soda): water softening; alkaline<br>NaHCO3 (baking soda): leavening; slightly alkaline"]:::key
    KS --> KS2["CaSO4.0.5H2O (Plaster of Paris): moulds + casts<br>KAl(SO4)2.12H2O (Alum): water purification (flocculation)<br>CaCO3 (limestone): building material; chalk"]:::key""",

"## Chapter E1 — Properties of Metals": """\
flowchart TD
    R["PROPERTIES OF METALS"]:::root
    R --> PH["Physical Properties"]:::key
    R --> EX["Extremes — Exam Favourites"]:::key
    R --> TR["TRAP: Hardest substance"]:::trap
    PH --> PH1["Good conductors of heat + electricity<br>Lustrous (shiny) appearance<br>Malleable (can be hammered flat); ductile (drawn into wires)"]:::key
    PH --> PH2["High melting point (generally)<br>Exception: Mercury (only liquid metal at room temp)<br>Gallium: melts at 30 C (melts in hand)"]:::key
    EX --> EX1["Best conductor of electricity: SILVER<br>2nd: Copper (used in wiring — cheaper)<br>Best conductor of heat: also Silver"]:::key
    EX --> EX2["Most malleable + ductile metal: GOLD<br>Lightest metal: LITHIUM<br>Heaviest metal: OSMIUM<br>Hardest metal: CHROMIUM"]:::key
    EX --> EX3["Most abundant metal in Earth's crust: ALUMINIUM<br>2nd most abundant element overall: Silicon<br>Most reactive metal: Caesium (or Francium)"]:::key
    TR --> TR1["TRAP: Hardest NATURAL substance = Diamond (not a metal)<br>Hardest METAL = Chromium<br>Diamond is carbon (non-metal) in cubic lattice structure"]:::trap""",

"## Chapter E2 — Activity Series (Reactivity Series)": """\
flowchart TD
    R["ACTIVITY SERIES OF METALS"]:::root
    R --> OR["Order of Reactivity"]:::key
    R --> RU["Rules for Reactions"]:::key
    R --> TR["TRAP: Thermite reaction"]:::trap
    OR --> OR1["K > Na > Ca > Mg > Al > Zn > Fe<br>> Pb > H > Cu > Hg > Ag > Au > Pt<br>Decreasing reactivity left to right"]:::key
    OR --> OR2["Above H: displace H2 from dilute acid<br>Above Ca: even displace H2 from cold water<br>Below H (Cu, Hg, Ag, Au): do NOT react with dilute acids"]:::key
    RU --> RU1["More reactive metal displaces less reactive from salt solution<br>Fe + CuSO4 -> FeSO4 + Cu (Fe more reactive than Cu)<br>Cu + FeSO4 -> NO REACTION (Cu less reactive than Fe)"]:::key
    RU --> RU2["Gold + Platinum: most stable; no tarnishing<br>Noble metals; very hard to react<br>Used in jewellery and electrical contacts"]:::key
    TR --> TR1["Thermite reaction: Al + Fe2O3 -> Al2O3 + Fe + heat<br>Al is more reactive than Fe (displaces it)<br>Used in WELDING of railway tracks (exothermic)"]:::trap""",

"## Chapter E3 — Extraction of Metals": """\
flowchart TD
    R["EXTRACTION OF METALS"]:::root
    R --> ME["Method depends on reactivity"]:::proc
    R --> IR["Iron: Blast Furnace"]:::key
    R --> AL["Aluminium: Electrolysis"]:::key
    R --> TR["TRAP: Ore names"]:::trap
    ME --> ME1["Low reactivity (Cu, Hg, Ag): simple heating or<br>reduction with CO/carbon<br>High reactivity (Al, Na, K, Mg): electrolysis required"]:::proc
    IR --> IR1["Iron ore: Hematite (Fe2O3) or Magnetite (Fe3O4)<br>Blast furnace: iron ore + coke + limestone + hot air<br>Pig iron -> cast iron -> wrought iron -> steel"]:::key
    IR --> IR2["Coke: reduces Fe2O3 (C + O2 -> CO2; CO2 + C -> CO)<br>CO reduces iron: Fe2O3 + 3CO -> 2Fe + 3CO2<br>Limestone: removes impurities as slag (CaSiO3)"]:::key
    AL --> AL1["Bauxite (Al2O3.2H2O): aluminium ore<br>Purified to alumina (Al2O3) by Bayer process<br>Electrolysis of molten alumina (Hall-Heroult)"]:::key
    AL --> AL2["Electrolysis: Al deposited at cathode<br>Carbon anode burns off (oxygen attacks it)<br>High energy process (expensive)"]:::key
    TR --> TR1["TRAP: Iron ore = Hematite (Fe2O3)<br>Aluminium ore = Bauxite<br>Copper ore = Chalcopyrite (CuFeS2)<br>Zinc ore = Zinc blende (ZnS)"]:::trap""",

"## Chapter E4 — Corrosion and Prevention": """\
flowchart TD
    R["CORROSION AND PREVENTION"]:::root
    R --> RU["Rusting of Iron"]:::key
    R --> CO["Conditions for Rusting"]:::key
    R --> PR["Prevention Methods"]:::key
    R --> TR["TRAP: Galvanising metal"]:::trap
    RU --> RU1["Rust = hydrated iron oxide: Fe2O3.xH2O<br>Reddish-brown; flaky; weaker than iron<br>A slow REDOX reaction (iron oxidises)"]:::key
    CO --> CO1["Rusting requires BOTH oxygen AND water (moisture)<br>Salt water speeds rusting (electrolyte)<br>NO rust in completely dry air OR oxygen-free water"]:::key
    PR --> PR1["Painting: barrier between iron and air/water<br>Oiling/greasing: lubricant barrier<br>Electroplating: coat with less reactive metal (Sn, Cr, Ni)"]:::key
    PR --> PR2["Galvanising: coat iron with ZINC<br>Zinc oxidises first (sacrificial anode protection)<br>Even if Zn coating scratched, iron still protected"]:::key
    PR --> PR3["Alloying: stainless steel = Fe + Cr + Ni<br>Cr forms protective oxide layer on surface<br>Most effective long-term solution"]:::key
    TR --> TR1["TRAP: Galvanising uses ZINC not tin<br>Zinc is sacrificial (more reactive than iron)<br>Tin plating (food cans): once scratched, iron rusts fast"]:::trap""",

"## Chapter F1 — Why Carbon Is Special": """\
flowchart TD
    R["WHY CARBON IS SPECIAL"]:::root
    R --> TE["Tetravalency"]:::key
    R --> CA["Catenation"]:::key
    R --> AL["Allotropes of Carbon"]:::key
    TE --> TE1["Carbon has 4 valence electrons<br>Can form 4 bonds (single, double, triple)<br>Most versatile bonding capability of any element"]:::key
    CA --> CA1["Catenation: C-C bonds form long chains<br>No other element chains so extensively<br>Basis of millions of organic compounds"]:::key
    CA --> CA2["Organic chemistry: ~10 million carbon compounds<br>vs only ~100,000 non-carbon compounds<br>Life is carbon-based: proteins, DNA, carbs, fats"]:::key
    AL --> AL1["Diamond: all sp3 bonds; 3D tetrahedral lattice<br>Hardest natural substance; transparent; insulator<br>Used in cutting tools, jewellery"]:::key
    AL --> AL2["Graphite: sp2 bonds; layered hexagonal sheets<br>Slippery lubricant (layers slide); dark grey<br>Conducts electricity (free electrons between layers)"]:::key
    AL --> AL3["Fullerene (C60 Buckminsterfullerene): soccer ball shape<br>60 carbon atoms; discovered 1985 (Nobel 1996)<br>Carbon nanotubes: strongest material per unit weight"]:::date""",

"## Chapter F2 — Hydrocarbons — The Three Series": """\
flowchart TD
    R["HYDROCARBONS"]:::root
    R --> AK["Alkanes (Saturated)"]:::key
    R --> AE["Alkenes (Unsaturated)"]:::key
    R --> AY["Alkynes (Unsaturated)"]:::key
    R --> TR["TRAP: -ane vs -ene vs -yne"]:::trap
    AK --> AK1["General formula: CnH(2n+2)<br>Single bonds only (SATURATED)<br>Methane CH4, Ethane C2H6, Propane C3H8, Butane C4H10"]:::key
    AK --> AK2["Properties: least reactive; stable<br>Fuels: natural gas (CH4), LPG (C3-C4), petrol (C5-C8)<br>Undergo substitution reactions (not addition)"]:::key
    AE --> AE1["General formula: CnH2n<br>One DOUBLE bond (UNSATURATED)<br>Ethene C2H4 = ethylene (fruit ripening hormone)"]:::key
    AE --> AE2["Properties: more reactive than alkanes<br>Undergo ADDITION reactions (double bond opens)<br>Ethylene used to ripen bananas commercially"]:::key
    AY --> AY1["General formula: CnH(2n-2)<br>One TRIPLE bond (UNSATURATED)<br>Ethyne C2H2 = acetylene (welding + cutting)"]:::key
    TR --> TR1["TRAP: -ane = alkane (saturated, single bonds)<br>-ene = alkene (one double bond)<br>-yne = alkyne (one triple bond)<br>Saturated = more H; Unsaturated = fewer H"]:::trap""",

"## Chapter F3 — Functional Groups": """\
flowchart LR
    R["FUNCTIONAL GROUPS IN ORGANIC CHEMISTRY"]:::root
    R --> OH["Alcohol (-OH)"]:::key
    R --> CH["Aldehyde (-CHO)"]:::key
    R --> CO["Ketone (-CO-)"]:::key
    R --> CA["Carboxylic Acid (-COOH)"]:::key
    R --> ES["Ester (-COO-)"]:::key
    OH --> OH1["Ethanol C2H5OH: drinking alcohol<br>Antiseptic; solvent; fuel additive<br>Fermentation: glucose -> ethanol + CO2 (yeast)"]:::key
    CH --> CH1["Formaldehyde HCHO: preservative (formalin)<br>Acetaldehyde CH3CHO: oxidation product of ethanol<br>Pungent smell; reducing agent"]:::key
    CO --> CO1["Acetone CH3COCH3: nail polish remover; solvent<br>Propanone = simplest ketone<br>Distinctive fruity smell"]:::key
    CA --> CA1["Acetic acid CH3COOH: vinegar (5% solution)<br>Formic acid HCOOH: ant sting (formic = ant)<br>Citric acid: lemons"]:::key
    ES --> ES1["Formed by alcohol + carboxylic acid (condensation)<br>Pleasant fruity smell; artificial flavours<br>Ethyl acetate: nail polish remover; solvent"]:::key""",

"## Chapter F4 — Fuels": """\
flowchart TD
    R["FUELS"]:::root
    R --> CO["Coal Types"]:::key
    R --> PE["Petroleum Products"]:::key
    R --> GA["LPG and CNG"]:::key
    R --> CV["Calorific Values"]:::key
    CO --> CO1["Peat -> Lignite -> Bituminous -> Anthracite<br>Carbon content INCREASES left to right<br>Anthracite: best; 90%+ carbon; least smoke"]:::key
    CO --> CO2["Bituminous: most common; coke made from it<br>Lignite (brown coal): low carbon; high moisture<br>Peat: barely compacted; lowest carbon"]:::key
    PE --> PE1["Petroleum = crude oil: mixture of hydrocarbons<br>Refinery: fractional distillation by boiling point<br>LPG -> petrol -> naphtha -> kerosene -> diesel -> fuel oil -> bitumen"]:::key
    PE --> PE2["Petrol (gasoline): C5-C8; vehicles<br>Kerosene: C10-C16; jet fuel, lamps<br>Diesel: C14-C20; trucks, buses, trains"]:::key
    GA --> GA1["LPG: mainly propane + butane<br>Mercaptan (thioethanol) added for smell (LPG is odourless)<br>Used: cooking gas in India"]:::key
    GA --> GA2["CNG: mainly methane (CH4)<br>Cleaner than petrol/diesel (less pollutants)<br>Used in Delhi buses, auto-rickshaws"]:::key
    CV --> CV1["Calorific value: heat produced per kg of fuel<br>Hydrogen: 142 MJ/kg (highest)<br>LPG: ~47 MJ/kg; Petrol: 45; Diesel: 45; Coal: 25-35"]:::key""",

"## Chapter G1 — Key Concepts": """\
flowchart TD
    R["KEY CHEMISTRY CONCEPTS FOR GA"]:::root
    R --> CF["Common Chemical Formulae"]:::key
    R --> LA["Lab Tests and Observations"]:::key
    R --> CO["Corrosion and Combustion Summary"]:::key
    CF --> CF1["Water H2O; Common salt NaCl<br>Baking soda NaHCO3; Washing soda Na2CO3<br>Vinegar CH3COOH; Bleaching powder Ca(OCl)Cl"]:::key
    CF --> CF2["Limestone CaCO3; Slaked lime Ca(OH)2<br>Quicklime CaO; Plaster of Paris CaSO4.0.5H2O<br>Alum KAl(SO4)2.12H2O; Marble = CaCO3"]:::key
    LA --> LA1["Blue litmus turns red = ACID present<br>Red litmus turns blue = BASE present<br>Limewater turns milky = CO2 present"]:::key
    LA --> LA2["Glowing splint relights = OXYGEN<br>Burning splint makes pop sound = HYDROGEN<br>Turmeric turns red-brown = BASE present"]:::key
    CO --> CO1["Complete combustion: fuel + excess O2 -> CO2 + H2O<br>Incomplete combustion: insufficient O2 -> CO (toxic)<br>CO: colourless + odourless + poisonous gas"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────
ENVIRONMENT = {

"## Chapter A1 — The Ecosystem": """\
flowchart TD
    R["THE ECOSYSTEM"]:::root
    R --> CO["Components"]:::proc
    R --> TR["Trophic Levels + 10% Rule"]:::key
    R --> PY["Ecological Pyramids"]:::key
    CO --> CO1["Abiotic: temperature, light, water, soil, wind<br>Biotic: producers, consumers, decomposers<br>Ecosystem = abiotic + biotic together"]:::proc
    CO --> CO2["Producers: autotrophs (plants, algae, phytoplankton)<br>Consumers: heterotrophs (primary, secondary, tertiary)<br>Decomposers: bacteria + fungi (break dead matter)"]:::proc
    TR --> TR1["Lindeman's 10% Law (1942):<br>Only 10% of energy transfers to next trophic level<br>90% lost as heat, respiration, etc."]:::key
    TR --> TR2["Implication: shorter food chains = more energy<br>Vegetarians extract more energy from ecosystem<br>Top carnivores get only 0.1% of primary production"]:::key
    PY --> PY1["Pyramid of Energy: ALWAYS UPRIGHT<br>Cannot be inverted (energy always lost at each level)<br>Most reliable ecological pyramid"]:::key
    PY --> PY2["Pyramid of Biomass: can be inverted in aquatic<br>Phytoplankton (small mass) supports zooplankton (larger)<br>Pyramid of Number: can be inverted (1 tree, 1000 insects)"]:::key""",

"## Chapter A2 — Biogeochemical Cycles": """\
flowchart TD
    R["BIOGEOCHEMICAL CYCLES"]:::root
    R --> CA["Carbon Cycle"]:::proc
    R --> NI["Nitrogen Cycle"]:::proc
    R --> WA["Water Cycle"]:::proc
    CA --> CA1["CO2 removed from air: photosynthesis<br>CO2 returned to air: respiration + combustion + decomposition<br>Deforestation + fossil fuels: excess CO2 -> climate change"]:::proc
    CA --> CA2["Carbon sinks: forests, oceans, soil<br>Carbon sources: fossil fuels, deforestation<br>Ocean: largest carbon reservoir"]:::key
    NI --> NI1["N2 (78% of air) cannot be used directly<br>Nitrogen fixation: Rhizobium (legume roots) + Azotobacter<br>NH3 -> NO2 -> NO3 (nitrification by Nitrosomonas, Nitrobacter)"]:::proc
    NI --> NI2["Plants absorb NO3-; animals eat plants<br>Decomposers: return N to soil as NH3<br>Denitrification: Pseudomonas converts NO3 back to N2"]:::proc
    WA --> WA1["Evaporation (water -> water vapour)<br>Transpiration: water vapour from plants (also contributes)<br>Condensation -> clouds -> Precipitation"]:::proc
    WA --> WA2["Surface runoff -> rivers -> ocean<br>Infiltration: ground water recharge<br>Transpiration contributes ~10% of water cycle"]:::key""",

"## Chapter B1 — Levels and Importance of Biodiversity": """\
flowchart TD
    R["BIODIVERSITY — LEVELS AND IMPORTANCE"]:::root
    R --> LV["3 Levels of Biodiversity"]:::key
    R --> VA["Value of Biodiversity"]:::key
    R --> IN["India's Biodiversity Facts"]:::key
    LV --> LV1["Genetic diversity: variation in genes within a species<br>Allows adaptation + evolution<br>Example: different rice varieties"]:::key
    LV --> LV2["Species diversity: number of different species<br>in an area (species richness)<br>Tropical regions highest species diversity"]:::key
    LV --> LV3["Ecosystem diversity: variety of habitats and ecosystems<br>Forests, wetlands, grasslands, deserts, coral reefs<br>India has all major ecosystem types"]:::key
    VA --> VA1["Direct values: food, timber, medicine, fibres<br>80% of world's population uses plants for primary healthcare<br>25% of western medicines derived from tropical plants"]:::key
    VA --> VA2["Indirect values: ecosystem services<br>Pollination, water purification, climate regulation, soil formation<br>Option value: future discoveries"]:::key
    IN --> IN1["India: 17th megadiverse country<br>2.4% of Earth's area; 8.1% of species<br>4 biodiversity hotspots; 90,000 animal species"]:::key""",

"## Chapter B2 — Biodiversity Hotspots": """\
flowchart TD
    R["BIODIVERSITY HOTSPOTS"]:::root
    R --> CR["Criteria to Qualify"]:::key
    R --> GL["Global Hotspots"]:::key
    R --> IN["India's 4 Hotspots"]:::key
    CR --> CR1["Must have 1500+ endemic plant species<br>AND must have lost more than 70% of original habitat<br>Endemic: found ONLY in that region, nowhere else"]:::key
    GL --> GL1["36 biodiversity hotspots globally (as of 2024)<br>Cover only 2.4% of Earth's land area<br>But contain 60%+ of world's plant, animal, fungi species"]:::key
    IN --> IN1["1. Eastern Himalayas (includes NE India)<br>2. Western Ghats + Sri Lanka (Sahyadri)<br>3. Indo-Burma (NE India + Myanmar border)"]:::key
    IN --> IN2["4. Sundaland (Andaman-Nicobar Islands segment)<br>Western Ghats: biodiversity richest area in India<br>Anamudi (2695m) = highest peak in Western Ghats"]:::key
    IN --> IN3["TRAP: India's hotspots are parts of GLOBAL hotspots<br>Western Ghats is 1 of 36 globally<br>Not independent of the global classification"]:::trap""",

"## Chapter B3 — IUCN Red List Categories": """\
flowchart TD
    R["IUCN RED LIST CATEGORIES"]:::root
    R --> OR["Order from Most to Least Threatened"]:::key
    R --> IN["Indian Examples"]:::key
    R --> TR["TRAP: EW vs EX"]:::trap
    OR --> OR1["EX — Extinct: no living individuals known<br>EW — Extinct in Wild: only in captivity/cultivation<br>CR — Critically Endangered: extremely high risk"]:::key
    OR --> OR2["EN — Endangered: very high risk<br>VU — Vulnerable: high risk<br>NT — Near Threatened: close to qualifying VU"]:::key
    OR --> OR3["LC — Least Concern: widespread + abundant<br>DD — Data Deficient: insufficient data<br>NE — Not Evaluated: not yet assessed"]:::key
    IN --> IN1["CR examples: Great Indian Bustard, Gharial<br>EN examples: Bengal Tiger, Asiatic Lion, Snow Leopard<br>VU examples: Indian Rhinoceros, Sloth Bear, Dhole"]:::key
    IN --> IN2["National Animal: Bengal Tiger (EN)<br>National Bird: Indian Peafowl (Peacock) — LC<br>National Aquatic Animal: Gangetic Dolphin (EN)"]:::key
    TR --> TR1["TRAP: EX = completely gone from Earth<br>EW = extinct in WILD; survives in zoo/captive<br>Example EW: Red List has very few; Scimitar Oryx was EW"]:::trap""",

"## Chapter B4 — Key Endangered Species in India": """\
flowchart LR
    R["KEY ENDANGERED SPECIES IN INDIA"]:::root
    R --> MA["Mammals"]:::key
    R --> BI["Birds"]:::key
    R --> RE["Reptiles"]:::key
    MA --> MA1["Bengal Tiger (EN): 3167 tigers (2022 census)<br>53 Tiger Reserves; Corbett, Ranthambore, Sundarbans<br>Project Tiger since 1973"]:::key
    MA --> MA2["Asiatic Lion (EN): ONLY in Gir Forest, Gujarat<br>Population: ~600+ (2022 census)<br>Project Lion: reintroduction to Kuno NP (Madhya Pradesh)"]:::key
    MA --> MA3["Indian Rhinoceros (VU): 70% at Kaziranga, Assam<br>Population: ~4000+; horn poaching biggest threat<br>Project Rhinoceros; UNESCO WHS"]:::key
    MA --> MA4["Snow Leopard (VU): Himalayas; very elusive<br>Project Snow Leopard: 2009<br>Red Panda (EN): NE Himalayas; bamboo forest"]:::key
    BI --> BI1["Great Indian Bustard (CR): Rajasthan + Gujarat<br>Fewer than 150 remaining; power lines threat<br>Project Great Indian Bustard 2015"]:::key
    RE --> RE1["Gharial (CR): Chambal River, Girwa River<br>Narrow snout; fish-eater; critically endangered<br>Mugger crocodile: VU; Indian Cobra: LC"]:::key""",

"## Chapter C1 — Types of Protected Areas": """\
flowchart TD
    R["PROTECTED AREAS IN INDIA"]:::root
    R --> NP["National Parks"]:::key
    R --> WS["Wildlife Sanctuaries"]:::key
    R --> BR["Biosphere Reserves"]:::key
    R --> TR["TRAP: Which allows what activity?"]:::trap
    NP --> NP1["National Parks: complete protection<br>NO human activity (no grazing, logging, cultivation)<br>106 National Parks in India; cover 1.23% of area"]:::key
    NP --> NP2["First NP in India: Corbett (1936, Uttarakhand)<br>Smallest NP: South Button Island (Andaman Nicobar)<br>Largest NP: Hemis (Ladakh, high altitude)"]:::key
    WS --> WS1["Wildlife Sanctuaries: some human activities allowed<br>Grazing + forestry may be permitted<br>565+ Wildlife Sanctuaries in India"]:::key
    WS --> WS2["Difference from NP: human settlement may exist<br>Less strict protection than National Parks<br>Private ownership of land may continue"]:::key
    BR --> BR1["Biosphere Reserves: 3 zones<br>Core zone: no human activity (most protected)<br>Buffer zone: limited research/tourism<br>Transition zone: settlements, farming allowed"]:::key
    TR --> TR1["TRAP: National Park = strictest (no human use)<br>Wildlife Sanctuary = moderate (some human use)<br>Biosphere Reserve = largest; has human zones"]:::trap""",

"## Chapter C2 — Key National Parks — Must-Know Facts": """\
flowchart LR
    R["KEY NATIONAL PARKS — EXAM FACTS"]:::root
    R --> N1["Corbett NP"]:::date
    R --> N2["Kaziranga NP"]:::key
    R --> N3["Gir Forest NP"]:::key
    R --> N4["Sundarbans NP"]:::key
    R --> N5["Manas NP"]:::key
    R --> N6["Ranthambore NP"]:::key
    N1 --> N1a["Established 1936 (first NP in India)<br>Uttarakhand; Jim Corbett (British hunter-naturalist)<br>Bengal Tiger; Elephant; Gharial"]:::date
    N2 --> N2a["Assam; UNESCO World Heritage Site 1985<br>70% of world's Indian One-horned Rhinoceros<br>Also: elephants, wild buffalo, Bengal Tiger"]:::key
    N3 --> N3a["Gujarat; only home of Asiatic Lion (600+)<br>UNESCO WHS 2023 (Gir Forest)<br>Proposed second home: Kuno NP, Madhya Pradesh"]:::key
    N4 --> N4a["West Bengal; UNESCO WHS 1987<br>Largest mangrove forest in the world<br>Bengal Tiger; Gangetic Dolphin; Irrawaddy Dolphin"]:::key
    N5 --> N5a["Assam; UNESCO WHS; Project Tiger Reserve<br>Golden Langur (EN) + Pygmy Hog (CR) found here<br>Red Panda; Hispid Hare; Bengal Florican"]:::key
    N6 --> N6a["Rajasthan; famous for Tiger sightings<br>Sariska also a Tiger Reserve in Rajasthan<br>Historical Ranthambore Fort inside the park"]:::key""",

"## Chapter C3 — Biosphere Reserves (India's 18)": """\
flowchart TD
    R["BIOSPHERE RESERVES OF INDIA"]:::root
    R --> ST["Statistics"]:::key
    R --> FI["First Established"]:::date
    R --> UN["UNESCO Recognised (12)"]:::key
    R --> TR["TRAP: BR vs National Park"]:::trap
    ST --> ST1["Total: 18 Biosphere Reserves in India<br>12 recognised under UNESCO MAB Programme<br>Cover 5.33% of India's total geographical area"]:::key
    FI --> FI1["First BR: Nilgiri Biosphere Reserve 1986<br>(Tamil Nadu + Kerala + Karnataka)<br>Largest BR: Pachmarhi (Satpura range, MP)"]:::date
    UN --> UN1["UNESCO recognised 12 (out of 18):<br>Nilgiri, Gulf of Mannar, Sundarbans<br>Nanda Devi, Nokrek, Pachmarhi"]:::key
    UN --> UN2["Simlipal, Achanakmar-Amarkantak<br>Great Nicobar, Agasthyamalai<br>Khangchendzonga, Panna (most recently)"]:::key
    TR --> TR1["TRAP: Biosphere Reserve is largest category<br>Can include National Parks and Sanctuaries within it<br>Example: Nilgiri BR includes Mudumalai + Wayanad + Bandipur"]:::trap""",

"## Chapter C4 — Ramsar Sites (Wetlands)": """\
flowchart TD
    R["RAMSAR WETLAND SITES"]:::root
    R --> CO["Convention Background"]:::date
    R --> IN["India's Ramsar Sites"]:::key
    R --> KS["Key Sites to Know"]:::key
    CO --> CO1["Ramsar Convention: signed 1971 in Ramsar, Iran<br>HQ: Gland, Switzerland<br>Focuses on conservation of wetland ecosystems"]:::date
    CO --> CO2["Ramsar = 'Wetland of International Importance'<br>Criteria: rare ecosystem; supports waterfowl; unique biodiversity<br>World: 2400+ sites; 169 countries"]:::key
    IN --> IN1["India: 75 Ramsar sites (2023) — most in South Asia<br>First 2 Ramsar sites in India (1981):<br>Chilika Lake (Odisha) + Keoladeo NP (Rajasthan)"]:::date
    IN --> IN2["Largest Ramsar site: Sundarbans (WB)<br>Smallest Ramsar site: Renuka Lake (HP)<br>Most Ramsar sites in one state: Uttar Pradesh (10+)"]:::key
    KS --> KS1["Chilika Lake: Asia's largest brackish water lagoon<br>Irrawaddy dolphins + migratory birds<br>Flamingo Festival held here"]:::key
    KS --> KS2["Sambhar Lake (Rajasthan): largest inland saline lake<br>Flamingo sightings; near Jaipur<br>Wular Lake (J&K): largest freshwater lake in India"]:::key""",

"## Chapter D1 — Air Pollution": """\
flowchart TD
    R["AIR POLLUTION"]:::root
    R --> PO["Pollutants"]:::key
    R --> AQ["AQI Scale"]:::key
    R --> SM["Smog Types"]:::key
    R --> TR["TRAP: Primary vs Secondary pollutants"]:::trap
    PO --> PO1["Primary pollutants: directly from source<br>CO (incomplete combustion), SO2 (coal/industry)<br>NOx (vehicles), PM2.5/PM10, hydrocarbons"]:::key
    PO --> PO2["Secondary pollutants: formed in atmosphere<br>Tropospheric ozone (O3): photochemical<br>PAN (peroxyacetyl nitrate): eye irritant"]:::key
    AQ --> AQ1["AQI scale: 0-500<br>0-50: GOOD (green); 51-100: Satisfactory<br>101-200: Moderate; 201-300: Poor"]:::key
    AQ --> AQ2["301-400: Very Poor; 401-500: Severe<br>India uses AQI for 8 pollutants<br>PM2.5 (fine particles) most dangerous"]:::key
    SM --> SM1["London smog (Classic smog): SO2 + fog + soot<br>Cold; humid; during winter inversions<br>London 1952: 4000 deaths in 4 days"]:::date
    SM --> SM2["Photochemical smog (Los Angeles type): NOx + VOC + sunlight<br>-> ozone + PAN; warm + sunny climates<br>Delhi winter: mix of both types"]:::key
    TR --> TR1["TRAP: Ground-level ozone = POLLUTANT (bad)<br>Stratospheric ozone = PROTECTS (good)<br>Same molecule, different location = opposite effect"]:::trap""",

"## Chapter D2 — Water Pollution": """\
flowchart TD
    R["WATER POLLUTION"]:::root
    R --> SO["Major Sources"]:::key
    R --> BO["BOD and DO"]:::key
    R --> EU["Eutrophication"]:::key
    R --> TR["TRAP: Ganga pollution"]:::trap
    SO --> SO1["Sewage: pathogens, BOD, nutrients<br>Industrial effluents: heavy metals (Hg, Pb, Cd, Cr)<br>Agricultural runoff: pesticides (DDT), fertilizers (nitrates)"]:::key
    SO --> SO2["Thermal pollution: hot water from power plants<br>Reduces DO (dissolved oxygen) in water<br>Oil spills: film prevents sunlight, kills marine life"]:::key
    BO --> BO1["BOD (Biochemical Oxygen Demand):<br>More organic waste = more BOD = more polluted<br>Clean water: BOD < 1 mg/L; Polluted: BOD > 5 mg/L"]:::key
    BO --> BO2["DO (Dissolved Oxygen): measure of water health<br>Fish need DO > 6 mg/L<br>DO decreases when BOD increases"]:::key
    EU --> EU1["Eutrophication: excess nutrients (N, P) in water<br>Causes: algal bloom -> oxygen depletion -> fish die<br>Agricultural runoff main cause in India"]:::key
    TR --> TR1["TRAP: Ganga pollution sources:<br>Industrial (leather tanneries Kanpur + paper mills)<br>Domestic sewage + religious practices + cremation"]:::trap""",

"## Chapter D3 — Solid Waste, Noise, Soil": """\
flowchart TD
    R["SOLID WASTE, NOISE AND SOIL POLLUTION"]:::root
    R --> SW["Solid Waste Types"]:::key
    R --> NO["Noise Pollution"]:::key
    R --> SP["Soil Pollution"]:::key
    R --> BM["Biomagnification"]:::key
    SW --> SW1["E-waste: fastest growing; cadmium, lead, mercury<br>Biomedical waste: colour-coded bags<br>Yellow=infectious, Red=recyclable, Blue=glassware"]:::key
    SW --> SW2["Plastic: persistent; microplastics now in ocean + food chain<br>Municipal Solid Waste: 62 million tonnes/year in India<br>Less than 60% collected; less than 15% processed"]:::key
    NO --> NO1["Sound measured in decibels (dB)<br>Industrial limit: 75 dB; Residential: 45 dB (day); 35 dB (night)<br>Above 85 dB: hearing damage over time"]:::key
    SP --> SP1["Pesticides: DDT persists in soil decades<br>Heavy metals: cadmium, lead from industries<br>Plastic bags: prevent water + air movement in soil"]:::key
    BM --> BM1["Biomagnification: concentration INCREASES up food chain<br>DDT: algae 0.003 ppb -> fish 2 ppb -> eagle 25 ppb<br>Top predators most affected"]:::key""",

"## Chapter E1 — Greenhouse Gases": """\
flowchart TD
    R["GREENHOUSE GASES"]:::root
    R --> GE["Greenhouse Effect — Natural vs Enhanced"]:::key
    R --> GH["Main Greenhouse Gases + GWP"]:::key
    R --> IM["Impacts of Climate Change"]:::key
    GE --> GE1["Natural greenhouse effect: ESSENTIAL for life<br>Without it: Earth would be -18 C (too cold)<br>GHGs trap outgoing infrared radiation"]:::key
    GE --> GE2["Enhanced greenhouse effect: human-caused<br>Excess CO2, CH4, N2O from industries + agriculture<br>Global average temp has risen 1.2 C since 1850"]:::date
    GH --> GH1["CO2 (carbon dioxide): baseline GWP = 1<br>Main source: fossil fuels, deforestation<br>Remains in atmosphere 100-300 years"]:::key
    GH --> GH2["CH4 (methane): GWP = 25 (25x more powerful than CO2)<br>Sources: cattle, rice paddy, landfill, natural gas leaks<br>N2O (nitrous oxide): GWP = 298; fertilizers + fossil fuels"]:::key
    GH --> GH3["CFCs: GWP = thousands; now banned under Montreal Protocol<br>Water vapour: most abundant GHG (natural)<br>HFCs: replacements for CFCs; GWP = 1000s"]:::key
    IM --> IM1["Rising sea levels (melting ice + thermal expansion)<br>Extreme weather: floods, droughts, cyclones more intense<br>Coral bleaching; species extinction; food insecurity"]:::key""",

"## Chapter E2 — Climate Treaties Timeline": """\
flowchart TD
    R["CLIMATE TREATIES TIMELINE"]:::root
    R --> S1["1970s-80s"]:::date
    R --> S2["1990s"]:::date
    R --> S3["2000s-2010s"]:::date
    R --> S4["2020s"]:::date
    S1 --> S1a["Stockholm Conference 1972: first global env. conference<br>UNEP (UN Environment Programme) established<br>World Environment Day: June 5"]:::date
    S1 --> S1b["Montreal Protocol 1987: phase out CFCs<br>Most successful global env. treaty<br>Ozone hole slowly healing"]:::date
    S2 --> S2a["Rio Earth Summit 1992 (UNCED):<br>3 conventions: UNFCCC, CBD, UNCCD<br>Brundtland definition of Sustainable Development"]:::date
    S2 --> S2b["Kyoto Protocol 1997: binding targets for developed nations<br>37 industrialised countries; 2 commitment periods<br>USA did NOT ratify; Canada withdrew"]:::date
    S3 --> S3a["Copenhagen COP15 (2009): failed to get binding agreement<br>Cancun COP16 (2010): Green Climate Fund established<br>Paris Agreement COP21 (2015): all countries; 1.5 C target"]:::date
    S4 --> S4a["Glasgow COP26 (2021): phase DOWN coal (not phase out)<br>Kunming-Montreal GBF 2022: 30x30 (protect 30% land by 2030)<br>Dubai COP28 (2023): transition away from fossil fuels"]:::date""",

"## Chapter E3 — India's Climate Action": """\
flowchart TD
    R["INDIA'S CLIMATE ACTION"]:::root
    R --> ND["NDC Targets"]:::key
    R --> RE["Renewable Energy"]:::key
    R --> PA["Policy + Agreements"]:::key
    ND --> ND1["India's NDC (2022 update) targets:<br>50% electricity from non-fossil fuels by 2030<br>Reduce carbon intensity by 45% vs 2005 level"]:::key
    ND --> ND2["Create additional 1 billion tonne carbon sink<br>(through forests + tree cover) by 2030<br>Net Zero target: 2070"]:::key
    RE --> RE1["Solar: India 3rd largest solar capacity globally<br>Target: 500 GW renewable by 2030 (300 GW solar)<br>International Solar Alliance (ISA): co-founded by India"]:::key
    RE --> RE2["Green Hydrogen Mission: 5 million tonnes by 2030<br>PM Surya Ghar Muft Bijli: 1 crore households<br>PLI scheme: production-linked incentive for solar"]:::key
    PA --> PA1["NAPCC: National Action Plan on Climate Change<br>8 national missions incl. solar, water, Himalayan ecosystem<br>State Action Plans on Climate Change (SAPCCs)"]:::key
    PA --> PA2["India stance: common but differentiated responsibilities<br>Developed nations must take lead + provide finance<br>India: low per capita emissions; development right"]:::key""",

"## Chapter F1 — Key Environmental Acts (Chronological)": """\
flowchart TD
    R["KEY ENVIRONMENTAL ACTS"]:::root
    R --> A1["Pre-1980 Acts"]:::date
    R --> A2["1980s Acts"]:::date
    R --> A3["Post-1990 Acts"]:::date
    A1 --> A1a["Wildlife Protection Act 1972: 6 schedules<br>Schedule I: highest protection (tigers, rhinos)<br>Hunting of Schedule I species: up to 7 years"]:::date
    A1 --> A1b["Water (Prevention + Control of Pollution) Act 1974<br>Established Central + State Pollution Control Boards<br>Forest Conservation Act 1980: no diversion without approval"]:::date
    A2 --> A2a["Air (Prevention + Control of Pollution) Act 1981<br>Environment (Protection) Act 1986: umbrella legislation<br>After Bhopal gas disaster December 1984"]:::date
    A2 --> A2b["Bhopal gas tragedy: MIC (methyl isocyanate) leak<br>Union Carbide plant; 3 December 1984<br>Worst industrial disaster; 15,000+ deaths"]:::date
    A3 --> A3a["Biological Diversity Act 2002: access + benefit sharing<br>National Green Tribunal (NGT) Act 2010<br>E-waste Management Rules 2016"]:::key""",

"## Chapter F2 — Wildlife Protection Act 1972 — Schedules": """\
flowchart TD
    R["WILDLIFE PROTECTION ACT 1972 — SCHEDULES"]:::root
    R --> S1["Schedule I"]:::key
    R --> S2S3["Schedules II and III"]:::key
    R --> S5S6["Schedules V and VI"]:::key
    R --> AM["2022 Amendment"]:::date
    S1 --> S1a["HIGHEST protection: no hunting at all<br>Tiger, Elephant, Lion, Rhino, Snow Leopard<br>Gharial, Gangetic Dolphin, Golden Langur, Great Indian Bustard"]:::key
    S1 --> S1b["Punishment: minimum 3 years; up to 7 years<br>Fine up to Rs 25,000 (amended amounts vary)<br>Repeat offenders: minimum 7 years"]:::key
    S2S3 --> S2S3a["Schedule II: high protection; lesser penalty than I<br>Schedule III: specified animals; hunting allowed with license<br>Schedule IV: lesser protection; license required"]:::key
    S5S6 --> S5S6a["Schedule V: vermin (can be hunted)<br>Common crow, fruit bat, common rat, mice<br>Schedule VI: protected plants (6 species originally)"]:::key
    AM --> AM1["WPA Amendment 2022 consolidated to 4 schedules<br>Also incorporated CITES (Convention on Int'l Trade<br>in Endangered Species) into Indian law"]:::date""",

"## Chapter F3 — Key Institutions": """\
flowchart TD
    R["KEY ENVIRONMENTAL INSTITUTIONS"]:::root
    R --> CP["CPCB"]:::key
    R --> NG["NGT"]:::key
    R --> MO["MoEFCC"]:::key
    R --> IN["International Bodies"]:::key
    CP --> CP1["CPCB: Central Pollution Control Board<br>Established 1974 under Water Act<br>HQ: Delhi; Under MoEFCC; sets standards"]:::key
    CP --> CP2["SPCB: State Pollution Control Boards<br>Implement CPCB standards at state level<br>Issue consents (No Objection Certificates) to industry"]:::key
    NG --> NG1["NGT: National Green Tribunal<br>Established under NGT Act 2010<br>HQ: Delhi; handles environmental cases"]:::key
    NG --> NG2["Faster than regular courts for env. cases<br>Chairperson: retired SC or HC judge<br>Expert members + judicial members"]:::key
    MO --> MO1["MoEFCC: Ministry of Environment, Forest and Climate Change<br>Controls Wildlife Protection Act, Forest Conservation Act<br>Environment (Protection) Act 1986"]:::key
    IN --> IN1["UNEP: UN Environment Programme; HQ Nairobi, Kenya<br>IUCN: HQ Gland, Switzerland; Red List<br>WWF: World Wide Fund for Nature; HQ Gland"]:::key""",
}


# ─────────────────────────────────────────────────────────────────────────────
# SCI_TECH
# ─────────────────────────────────────────────────────────────────────────────
SCI_TECH = {

"## Chapter A1 — The Story of ISRO: From Coconut Groves to Cosmos": """\
flowchart TD
    R["ISRO — INDIA'S SPACE PROGRAMME"]:::root
    R --> FO["Foundation + Milestones"]:::date
    R --> VE["Key Launch Vehicles"]:::key
    R --> MI["Major Missions"]:::date
    R --> TR["TRAP: First satellite vs first rocket"]:::trap
    FO --> FO1["ISRO founded: 1969 by Dr Vikram Sarabhai<br>HQ: Bengaluru (Space Commission + DOS)<br>First rocket launch: 1963 from Thumba (Thiruvananthapuram)"]:::date
    FO --> FO2["First satellite: Aryabhata (April 19, 1975)<br>Launched by Soviet Kosmos-3M rocket<br>Name: after Indian mathematician Aryabhata"]:::date
    VE --> VE1["PSLV (Polar Satellite Launch Vehicle):<br>Workhorse; 4-stage alternating solid+liquid fuel<br>58+ successful missions; most reliable"]:::key
    VE --> VE2["GSLV Mk III / LVM3 (Launch Vehicle Mark 3):<br>Heavy-lift; 4 tonnes to GTO<br>Launched Chandrayaan-3, OneWeb satellites"]:::key
    MI --> MI1["Chandrayaan-3: landed August 23, 2023<br>SOUTH POLE lunar landing (world FIRST)<br>Vikram lander + Pragyan rover; 14 days on Moon"]:::date
    MI --> MI2["Mangalyaan (MOM 2013-14):<br>1st Asian country to reach Mars<br>1st country to succeed in FIRST attempt"]:::date
    MI --> MI3["Gaganyaan: India's crewed space mission<br>Target: 2025-2026; 3 astronauts; 400 km orbit<br>Crew: Prasanth Balakrishnan + 3 others (Vyommitras)"]:::date
    TR --> TR1["TRAP: First ROCKET = 1963 (American Nike-Apache)<br>First INDIAN SATELLITE = Aryabhata 1975<br>First ISRO rocket = SLV-3 1980 (Rohini into orbit)"]:::trap""",

"## Chapter A2 — Private Space & Global Context": """\
flowchart TD
    R["PRIVATE SPACE AND GLOBAL CONTEXT"]:::root
    R --> IS["IN-SPACe + Indian Private Sector"]:::date
    R --> GL["Global Space Players"]:::key
    R --> ST["Space Stations + Telescopes"]:::key
    IS --> IS1["IN-SPACe: Indian National Space Promotion and<br>Authorization Centre; established 2020<br>Regulates private space companies in India"]:::date
    IS --> IS2["NSIL: NewSpace India Limited (ISRO commercial arm)<br>Agnikul Cosmos + Skyroot Aerospace (Indian startups)<br>Pixxel: Indian earth observation satellite startup"]:::key
    GL --> GL1["SpaceX (Elon Musk): Falcon 9 (reusable)<br>Starship (largest rocket ever); Crew Dragon (ISS)<br>Starlink: global internet via 5000+ LEO satellites"]:::key
    GL --> GL2["NASA: US; Artemis mission (Moon return)<br>ESA: European Space Agency; HQ Paris<br>JAXA: Japan; Roscosmos: Russia; CNSA: China"]:::key
    ST --> ST1["ISS: International Space Station<br>Since 1998; 400 km altitude<br>Partners: USA, Russia, Japan, ESA, Canada"]:::key
    ST --> ST2["James Webb Space Telescope (JWST): 2021<br>L2 point; 1.5M km from Earth<br>Infrared; 100x more powerful than Hubble"]:::date""",

"## Chapter B1 — DRDO and the Missile Story": """\
flowchart TD
    R["DRDO AND MISSILES"]:::root
    R --> DR["DRDO Overview"]:::date
    R --> IG["IGMDP Missiles"]:::key
    R --> OT["Other Key Weapons Systems"]:::key
    R --> TR["TRAP: BrahMos is NOT DRDO alone"]:::trap
    DR --> DR1["DRDO: Defence Research and Development Organisation<br>Founded 1958; HQ New Delhi<br>52 labs; 30,000+ scientists + staff"]:::date
    DR --> DR2["APJ Abdul Kalam: Missile Man of India<br>Led IGMDP (Integrated Guided Missile Development Programme)<br>Later became 11th President of India (2002-2007)"]:::date
    IG --> IG1["IGMDP launched 1983; five missiles:<br>P — Prithvi (surface-to-surface; 150-500 km)<br>A — Agni (ballistic; Agni-V = 5000+ km; ICBM range)"]:::key
    IG --> IG2["T — Trishul (short-range naval air defense)<br>A — Akash (air defense; Mach 2.5; 25 km range)<br>N — Nag (anti-tank guided missile; third generation)"]:::key
    OT --> OT1["Astra: beyond-visual-range air-to-air; 100+ km<br>Tejas: light combat aircraft (HAL + DRDO)<br>Arjun: main battle tank"]:::key
    TR --> TR1["TRAP: BrahMos = India-Russia JOINT venture<br>DRDO (India) + NPO Mashinostroyenia (Russia)<br>World's fastest operational cruise missile: Mach 2.8"]:::trap""",

"## Chapter C1 — Bhabha's Three-Stage Plan": """\
flowchart TD
    R["INDIA'S NUCLEAR PROGRAMME"]:::root
    R --> HB["Homi J. Bhabha"]:::date
    R --> TS["Three-Stage Plan"]:::proc
    R --> FA["Key Facilities"]:::key
    R --> PO["Pokhran Tests"]:::date
    HB --> HB1["Homi J. Bhabha: Father of India's nuclear programme<br>Founded TIFR (1945) and BARC (1954)<br>Died 1966 in Air India crash near Mont Blanc"]:::date
    TS --> TS1["Stage 1: PHWRs (Pressurised Heavy Water Reactors)<br>Fuel: natural uranium-238; Moderator: heavy water<br>Produces plutonium-239 as byproduct"]:::proc
    TS --> TS2["Stage 2: Fast Breeder Reactors (FBRs)<br>Fuel: Pu-239 from Stage 1; breeds more Pu<br>India's first FBR: Kalpakkam, Tamil Nadu"]:::proc
    TS --> TS3["Stage 3: Advanced reactors using Thorium-232<br>India has world's LARGEST thorium reserves<br>Thorium -> U-233 (fissile material for reactor)"]:::proc
    FA --> FA1["BARC: Bhabha Atomic Research Centre, Mumbai<br>NPCIL: Nuclear Power Corporation of India Limited<br>Operating plants: Tarapur, Rawatbhata, Kalpakkam, Kaiga, Kudankulam"]:::key
    PO --> PO1["Pokhran-I (Smiling Buddha): May 18, 1974<br>PM Indira Gandhi; first nuclear test<br>Pokhran-II (Operation Shakti): May 11-13, 1998<br>PM Vajpayee; India declared nuclear weapon state"]:::date""",

"## Chapter D1 — Computer Fundamentals": """\
flowchart TD
    R["COMPUTER FUNDAMENTALS"]:::root
    R --> GE["Computer Generations"]:::date
    R --> BN["Binary System + Storage"]:::key
    R --> CO["Key Components"]:::key
    R --> IN["Internet Basics"]:::key
    GE --> GE1["1st Gen (1940-55): Vacuum tubes; ENIAC, UNIVAC<br>2nd Gen (1955-65): Transistors; smaller + faster<br>3rd Gen (1965-75): Integrated Circuits (ICs)"]:::date
    GE --> GE2["4th Gen (1975-): Microprocessors (VLSI); PCs<br>5th Gen (now): AI, quantum, neuromorphic<br>Each gen: smaller, faster, cheaper, less power"]:::date
    BN --> BN1["Binary: base-2 number system (0 and 1)<br>1 bit = smallest unit (0 or 1)<br>8 bits = 1 Byte; 1024 Bytes = 1 KB"]:::key
    BN --> BN2["1 MB = 1024 KB; 1 GB = 1024 MB<br>1 TB = 1024 GB; 1 PB = 1024 TB<br>RAM: volatile; ROM: non-volatile"]:::key
    CO --> CO1["CPU: ALU (arithmetic) + CU (control) + Registers<br>RAM: Random Access Memory (temporary, fast)<br>HDD/SSD: permanent storage"]:::key
    IN --> IN1["ARPANET (1969): predecessor of internet<br>TCP/IP: fundamental protocol of the internet<br>HTTP/HTTPS: web browsing protocol; SMTP: email"]:::key""",

"## Chapter D2 — Artificial Intelligence & Emerging Tech": """\
flowchart TD
    R["AI AND EMERGING TECHNOLOGIES"]:::root
    R --> AI["Artificial Intelligence"]:::key
    R --> BC["Blockchain"]:::key
    R --> QC["Quantum Computing"]:::key
    R --> OT["Other Tech"]:::key
    AI --> AI1["AI: machines simulating human intelligence<br>ML: machine learns from data patterns<br>DL (Deep Learning): neural networks; multiple layers"]:::key
    AI --> AI2["Generative AI: creates text/image/audio<br>LLM (Large Language Model): ChatGPT, Gemini, Claude<br>Computer Vision: image recognition; face unlock"]:::key
    BC --> BC1["Blockchain: distributed ledger technology<br>Immutable (cannot alter past records)<br>Decentralised: no single controlling authority"]:::key
    BC --> BC2["Bitcoin: first cryptocurrency (Satoshi Nakamoto 2008)<br>Smart contracts: self-executing code on blockchain<br>Web3: decentralised internet vision"]:::key
    QC --> QC1["Qubits: quantum bits (superposition: 0 AND 1 simultaneously)<br>Quantum supremacy: Google Sycamore 2019<br>Exponentially faster for certain problems"]:::key
    OT --> OT1["5G: sub-1ms latency; 20 Gbps peak; IoT backbone<br>IoT: Internet of Things; smart devices connected<br>AR/VR: Augmented Reality (overlay) / Virtual Reality (immersive)"]:::key""",

"## Chapter E1 — Genetic Engineering Primer": """\
flowchart TD
    R["GENETIC ENGINEERING"]:::root
    R --> RT["Recombinant DNA Technology"]:::proc
    R --> GM["GMOs in India"]:::key
    R --> CR["CRISPR"]:::date
    R --> PC["PCR"]:::date
    RT --> RT1["Restriction enzymes: cut DNA at specific sequences<br>Ligase: join DNA fragments (molecular glue)<br>Vector (plasmid): carries foreign DNA into host cell"]:::proc
    RT --> RT2["Steps: Extract DNA -> Cut with restriction enzyme<br>Insert into vector -> Transform into host (bacteria)<br>Select + grow -> harvest product"]:::proc
    GM --> GM1["Bt Cotton: Bacillus thuringiensis toxin gene<br>Makes cotton resistant to bollworm pests<br>Only approved GM crop in India (2002)"]:::key
    GM --> GM2["Bt Brinjal: approved then suspended (moratorium 2010)<br>Golden Rice: beta-carotene (Vitamin A); not approved<br>GM Mustard (HT Mustard): approved 2022 by GEAC"]:::key
    CR --> CR1["CRISPR-Cas9: gene editing tool; 2012<br>Jennifer Doudna + Emmanuelle Charpentier<br>Nobel Prize Chemistry 2020"]:::date
    PC --> PC1["PCR: Polymerase Chain Reaction<br>Amplifies tiny DNA sample millions of times<br>Kary Mullis (Nobel 1993); used in COVID testing + forensics"]:::date""",

"## Chapter F1 — India's Energy Transition": """\
flowchart TD
    R["INDIA'S ENERGY TRANSITION"]:::root
    R --> CO["Coal (Current Reality)"]:::key
    R --> RE["Renewables (Target)"]:::key
    R --> NE["Nuclear Energy"]:::key
    R --> TR["TRAP: India is 3rd largest emitter"]:::trap
    CO --> CO1["Coal: 55% of India's electricity (2024)<br>India: 2nd largest coal consumer globally<br>Largest reserves: Jharkhand, Chhattisgarh, Odisha"]:::key
    CO --> CO2["Just Transition challenge: 300,000+ coal workers<br>Coal India Limited (CIL): world's largest coal producer<br>India NOT committed to phasing OUT coal (only phase down)"]:::key
    RE --> RE1["Renewable target: 500 GW by 2030<br>Solar: 300 GW; Wind: 60 GW<br>India: 3rd largest solar capacity globally (2024)"]:::key
    RE --> RE2["ISA (International Solar Alliance): co-founded India + France<br>HQ: Gurugram (near Delhi)<br>Green Hydrogen Mission: 5 million tonnes by 2030"]:::key
    NE --> NE1["Nuclear: 22 reactors; 7,480 MW capacity<br>NPCIL operates all nuclear power plants<br>Kudankulam (Russia collaboration) = largest plant"]:::key
    TR --> TR1["TRAP: India = 3rd largest emitter (absolute)<br>But India has VERY LOW per capita emissions<br>Per capita: India 40th percentile globally"]:::trap""",

"## Chapter G1 — Medical Missions & Innovations": """\
flowchart TD
    R["MEDICAL MISSIONS AND INNOVATIONS"]:::root
    R --> AI["AIIMS + ICMR"]:::date
    R --> VA["COVID-19 Vaccines (India)"]:::date
    R --> DI["Digital Health"]:::key
    R --> TR["TRAP: Covaxin vs Covishield"]:::trap
    AI --> AI1["AIIMS: All India Institute of Medical Sciences<br>First AIIMS: New Delhi 1956<br>Now 23 AIIMS across India (expansion 2003+)"]:::date
    AI --> AI2["ICMR: Indian Council of Medical Research<br>Founded 1911 (oldest medical research body in India)<br>Co-developed Covaxin with Bharat Biotech"]:::date
    VA --> VA1["Covaxin: Bharat Biotech + ICMR<br>Inactivated virus vaccine (whole virus killed)<br>100% indigenous; WHO EUL approved Nov 2021"]:::date
    VA --> VA2["Covishield: Serum Institute + AstraZeneca (Oxford)<br>Viral vector vaccine (chimpanzee adenovirus)<br>Largest single manufacturer in world (SII Pune)"]:::date
    DI --> DI1["e-Sanjeevani: world's largest telemedicine platform<br>200+ million consultations (as of 2023)<br>MoHFW initiative; connects doctors + patients remotely"]:::key
    DI --> DI2["Ayushman Bharat: health ID + PM-JAY insurance<br>ABHA (Ayushman Bharat Health Account): health ID<br>DigiLocker: store + share health documents"]:::key
    TR --> TR1["TRAP: Covaxin = INDIAN vaccine; inactivated virus<br>Covishield = SERUM INSTITUTE + AstraZeneca; viral vector<br>Both approved for use in India in 2021"]:::trap""",

"## Chapter H1 — Physics Essentials (General Awareness flavour)": """\
flowchart TD
    R["PHYSICS FOR GA SECTION"]:::root
    R --> SP["Speed Values"]:::key
    R --> TE["Technologies based on Physics"]:::key
    R --> DI["Discoveries to Know"]:::date
    SP --> SP1["Speed of sound in air: 343 m/s at 20 C<br>Speed of light in vacuum: 3 x 10^8 m/s<br>Sound in water: 1480 m/s; in steel: 5100 m/s"]:::key
    TE --> TE1["SONAR: uses ultrasound; naval + depth measurement<br>RADAR: radio waves; detect aircraft + weather<br>Laser: coherent monochromatic light; cutting, surgery, CD/DVD"]:::key
    TE --> TE2["Optical fibre: total internal reflection; internet<br>MRI: magnetic resonance imaging; strong magnetic field<br>X-rays: discovered Roentgen 1895; electromagnetic radiation"]:::date
    DI --> DI1["Roentgen 1895: X-rays (Nobel 1901)<br>Curie 1898: Polonium + Radium; radioactivity<br>Fleming 1928: Penicillin (Alexander Fleming)"]:::date
    DI --> DI2["Newton 1687: Laws of Motion + Gravitation<br>Einstein 1905: Special Relativity; E=mc2<br>Planck 1900: Quantum theory"]:::date""",

"## Chapter H2 — Chemistry Essentials": """\
flowchart TD
    R["CHEMISTRY ESSENTIALS FOR GA"]:::root
    R --> CS["Common Salts + Formulae"]:::key
    R --> US["Common Uses"]:::key
    R --> TR["TRAP: Baking Soda vs Washing Soda"]:::trap
    CS --> CS1["NaCl: common salt (table salt); neutral pH<br>NaHCO3: baking soda; slightly alkaline<br>Na2CO3.10H2O: washing soda; alkaline"]:::key
    CS --> CS2["CaO: quicklime; CaSO4.0.5H2O: Plaster of Paris<br>Ca(OH)2: slaked lime; CaCO3: limestone<br>KAl(SO4)2.12H2O: alum; water purification"]:::key
    US --> US1["Baking soda: leavening in bread; antacid; fire extinguisher<br>Washing soda: remove stains; water softening<br>Bleaching powder: water treatment; textile bleaching"]:::key
    US --> US2["Plaster of Paris: bone casts; moulds; wall plaster<br>Alum: flocculation (water treatment) + styptic pencil<br>Chlorine: water disinfection + PVC manufacture"]:::key
    TR --> TR1["TRAP: Baking Soda = NaHCO3 (sodium BICARBONATE)<br>Washing Soda = Na2CO3.10H2O (sodium CARBONATE)<br>Baking soda for cooking; Washing soda for cleaning"]:::trap""",

"## Chapter H3 — Biology Essentials": """\
flowchart TD
    R["BIOLOGY ESSENTIALS FOR GA"]:::root
    R --> HB["Human Body Key Numbers"]:::key
    R --> BL["Blood Facts"]:::key
    R --> DI["Disease Vectors — Quick Reference"]:::key
    R --> VT["Vitamins — Quick Reference"]:::key
    HB --> HB1["Bones in adult: 206; Bones in infant: 270-300<br>Smallest bone: Stapes (ear); Largest: Femur<br>Normal pulse: 72 bpm; BP: 120/80 mmHg"]:::key
    HB --> HB2["Body temperature: 37 C; pH of blood: 7.35-7.45<br>RBC lifespan: 120 days; WBC: days-years<br>Platelet lifespan: 10 days"]:::key
    BL --> BL1["Universal donor: O negative (O-)<br>Universal recipient: AB positive (AB+)<br>Landsteiner discovered ABO system 1901 (Nobel 1930)"]:::key
    DI --> DI1["Malaria: Plasmodium via Anopheles female mosquito<br>Dengue: Flavivirus via Aedes aegypti mosquito<br>Filariasis: Wuchereria bancrofti via Culex mosquito"]:::key
    DI --> DI2["Sleeping sickness: Trypanosoma via Tsetse fly<br>Plague: Yersinia pestis via rat flea<br>Kala-azar: Leishmania via sandfly"]:::key
    VT --> VT1["A: Night blindness; B1: Beriberi; B3: Pellagra<br>B12: Pernicious anaemia; C: Scurvy<br>D: Rickets; K: Poor clotting"]:::key""",
}


SUBJECTS = {
    "biology":     ("biology.md",     BIOLOGY),
    "polity":      ("polity.md",      POLITY),
    "geography":   ("geography.md",   GEOGRAPHY),
    "history":     ("history.md",     HISTORY),
    "economics":   ("economics.md",   ECONOMICS),
    "physics":     ("physics.md",     PHYSICS),
    "chemistry":   ("chemistry.md",   CHEMISTRY),
    "environment": ("environment.md", ENVIRONMENT),
    "sci_tech":    ("sci_tech.md",    SCI_TECH),
}


def main() -> None:
    args = sys.argv[1:]
    if not args or "--help" in args:
        print("Usage: python3 add_chapter_diagrams.py [subject ...] | --all")
        print("Available subjects:", ", ".join(SUBJECTS))
        return

    targets = list(SUBJECTS.keys()) if "--all" in args else args

    for name in targets:
        if name not in SUBJECTS:
            print(f"Unknown subject: {name}. Available: {', '.join(SUBJECTS)}")
            continue
        fname, diagrams = SUBJECTS[name]
        fpath = NOTES / fname
        if not fpath.exists():
            print(f"File not found: {fpath}")
            continue
        n = insert_diagrams(fpath, diagrams)
        print(f"{name}: inserted {n} chapter-summary diagrams into {fpath.name}")


if __name__ == "__main__":
    main()
