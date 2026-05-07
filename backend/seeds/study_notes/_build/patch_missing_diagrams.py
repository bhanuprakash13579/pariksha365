#!/usr/bin/env python3
"""Patch script: insert the 15 diagrams that were missed in the first pass.
  - environment.md  : Chapter B1 (heading mismatch — 'of Biodiversity' was extra)
  - chemistry.md    : Chapters G2 G3 H1 H2 H3 I1 I2 I3 Y1 Y2 Y3 AB1 AB2 AB3
"""
import sys
from pathlib import Path

NOTES = Path(__file__).resolve().parent.parent

CD = """    classDef key fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef trap fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef date fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef proc fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef root fill:#f3e8ff,stroke:#9333ea,color:#4c1d95"""


def wrap(diagram: str) -> str:
    return (
        '\n<div class="chapter-summary">\n'
        '<div class="mermaid">\n'
        + diagram.rstrip() + "\n" + CD + "\n"
        + "</div>\n</div>\n"
    )


def insert_diagrams(filepath: Path, diagrams: dict) -> int:
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    count = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        diagram_code = diagrams.get(line.strip())
        if diagram_code is not None:
            i += 1
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
# ENVIRONMENT — B1 fix (exact heading without 'of Biodiversity')
# ─────────────────────────────────────────────────────────────────────────────
ENV_PATCH = {

"## Chapter B1 — Levels and Importance": """\
flowchart TD
    R["BIODIVERSITY — LEVELS AND IMPORTANCE"]:::root
    R --> LV["3 Levels of Biodiversity"]:::key
    R --> VA["Value of Biodiversity"]:::key
    R --> IN["India's Biodiversity Position"]:::key
    LV --> LV1["Genetic diversity: variation in genes WITHIN a species<br>Allows adaptation + evolution<br>Example: different rice varieties (Basmati, IR8)"]:::key
    LV --> LV2["Species diversity: count of different species in an area<br>Tropical regions: highest species richness<br>Measured by: Species richness + evenness"]:::key
    LV --> LV3["Ecosystem diversity: variety of habitats + ecosystems<br>Forests, wetlands, grasslands, deserts, coral reefs<br>India has ALL major ecosystem types"]:::key
    VA --> VA1["Direct values: food, timber, medicine, fibres, fuel<br>80% of global population uses plants for primary healthcare<br>25% of western medicines derived from tropical plants"]:::key
    VA --> VA2["Indirect values (ecosystem services):<br>Pollination (USD 235 billion/year globally)<br>Water purification, climate regulation, soil formation"]:::key
    VA --> VA3["Option value: future discoveries<br>Many compounds from biodiversity not yet discovered<br>Extinction = permanent loss of this option"]:::key
    IN --> IN1["India: 17th megadiverse country globally<br>2.4% of Earth's area; contains 8.1% of global species<br>90,000 animal species; 47,000 plant species"]:::key""",
}

