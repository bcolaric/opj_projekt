import pandas as pd

# Create sample tourism guide entries
tourism_guides = [
    {
        "text": "Dubrovnik je prekrasan grad na jugu Hrvatske, poznat po svojim impresivnim zidinama koje datiraju iz 13. stoljeća. Stari grad Dubrovnika, koji se nalazi na UNESCO-vom popisu svjetske baštine, okružen je zidinama dugim 1940 metara. Glavna ulica Stradun proteže se kroz srce starog grada, a uz nju se nalaze brojni restorani, kafići i trgovine. Tvrđava Lovrijenac, koja se nalazi na 37 metara visokoj litici, pruža spektakularan pogled na grad i Jadransko more. Tijekom ljetnih mjeseci, grad ugošćuje poznati Dubrovački ljetni festival koji traje od 10. srpnja do 25. kolovoza."
    },
    {
        "text": "Split, drugi najveći grad Hrvatske, poznat je po Dioklecijanovoj palači iz 4. stoljeća. Palača je izgrađena kao rezidencija rimskog cara Dioklecijana i danas čini jezgru gradskog središta. Unutar zidina palače nalazi se katedrala svetog Dujma, izvorno Dioklecijanov mauzolej. Riva, splitska gradska šetnica, proteže se duž luke i popularno je mjesto za šetnju i druženje. U blizini grada nalazi se brdo Marjan, zaštićeno područje prekriveno mediteranskom vegetacijom, s brojnim šetnicama i vidikovcima."
    },
    {
        "text": "Nacionalni park Plitvička jezera najveći je i najstariji nacionalni park u Hrvatskoj. Park je poznat po 16 jezera različitih veličina, međusobno povezanih slapovima. Jezera su poznata po svojoj jedinstvenoj tirkiznoj boji koja nastaje zbog posebnih geoloških uvjeta i prisutnosti različitih minerala. Kroz park vodi 18 kilometara drvenih staza i mostića. Najbolje vrijeme za posjet je od proljeća do jeseni, a park je otvoren tijekom cijele godine. Ulaznice se mogu kupiti na ulazima u park, a dostupni su i organizirani izleti s vodičem."
    },
    {
        "text": "Rovinj je slikoviti gradić na zapadnoj obali Istre. Stari grad smješten je na poluotoku, s uskim ulicama koje vode do crkve svete Eufemije na vrhu brda. Crkva ima najviši zvonik na istarskoj obali, visok 60 metara. Grad je poznat po svojoj ribljoj tržnici, umjetničkoj sceni i brojnim restoranima koji služe tradicionalnu istarsku kuhinju. U blizini se nalazi arhipelag od 13 otoka, a najpoznatiji su Crveni otok i otok Sveta Katarina. Okolica grada poznata je po uzgoju maslina i proizvodnji visokokvalitetnog maslinovog ulja."
    },
    {
        "text": "Zadar je grad bogate povijesti na dalmatinskoj obali. Poznate gradske atrakcije uključuju Morske orgulje, jedinstvenu arhitektonsku instalaciju koja proizvodi glazbu pomoću morskih valova, i Pozdrav Suncu, svjetlosnu instalaciju koja stvara impresivnu svjetlosnu predstavu tijekom zalaska sunca. Crkva svetog Donata iz 9. stoljeća jedan je od najprepoznatljivijih simbola grada. Zadarski Forum najveći je rimski trg na istočnoj strani Jadrana. Grad je također poznat po prekrasnim zalascima sunca, koje je Alfred Hitchcock opisao kao najljepše na svijetu."
    },
    {
        "text": "Hvar je jedan od najpopularnijih hrvatskih otoka, poznat po svojoj mediteranskoj klimi i rekordnom broju sunčanih sati. Grad Hvar, smješten na jugozapadnoj obali otoka, ima živopisnu luku i povijesnu jezgru. Tvrđava Fortica (Španjola) dominira gradom i pruža spektakularan pogled na Paklene otoke. Otok je poznat po svojim lavandnim poljima, vinogradima i maslinicima. Starogradsko polje, UNESCO-va svjetska baština, najbolje je sačuvani antički grčki sustav parcelacije zemljišta na Mediteranu."
    },
    {
        "text": "Zagreb, glavni grad Hrvatske, spaja srednjoeuropsku povijest s mediteranskim načinom života. Gornji grad, povijesni dio Zagreba, dom je crkve svetog Marka s prepoznatljivim šarenim krovom, Kamenitih vrata i Muzeja prekinutih veza. Donji grad karakteriziraju elegantne zgrade iz 19. stoljeća, Trg bana Jelačića i Lenucijeva potkova, niz trgova i parkova. Dolac, središnja gradska tržnica, najbolje je mjesto za doživjeti lokalnu gastronomiju. Maksimir, najstariji javni park u Zagrebu, savršeno je mjesto za bijeg od gradske vreve."
    },
    {
        "text": "Muzej krapinskih neandertalaca jedan je od najmodernijih muzeja u Hrvatskoj. Otvoren 2010. godine, muzej predstavlja evoluciju života na Zemlji s posebnim naglaskom na razdoblje neandertalaca. Nalazište Hušnjakovo, gdje su pronađeni ostaci neandertalaca, nalazi se odmah pored muzeja. Muzej godišnje posjeti preko 100.000 posjetitelja. Stalni postav uključuje rekonstrukcije neandertalaca u prirodnoj veličini."
    },
    {
        "text": "Opatija se često naziva 'biserom Jadrana' i prva je turistička destinacija u Hrvatskoj. Hotel Kvarner, izgrađen 1884. godine, bio je prvi hotel na istočnoj obali Jadrana. Lungomare, poznata obalna šetnica, proteže se 12 kilometara od Voloskog do Lovrana. Park Angiolina dom je više od 150 vrsta biljaka iz cijelog svijeta. Villa Angiolina predstavlja početak turizma u Opatiji."
    },
    {
        "text": "Varaždin je grad baroka, glazbe i cvijeća. Stari grad Varaždin je srednjovjekovna utvrda pretvorena u dvorac. Varaždinsko groblje, koje je uredio Herman Haller, smatra se jednim od najljepših u Europi. Špancirfest, tradicionalni ulični festival, održava se krajem kolovoza. Gradska vijećnica jedna je od najstarijih u Europi, izgrađena u 16. stoljeću."
    },
    {
        "text": "Nacionalni park Kornati sastoji se od 89 otoka, otočića i hridi. Područje parka obuhvaća oko 220 četvornih kilometara. Najpoznatija značajka Kornata su takozvane 'krune', strme litice okrenute prema otvorenom moru. Murter je glavna polazišna točka za posjet parku. Ronjenje je jedna od najpopularnijih aktivnosti u parku."
    },
    {
        "text": "Kopački rit je najveće močvarno područje u Hrvatskoj. Park prirode dom je preko 290 vrsta ptica. Najbolje vrijeme za posjet je proljeće i jesen tijekom migracije ptica. Drvene šetnice omogućuju posjetiteljima promatranje životinja iz blizine. Park se nalazi na ušću Drave u Dunav."
    },
    {
        "text": "Motovun je slikoviti gradić u središnjoj Istri. Gradske zidine duge su 1052 metra i pružaju panoramski pogled na dolinu rijeke Mirne. Motovunska šuma poznata je po tartufima, posebno bijelom tartufu. Motovun Film Festival održava se svake godine krajem srpnja. Gradska vrata iz 15. stoljeća glavni su ulaz u stari grad."
    }
]

# Create DataFrame
df = pd.DataFrame(tourism_guides)

# Save to CSV
df.to_csv('tourism_guides.csv', index=False)

print("Tourism guides CSV file has been created successfully!")