# ─────────────────────────────────────────────────────────────────────────────
# CHEMISTRY — 14 missing chapters
# ─────────────────────────────────────────────────────────────────────────────
CHEM_PATCH = {

"## Chapter G2 — The Important Polymers Table": """\
flowchart TD
    R["POLYMERS"]:::root
    R --> NP["Natural Polymers"]:::key
    R --> SP["Synthetic Polymers"]:::key
    R --> TY["Thermoplastic vs Thermosetting"]:::key
    NP --> NP1["Cellulose: plant cell walls; cotton = pure cellulose<br>Starch: energy storage in plants<br>Natural rubber: cis-polyisoprene; latex of rubber tree"]:::key
    NP --> NP2["Proteins: polypeptide chains; silk = fibroin<br>DNA/RNA: polynucleotides<br>Wool: protein (keratin); Silk: protein (fibroin + sericin)"]:::key
    SP --> SP1["Nylon (polyamide): strong; used in ropes, stockings, toothbrush<br>Polyester (Terylene/Dacron): fabric + bottles (PET)<br>PVC (polyvinyl chloride): pipes, flooring, cables"]:::key
    SP --> SP2["Polythene: bags, bottles; LDPE (soft), HDPE (rigid)<br>Teflon (PTFE): non-stick cookware; very chemically inert<br>Bakelite: first synthetic plastic; thermosetting; electrical switches"]:::date
    TY --> TY1["Thermoplastic: softens on heating; can be reshaped<br>Examples: Polythene, PVC, Nylon, PET<br>Recyclable; used in packaging + consumer goods"]:::key
    TY --> TY2["Thermosetting: hardens permanently on heating; cannot remelt<br>Examples: Bakelite, Melamine, Epoxy resin<br>TRAP: Bakelite = thermosetting (NOT thermoplastic)"]:::trap""",

"## Chapter G3 — Vulcanisation of Rubber": """\
flowchart TD
    R["RUBBER AND VULCANISATION"]:::root
    R --> NR["Natural Rubber"]:::key
    R --> VU["Vulcanisation Process"]:::date
    R --> SR["Synthetic Rubbers"]:::key
    NR --> NR1["Natural rubber: latex from Hevea brasiliensis (rubber tree)<br>Chemical structure: cis-polyisoprene (repeating C5H8 units)<br>Problems: sticky in heat, brittle in cold, weak"]:::key
    VU --> VU1["Discovered by Charles Goodyear 1839 (accidental)<br>Process: heat natural rubber WITH sulphur (130-160 C)<br>Sulphur forms cross-links between polymer chains"]:::date
    VU --> VU2["Effect of vulcanisation:<br>Harder, more elastic, less sticky, more durable<br>Higher tensile strength + resistance to temperature"]:::key
    VU --> VU3["Applications: tyres (majority), hoses, belts, gloves, erasers<br>More sulphur = harder rubber (ebonite = very hard)<br>Less sulphur = softer (surgical gloves)"]:::key
    SR --> SR1["Neoprene: resistant to oil + chemicals; wetsuits, cables<br>Buna-S (SBR): tyre manufacturing; most common synthetic<br>Buna-N: oil-resistant; seals + gaskets"]:::key""",

"## Chapter H1 — Food Science": """\
flowchart TD
    R["FOOD SCIENCE"]:::root
    R --> MC["Macronutrients"]:::key
    R --> PR["Food Preservation Methods"]:::key
    R --> AD["Common Adulterants — Exam Favourites"]:::trap
    MC --> MC1["Carbohydrates: sugars + starch; primary energy source<br>4 kcal per gram<br>Sources: rice, wheat, potato, sugar"]:::key
    MC --> MC2["Proteins: made of amino acids; essential 9 must come from diet<br>4 kcal per gram; growth + repair<br>Complete protein: egg, meat, milk (all 9 essential AA)"]:::key
    MC --> MC3["Fats: concentrated energy; 9 kcal per gram<br>Saturated (animal fat, coconut): solid at room temp<br>Unsaturated (vegetable oil, fish): liquid at room temp"]:::key
    PR --> PR1["Salt: draws out water; inhibits microbial growth (fish, pickle)<br>Sugar: osmotic effect; jams, jellies, condensed milk<br>Vinegar (acetic acid): pickling vegetables"]:::key
    PR --> PR2["Pasteurisation: heating milk to 72 C for 15 sec (flash method)<br>Louis Pasteur developed the process<br>Kills pathogens but doesn't sterilise completely"]:::date
    AD --> AD1["TRAP: Common food adulterants examiners love:<br>Milk: water, starch, detergent (Soda test for starch)<br>Turmeric: metanil yellow dye (HCl turns violet)"]:::trap
    AD --> AD2["Chilli powder: brick dust or sudan red dye<br>Mustard seeds: argemone seeds (toxic: epidemic dropsy)<br>Honey: sugar syrup + invert sugar"]:::trap""",

"## Chapter H2 — Soaps, Detergents, Water": """\
flowchart TD
    R["SOAPS, DETERGENTS AND WATER"]:::root
    R --> SO["Soap"]:::key
    R --> DE["Detergents"]:::key
    R --> HW["Hard vs Soft Water"]:::key
    R --> TR["TRAP: Why soap fails in hard water"]:::trap
    SO --> SO1["Soap = salt of long-chain fatty acid<br>Made by saponification: fat + NaOH -> soap + glycerol<br>Sodium soap: hard soap (bars); Potassium soap: soft (shaving cream)"]:::key
    SO --> SO2["Cleansing action: hydrophilic head (water-loving)<br>+ hydrophobic tail (oil-loving)<br>Forms micelle around oil/grease droplets"]:::key
    DE --> DE1["Synthetic detergents: work in HARD water (unlike soap)<br>Sodium lauryl sulphate + Sodium dodecyl benzene sulphonate<br>Non-biodegradable: cause water pollution (foam in rivers)"]:::key
    HW --> HW1["Hard water: contains Ca2+ and Mg2+ ions<br>Temporary hardness: calcium bicarbonate; removed by BOILING<br>Permanent hardness: calcium sulphate; removed by ion exchange or Na2CO3"]:::key
    HW --> HW2["Water softening: Ion exchange resin (Na+ replaces Ca2+/Mg2+)<br>Adding washing soda Na2CO3: precipitates Ca2+ as CaCO3<br>Zeolite (permutite): natural ion exchanger"]:::key
    TR --> TR1["TRAP: Soap forms scum in hard water<br>Ca2+(Mg2+) + soap -> insoluble calcium/magnesium soap (scum)<br>Detergent doesn't form scum (soluble calcium salt)"]:::trap""",

"## Chapter H3 — Medicines": """\
flowchart TD
    R["MEDICINES AND DRUGS"]:::root
    R --> AB["Antibiotics"]:::date
    R --> AN["Analgesics (Pain killers)"]:::key
    R --> AS["Antiseptics vs Disinfectants"]:::key
    R --> AM["Antimalarials"]:::key
    AB --> AB1["Penicillin: discovered Alexander Fleming 1928<br>From Penicillium mould; first antibiotic<br>Kills bacteria by preventing cell wall synthesis"]:::date
    AB --> AB2["Streptomycin: Selman Waksman 1943 (Nobel 1952)<br>Tetracycline: broad-spectrum<br>Amoxicillin: most prescribed today (penicillin family)"]:::date
    AN --> AN1["Aspirin (acetylsalicylic acid): pain + fever + anti-inflammatory<br>Paracetamol/Acetaminophen: safer for fever + mild pain<br>Ibuprofen: NSAID; pain + inflammation"]:::key
    AN --> AN2["Narcotic analgesics: morphine, codeine (opioids)<br>Used only for severe pain (cancer, surgery)<br>Highly addictive"]:::key
    AS --> AS1["Antiseptics: used ON body (skin, wounds)<br>Dettol (chloroxylenol), hydrogen peroxide, iodine tincture<br>Boric acid: eye wash antiseptic"]:::key
    AS --> AS2["Disinfectants: used on NON-living surfaces<br>Phenol, bleaching powder, chlorine (water)<br>TRAP: antiseptic safe on skin; disinfectant NOT safe on skin"]:::trap
    AM --> AM1["Quinine: from Cinchona bark; oldest antimalarial<br>Chloroquine: synthetic; once standard treatment<br>Artemisinin: from Artemisia plant; Tu Youyou (Nobel 2015)"]:::date""",

"## Chapter I1 — Air Pollution": """\
flowchart TD
    R["AIR POLLUTION — CHEMISTRY VIEW"]:::root
    R --> PO["Primary Pollutants"]:::key
    R --> SE["Secondary Pollutants"]:::key
    R --> AC["Acid Rain"]:::key
    R --> TR["TRAP: CO vs CO2"]:::trap
    PO --> PO1["CO (carbon monoxide): incomplete combustion<br>Odourless + colourless; binds haemoglobin 200x > O2<br>Sources: vehicle exhaust, coal burning, cigarettes"]:::key
    PO --> PO2["SO2 (sulphur dioxide): burning S-rich coal<br>Causes acid rain; lung irritant<br>NOx: vehicle engines; photochemical smog"]:::key
    PO --> PO3["PM 2.5 (fine particulate matter): most dangerous<br>Penetrates deep into lungs; causes respiratory + cardiac disease<br>PM 10: coarser; still harmful but less penetrating"]:::key
    SE --> SE1["Ground-level ozone (O3): formed photochemically<br>NOx + VOC + sunlight -> ozone (secondary pollutant)<br>Same molecule as protective stratospheric ozone"]:::key
    AC --> AC1["Acid rain: pH less than 5.6 (normal rain = 5.6)<br>Formation: SO2 + H2O -> H2SO3; SO3 -> H2SO4<br>NOx + H2O -> HNO3"]:::key
    AC --> AC2["Effects of acid rain: kills fish in lakes; damages marble buildings<br>Taj Mahal marble damage: acid rain from Mathura refinery<br>Kills forests; acidifies soil"]:::key
    TR --> TR1["TRAP: CO (monoxide) is the TOXIC one<br>CO2 (dioxide) is a greenhouse gas but not directly toxic<br>CO: binds haemoglobin -> prevents O2 transport -> death"]:::trap""",

"## Chapter I2 — Ozone Layer": """\
flowchart TD
    R["OZONE LAYER"]:::root
    R --> ST["Ozone in Stratosphere"]:::key
    R --> DE["Depletion Mechanism"]:::proc
    R --> CF["CFCs — The Culprit"]:::key
    R --> TR["TRAP: Good ozone vs Bad ozone"]:::trap
    ST --> ST1["Ozone (O3): allotrope of oxygen; 3 oxygen atoms<br>Location: stratosphere 15-35 km altitude<br>Absorbs harmful UV-B and UV-C radiation from Sun"]:::key
    ST --> ST2["Without ozone layer: UV radiation causes<br>skin cancer, cataracts, immune suppression<br>Also damages phytoplankton (base of ocean food chain)"]:::key
    DE --> DE1["UV light breaks CFC -> Cl radical (free chlorine)<br>Cl + O3 -> ClO + O2 (ozone destroyed)<br>ClO + O -> Cl + O2 (Cl regenerated = chain reaction)"]:::proc
    DE --> DE2["1 Cl atom can destroy 100,000 ozone molecules<br>Ozone hole: thinnest over Antarctica (polar vortex)<br>Discovered by British Antarctic Survey 1985"]:::date
    CF --> CF1["CFCs = Chlorofluorocarbons (Freon, R-12)<br>Used in: refrigerators, air conditioners, aerosol sprays<br>Very stable in lower atmosphere (10-100 yr lifetime)"]:::key
    CF --> CF2["Montreal Protocol 1987: phase-out of CFCs<br>Most successful global environmental agreement<br>Replaced by HFCs (then HFOs — less harmful)"]:::date
    TR --> TR1["TRAP: Ozone location determines if good or bad<br>Stratospheric ozone = GOOD (shields UV)<br>Tropospheric (ground-level) ozone = BAD (pollutant, smog)"]:::trap""",

"## Chapter I3 — Water Pollution": """\
flowchart TD
    R["WATER POLLUTION — CHEMISTRY VIEW"]:::root
    R --> HM["Heavy Metal Poisoning"]:::key
    R --> GW["Groundwater Contaminants"]:::key
    R --> BO["BOD Concept"]:::key
    R --> DW["Drinking Water Standards"]:::key
    HM --> HM1["Mercury (Hg): Minamata disease (Japan 1950s)<br>Bioaccumulates in fish; causes neurological damage<br>Source: chlor-alkali plants, coal power, artisanal gold mining"]:::date
    HM --> HM2["Lead (Pb): cognitive damage especially in children<br>Sources: old paint, lead pipes, petrol additives (now banned)<br>Cadmium (Cd): Itai-Itai disease (Japan); kidney damage"]:::date
    GW --> GW1["Fluoride: dental + skeletal fluorosis<br>Rajasthan, Andhra Pradesh, Telangana worst affected<br>Optimal: 0.5-1.5 mg/L; toxic above 1.5 mg/L"]:::key
    GW --> GW2["Arsenic: causes black foot disease + skin lesions<br>West Bengal + Bihar: most affected in India<br>Natural leaching from rocks (not industrial)"]:::key
    BO --> BO1["BOD = Biochemical Oxygen Demand<br>O2 needed by microbes to decompose organic matter<br>High BOD = highly polluted; kills aquatic life"]:::key
    DW --> DW1["WHO drinking water standard: pH 6.5-8.5<br>Total Dissolved Solids (TDS) less than 500 mg/L<br>BIS IS 10500: India's drinking water standard"]:::key""",

"## Chapter Y1 — The NPK Macronutrients": """\
flowchart TD
    R["NPK MACRONUTRIENTS"]:::root
    R --> N["Nitrogen (N)"]:::key
    R --> P["Phosphorus (P)"]:::key
    R --> K["Potassium (K)"]:::key
    R --> TR["TRAP: Deficiency symptoms"]:::trap
    N --> N1["Most critical macronutrient for plant growth<br>Component of: amino acids, proteins, chlorophyll, DNA<br>Deficiency: yellowing of older leaves (chlorosis) first"]:::key
    N --> N2["Plants absorb as: NO3- (nitrate) or NH4+ (ammonium)<br>Atmospheric N2 cannot be used directly<br>Nitrogen fixation by bacteria or industrial (Haber process)"]:::key
    P --> P1["Root development; early plant growth<br>Component of: ATP, ADP, DNA, RNA, phospholipids<br>Deficiency: purple/reddish leaves; poor root system"]:::key
    P --> P2["Plants absorb as H2PO4- or HPO42-<br>Phosphate fertilisers: SSP, DAP, TSP<br>Fixing: becomes unavailable in acidic + alkaline soil"]:::key
    K --> K1["Enzyme activation; stomatal regulation<br>Disease resistance; water-use efficiency<br>Deficiency: scorching of leaf edges (necrosis)"]:::key
    TR --> TR1["TRAP: N deficiency = yellowing of OLDER leaves first<br>P deficiency = purple/red coloration of leaves<br>K deficiency = leaf scorch at edges + tips"]:::trap""",

"## Chapter Y2 — Common Nitrogenous Fertilisers": """\
flowchart LR
    R["NITROGENOUS FERTILISERS"]:::root
    R --> U["Urea"]:::key
    R --> A["Ammonium Fertilisers"]:::key
    R --> C["Combination Fertilisers"]:::key
    U --> U1["Urea CO(NH2)2: 46% Nitrogen — HIGHEST N content<br>Most widely used N fertiliser globally<br>Made by Haber process (N2+H2->NH3) then reaction with CO2"]:::key
    U --> U2["Slow-release: hydrolysis to NH4+ in soil<br>Slightly acidifying; overdose causes salt burn<br>India: Neem-coated urea mandatory (slows release)"]:::key
    A --> A1["Ammonium sulphate (NH4)2SO4: 21% N; acidic<br>Ammonium nitrate NH4NO3: 34% N; explosive risk (stored carefully)<br>Ammonium chloride NH4Cl: 25% N; used in rice paddy"]:::key
    C --> C1["DAP (Diammonium phosphate) (NH4)2HPO4:<br>18% N + 46% P2O5; most popular complex fertiliser<br>Granular; applied at sowing"]:::key
    C --> C2["CAN (Calcium Ammonium Nitrate): 26% N<br>Less explosive than NH4NO3; calcium improves soil<br>MOP (Muriate of Potash) KCl: most common K fertiliser"]:::key""",

"## Chapter Y3 — Biofertilisers": """\
flowchart TD
    R["BIOFERTILISERS"]:::root
    R --> NF["Nitrogen-Fixing Biofertilisers"]:::key
    R --> PH["Phosphate-Solubilising"]:::key
    R --> MY["Mycorrhiza"]:::key
    R --> BE["Benefits vs Chemical Fertilisers"]:::key
    NF --> NF1["Rhizobium: symbiotic; in ROOT NODULES of legumes<br>Fixes atmospheric N2 into NH3 for plant<br>Host specificity: diff Rhizobium for diff legume crops"]:::key
    NF --> NF2["Azotobacter: FREE-LIVING in soil; aerobic<br>Azospirillum: associative; cereal crops (wheat, maize)<br>BGA (Blue-Green Algae): Anabaena, Nostoc — rice paddies"]:::key
    NF --> NF3["Frankia: symbiotic with non-legume Casuarina (forest tree)<br>Cyanobacteria in water fern Azolla: used in rice paddies<br>Azolla fixes N + decomposes as green manure"]:::key
    PH --> PH1["Phosphate-Solubilising Bacteria (PSB):<br>Bacillus + Pseudomonas species<br>Convert insoluble soil P to soluble form for plants"]:::key
    MY --> MY1["Mycorrhiza: fungus + plant root symbiosis<br>Ectomycorrhiza: outside root; Endomycorrhiza: inside root<br>Extends root surface area; improves P + water absorption"]:::key
    BE --> BE1["Cheaper + eco-friendly than chemical fertilisers<br>Improve soil health long-term<br>Do NOT cause groundwater nitrate pollution"]:::key""",

"## Chapter AB1 — IUPAC Naming Rules": """\
flowchart TD
    R["IUPAC NAMING OF ORGANIC COMPOUNDS"]:::root
    R --> RU["Basic Rules"]:::proc
    R --> SU["Suffixes by Functional Group"]:::key
    R --> PR["Prefixes for Branches"]:::key
    R --> TR["TRAP: Numbering direction"]:::trap
    RU --> RU1["Step 1: Find the LONGEST carbon chain (parent chain)<br>Step 2: Name the parent chain<br>1C=meth, 2C=eth, 3C=prop, 4C=but, 5C=pent, 6C=hex"]:::proc
    RU --> RU2["Step 3: Identify functional group (determines suffix)<br>Step 4: Number chain to give LOWEST locant<br>Step 5: Name branches (substituents) alphabetically"]:::proc
    SU --> SU1["Alkane: -ane (CH4 = methane; C2H6 = ethane)<br>Alkene: -ene (C2H4 = ethene; but-2-ene)<br>Alkyne: -yne (C2H2 = ethyne = acetylene)"]:::key
    SU --> SU2["Alcohol: -anol (methanol, ethanol, propan-1-ol)<br>Aldehyde: -anal (methanal = formaldehyde, ethanal)<br>Ketone: -anone (propanone = acetone)<br>Carboxylic acid: -anoic acid (ethanoic = acetic)"]:::key
    PR --> PR1["Methyl- (CH3), Ethyl- (C2H5), Propyl- (C3H7)<br>Halo-: fluoro, chloro, bromo, iodo<br>Nitro- (-NO2), Amino- (-NH2)"]:::key
    TR --> TR1["TRAP: Number from end that gives LOWEST locant<br>e.g. CH3-CH2-OH = ETHAN-1-OL (not ethan-2-ol)<br>Functional group takes priority in numbering"]:::trap""",

"## Chapter AB2 — Named Reactions (High-Frequency)": """\
flowchart LR
    R["NAMED REACTIONS — HIGH FREQUENCY"]:::root
    R --> R1["Saponification"]:::key
    R --> R2["Fermentation"]:::key
    R --> R3["Thermite Reaction"]:::key
    R --> R4["Esterification"]:::key
    R --> R5["Haber Process"]:::key
    R1 --> R1a["Fat + NaOH --heat--> Soap + Glycerol<br>Used to make hard soap (bars)<br>NaOH -> hard soap; KOH -> soft soap/shaving cream"]:::key
    R2 --> R2a["C6H12O6 --yeast--> 2C2H5OH + 2CO2<br>Glucose -> ethanol + carbon dioxide<br>Anaerobic process; used to make alcohol + bioethanol"]:::key
    R3 --> R3a["2Al + Fe2O3 -> Al2O3 + 2Fe + heat<br>Aluminium displaces iron (activity series)<br>Used in welding railway tracks (thermite welding)"]:::key
    R4 --> R4a["Alcohol + Carboxylic acid --H2SO4--> Ester + Water<br>C2H5OH + CH3COOH -> CH3COOC2H5 + H2O<br>Ester = fruity smell; used in flavours + perfumes"]:::key
    R5 --> R5a["N2 + 3H2 --Fe catalyst, 200 atm, 400-500 C--> 2NH3<br>Industrial synthesis of ammonia<br>Fritz Haber (Nobel 1918); Carl Bosch scaled it up"]:::date""",

"## Chapter AB3 — Tests for Functional Groups": """\
flowchart TD
    R["TESTS FOR FUNCTIONAL GROUPS"]:::root
    R --> AL["Alcohol (-OH)"]:::key
    R --> AD["Aldehyde (-CHO)"]:::key
    R --> CA["Carboxylic Acid (-COOH)"]:::key
    R --> UN["Unsaturation (double/triple bond)"]:::key
    R --> TR["TRAP: Tollens' vs Fehling's"]:::trap
    AL --> AL1["Sodium metal test: 2ROH + 2Na -> 2RONa + H2 (gas)<br>Fizzing/bubbling = alcohol present<br>Ester formation test: add acetic acid + H2SO4 -> fruity smell"]:::key
    AD --> AD1["Tollens' test (Silver mirror test):<br>RCHO + Ag2O -> RCOOH + Ag (silver mirror on flask wall)<br>Silver mirror = ALDEHYDE confirmed"]:::key
    AD --> AD2["Fehling's test:<br>RCHO + Fehling's solution (Cu2+) -> red/brick ppt Cu2O<br>Red precipitate = ALDEHYDE confirmed; KETONE does not react"]:::key
    CA --> CA1["Blue litmus turns RED: acid present<br>Na2CO3 test: RCOOH + Na2CO3 -> CO2 gas (brisk effervescence)<br>pH test: aqueous solution pH below 7"]:::key
    UN --> UN1["Bromine water test (Baeyer's test):<br>Add Br2 water: decolourisation = UNSATURATION (double/triple bond)<br>Alkanes do NOT decolourise bromine water"]:::key
    UN --> UN2["KMnO4 test: purple KMnO4 decolourises = unsaturation<br>Also: alkenes + alkynes react; alkanes don't<br>Used to distinguish alkane from alkene/alkyne"]:::key
    TR --> TR1["TRAP: Both Tollens' and Fehling's detect ALDEHYDE<br>Ketones give NEGATIVE Tollens' and Fehling's<br>Tollens' = Ag mirror; Fehling's = red Cu2O precipitate"]:::trap""",
}


def main():
    # Fix environment B1
    env_path = NOTES / "environment.md"
    n = insert_diagrams(env_path, ENV_PATCH)
    print(f"environment: inserted {n} missing diagram(s)")

    # Fix chemistry G2-AB3
    chem_path = NOTES / "chemistry.md"
    n = insert_diagrams(chem_path, CHEM_PATCH)
    print(f"chemistry: inserted {n} missing diagram(s)")


if __name__ == "__main__":
    main()
