# P1 — rozeznanie dostawców z dostawą do Polski

**Status:** migawka rynku; nie jest zgodą na zakup

**Data sprawdzenia:** 2026-07-20

**Zakres:** jeden zestaw stanowiska P1

## 1. Wniosek

Większość aparatury i standardowych części można pozyskać w Polsce lub UE.
Nie ma jednak jeszcze kompletnego koszyka, który można bezpiecznie opłacić.
Pozostają cztery blokery:

1. dostawca Leadshine musi pisemnie zatwierdzić konkretny zasilacz, sposób
   obsługi energii zwrotnej i rezystor hamowania;
2. koła Gates, tuleja oraz gotowy otwór małego koła wymagają wspólnej oferty;
3. dokładna konfiguracja E6 wymaga oferty i dopiero ona zamraża mocowanie;
4. znalezione sprzęgło spełniające wymagania ma Ø41,3 × 51,7 mm, przekracza
   obecny zastępczy obrys CAD Ø35 × 45 mm i wymaga ponownej kontroli prześwitu.

Najbardziej praktyczny pierwszy kontakt to EBMiA: ma dokładne serwo i jest
polskim kanałem Leadshine, więc może jednocześnie odpowiedzieć o zasilaniu,
regeneracji, rewizji napędu i przewodach. Nie należy jeszcze składać zamówienia.

## 2. Jak czytać statusy

- **dokładny kandydat** — publiczna oferta odpowiada kodowi i parametrom BOM;
  cenę, stan, rewizję i dostawę sprawdza się ponownie przed płatnością;
- **RFQ** — potrzebna jest pisemna oferta albo odpowiedź techniczna;
- **warunkowy** — część spełnia część wymagań, ale ma nierozstrzygnięty wpływ
  na CAD, elektrykę lub pomiar;
- **odrzucony** — nie spełnia co najmniej jednego wymagania i nie jest cichym
  zamiennikiem.

Ceny zagraniczne pozostają w walucie oferty. Dla orientacji średni kurs NBP z
2026-07-20 wynosił `1 EUR = 4,3359 PLN` i `1 USD = 3,7906 PLN`. Kwoty netto i
brutto nie są sumowane, a koszt wysyłki, polski VAT i cło muszą być potwierdzone
w ofercie lub koszyku.

## 3. Napęd i przekładnia

| Element | Dostawca i stan strony | Cena strony | Status i decyzja |
|---|---|---:|---|
| Leadshine `iSV2-RS6040V48G` | [EBMiA](https://www.ebmia.pl/zintegrowane-serwonapedy/260011-zintegrowany-serwosilnik-z-sterownikiem-serwonaped-leadshine-isv2-rs6040v48g-400w-127nm-48vdc-rs232-hamulec.html), magazyn PL, wysyłka 24 h | 1 749,74 PLN netto / 2 152,18 PLN brutto | **Dokładny kandydat.** Przed zakupem potwierdzić rewizję, gwarancję, zwrot, Modbus oraz cały tor zasilania/regeneracji. |
| Gates `600-5MGT3-15`, nr `9400-55202` | [EBMiA](https://www.ebmia.pl/pasy-zebate-powergrip-gt3-5mgt/8759-pas-zebaty-powergrip-gt3-600-5mgt3-15-z120.html), stan 0; [Z24](https://www.z24.de/a/40022-zahnriemen-5m-gt-gt3/313433), magazyn UE, pas docinany do szerokości | 103,17 PLN brutto w EBMiA; 29,55 EUR brutto + 8,99 EUR wysyłki w Z24 | **Dokładny kandydat.** Z24 ma obecnie bardziej wiarygodny termin; produkt docinany jest wyłączony ze zwrotu. |
| Gates `P18-5MGT-15AL`, nr `7845-1518` | kod i wymiary potwierdza [katalog Gates](https://www.gates.com/content/dam/gates/home/knowledge-center/resource-library/catalogs/korea/power-transmission-2015-products-catalogue-en.pdf); brak potwierdzonej oferty PL/UE | RFQ | **RFQ.** Katalog podaje zakres otworu do 3/8 cala, a nie gwarantowany gotowy otwór. Potwierdzić 9,525 mm i retencję. |
| Gates `P90-5MGT-15`, nr `7709-1090` | kod i interfejs 1610 potwierdza [katalog Gates](https://www.gates.com/content/dam/documents-library/catalogs/light-power-and-precision-manual.pdf); brak potwierdzonej oferty PL/UE | RFQ | **RFQ.** Zamawiać tylko razem z pasującą tuleją i rysunkiem. |
| Gates `1610-20MM`, nr `7858-1620` | dokładny kod potwierdza [karta dystrybutora](https://www.easternia.com/gates-78581620); brak potwierdzonej oferty PL/UE | RFQ | **RFQ.** Generyczna lub Optibelt 1610-20 nie jest automatycznie zaakceptowanym zamiennikiem. |
| Ruland `BCK26-14MM-3/8-A` | [Ruland Europe](https://www.ruland.com/de/bck26-14mm-3-8-a.html), 3 szt. | 179,75 EUR | **Warunkowy, nie kupować.** Otwory, zacisk, brak luzu i 7 Nm w rewersie spełniają wymagania, ale Ø41,3 × 51,7 mm przekracza obecny zastępczy obrys CAD Ø35 × 45 mm; trzeba zregenerować model i sprawdzić kolizje oraz dostęp zacisków. |

Powiązane przewody EBMiA: `CABLE-PC-1` kosztował 9,88 PLN brutto, a przewód
komunikacyjny iSV2 36,38 PLN brutto. Dokładną zgodność z dostarczoną rewizją
napędu należy ująć w tej samej ofercie.

## 4. Zasilanie, hamowanie i odcięcie

| Element | Dostawca i stan strony | Cena strony | Status i decyzja |
|---|---|---:|---|
| Mean Well `RSP-750-48`, 48 V / 15,7 A / 753,6 W | [TME](https://www.tme.eu/pl/details/rsp-750-48/zasilacze-do-wbudowania/mean-well/), 29 szt. | 705,31 PLN netto / 867,54 PLN brutto | **Warunkowy.** Spełnia moc i prąd, lecz [datasheet Mean Well](https://www.meanwell.com/Upload/PDF/RSP-750/RSP-750-SPEC.PDF) nie deklaruje pochłaniania energii zwrotnej. Wymagane pisemne zatwierdzenie. |
| Ohmite `TEH100M10R0FE`, 10 Ω / 100 W | [Mouser EU](https://eu.mouser.com/ProductDetail/Ohmite/TEH100M10R0FE?qs=bnytM%2FPQ3LyR6ugYOEsRHA%3D%3D), 210 szt. | 9,29 EUR netto | **Dokładny kandydat elektryczny.** Nieindukcyjny i izolowany, ale 100 W wymaga właściwego radiatora, TIM i osłony. Leadshine ma potwierdzić cały układ CN4. |
| Eaton `DILM40-22(RDC24)`, nr `277812` | [Elektro-Spark](https://sklep.elektrospark.pl/aparatura-elektryczna/sterownie-i-zabezpieczenie-silnikow-elektrycznych/stycznik-ac/36661%2Cdilm40-22-rdc24-stycznik-mocy-40a-ac-3-2z-2r-277812-eaton.html), 3 szt. / 24 h | 476,44 PLN netto / 586,02 PLN brutto | **Warunkowy.** [Eaton](https://www.eaton.com/pl/pl-pl/skuPage.277812.html) podaje 50 A DC-1 przy 60 V. Wymaga zasilania cewki 24 V i sprawdzenia pojemności szyny, koordynacji zwarciowej oraz osobnej izolacji serwisowej. |
| Schneider `XB5AS8442`, grzybek 1NC | [TME](https://www.tme.eu/pl/details/xb5as8442/przelaczniki-tablicowe-standardowe-22mm/schneider-electric/), 211 szt. | 82,89 PLN netto / 101,95 PLN brutto | **Dokładny kandydat sterowania cewką.** Nie wolno nim bezpośrednio rozłączać szyny 48 V / 30 A. |
| Bezpiecznik i podstawa DC | ETI `CH10x38 gPV 20A` i `EFH10DC` są dostępne w PL | ok. 42 PLN brutto razem | **Warunkowe.** Typ gPV i 20 A wymagają koordynacji z inrush napędu, przewodem i instrukcją Leadshine. |

Nie znaleziono publicznego dowodu, że RSP-750-48 może przyjmować prąd zwrotny.
Jego OVP nie zastępuje odpowiedzi o backfeed. Dobór stycznika, zabezpieczenia,
przewodów i izolacji serwisowej powinien zostać zatwierdzony przez osobę
kompetentną w obwodach DC przed zasileniem stanowiska.

## 5. Sterowanie i aparatura

| Element | Dostawca i stan strony | Cena strony | Status i decyzja |
|---|---|---:|---|
| Mesa `7I96S` | producent [nie ma stanu](https://store.mesanet.com/index.php?product_id=374&route=product%2Fproduct); [EuSurplus](https://eusurplus.com/index.php?product_id=159&route=product%2Fproduct) pokazuje magazyn UE | 170 EUR, VAT i wysyłka do potwierdzenia | **Dokładny kandydat.** Potwierdzić autentyczność, rewizję i koszt dostarczony do Polski. Brak magazynu producenta nie blokuje już samego rozeznania. |
| Stabilizowane 5,0 V / co najmniej 1 A dla Mesa i E6 | dokładny model jeszcze niewybrany | RFQ / dobór | **Nowy wymagany element.** [Manual 7I96S](https://www.mesanet.com/pdf/parallel/7i96sman.pdf) dopuszcza tylko 4,75–5,25 V i podaje do 400 mA bez obciążeń zewnętrznych. |
| Waveshare `USB TO RS485 (C)`, SKU 34620 | [OpenELAB EU](https://openelab.de/products/waveshare-usb-zu-rs485-c), wysyłka deklarowana do 72 h | 11,95 EUR brutto | **Dokładny kandydat.** Potwierdzić magazyn UE i dostawę. Warianty B/CH343G nie są tym samym produktem. |
| US Digital `E6-10000-787-IE-D-H-D-3` + `CA-FC10-SH-NC-6` | RFQ do [Angst+Pfister Polska](https://www.angst-pfister.com/media-resources/contact.html), oficjalnego partnera US Digital | RFQ | **RFQ i blocker CAD.** US Digital ma potwierdzić, że pełna kombinacja jest produkowana, dołączyć narzędzia, spacer, kabel, śruby i rysunek. |
| Pico `USB TC-08`, PP222 | [Pico Polska](https://www.picopolska.pl/rejestratory/rejestrator-usb-tc-08), na wyczerpaniu, 24 h | 1 779 PLN netto / 2 188,17 PLN brutto | **Dokładny kandydat.** Oferta sond ma obejmować trzy samoprzylepne termopary powierzchniowe typu K i jedną sondę otoczenia. |
| Mark-10 `M3-5` | [Checkline EU](https://www.checkline.eu/product/series-3), zwykle 1–3 dni lub 1–3 tygodnie | 688 EUR netto za miernik | **RFQ.** Poprosić o `M3-5 + CERT` z danymi + `AC1120` + dostawę PL. Równolegle zapytać o wynajem wzorcowanego miernika 0–25 N. |

Nie zatwierdza się jeszcze tańszego KERN/SAUTER `FK25`. Ma odpowiedni zakres i
rozdzielczość, ale większy błąd, brak USB i wymaga osobnego wzorcowania oraz
oceny zgodnie ze specyfikacją aparatury.

## 6. Łożyska i materiały

| Element | Dostawca i stan strony | Cena strony | Status i decyzja |
|---|---|---:|---|
| `R6-2RS-SNB`, 9,525 × 22,225 × 7,14 mm, C=2,535 kN | [DigiKey PL](https://www.digikey.pl/pl/products/detail/mechatronics-bearing-group/R6-2RS-SNB/9608360), duży stan | 9,37 PLN netto / 11,53 PLN brutto za szt.; wysyłka może dominować cenę | **Dokładny kandydat.** Kupić dwie sztuki jednej serii i zmierzyć przed zamknięciem pasowań. |
| SKF `6204-2RSH`, luz normalny | [123łożysko](https://www.123lozysko.pl/lozysko/lozysko-kulkowe/jednorzedowe/6204-2rsh-skf), ponad 50 szt. | 22,21 PLN brutto za szt. | **Dokładny kandydat.** Nie zamieniać cicho na C3. |
| EN AW-6082 T6/T651, 600 × 360 × 12 mm | [Alinox](https://e-alinox.pl/pl/492-plyty), cięcie na wymiar | od 33,90 PLN/kg; około 237 PLN za 7 kg przed cięciem i dostawą | **RFQ materiałowe.** Wymaga tolerancji, płaskości i świadectwa materiału. |
| C45 / 1.1191 na wały | [Abrams](https://files.abrams-industries.com/steel/pl_pl/katalog.pdf), Ø10 i Ø20 z możliwością cięcia | RFQ | **RFQ materiałowe.** Czop 9,525 mm należy obrobić z naddatkiem po pomiarze łożysk; nie kupować przypadkowego pręta hobby bez gatunku i tolerancji. |

Pozostałe obudowy, wały, ramię, masa, elementy mocujące i obróbka pozostają
wyceną wykonawczą po dostawie oraz pomiarze części katalogowych.

## 7. Pozycje jawnie odrzucone

- Leadshine `SPS488` 48 V / 8 A — poniżej wymaganego 12,5 A;
- NBK `MJC-40CS-EBL-9.525-14` — 4,9 Nm, poniżej wymaganego 5 Nm;
- dowolne koła HTD/GT2 lub nieidentyfikowalne zamienniki Gates — brak zgodności
  z obliczeniami i opublikowanymi bezwładnościami;
- generyczna tuleja 1610-20 bez potwierdzenia współpracy z P90 Gates;
- bezpośrednie przełączanie 48 V / 30 A grzybkiem panelowym;
- Mesa `7I95T` jako automatyczny zamiennik — droższa i zmienia interfejs;
- ręcznie przykładana sonda temperatury podczas automatycznych 1000 cykli;
- KERN `FK25` jako cichy zamiennik Mark-10 bez wzorcowania i aktualizacji spec.

## 8. Orientacyjny koszt — czego jeszcze nie wiadomo

Same publiczne ceny serwa, kandydata zasilacza, stycznika, grzybka, TC-08 i
czterech łożysk dają `5 963,34 PLN brutto`, zanim doliczy się koła Gates,
tuleję, sprzęgło, E6, Mesa, miernik siły, sondy, rezystor z radiatorem,
materiały, obróbkę, przewody, zabezpieczenia, VAT i transport.

To nie jest budżet ani rekomendacja zakupowa. Pokazuje natomiast, że aparatura
pomiarowa stanowi dużą część P1. W zapytaniu o Mark-10 należy od razu pytać o
wynajem; wymagania pomiarowe nie mogą zostać obniżone wyłącznie z powodu ceny.

## 9. Gotowe zapytania ofertowe

### 9.1 EBMiA / Leadshine

> Proszę o pisemną ofertę dla jednego stanowiska testowego: dokładny
> iSV2-RS6040V48G z hamulcem, aktualna rewizja i instrukcja, CABLE-PC-1 oraz
> wszystkie potrzebne wtyki/przewody Pulse+Direction, RS485 i hamulca. Proszę
> potwierdzić gwarancję, prawo zwrotu, stan, termin i cenę brutto z dostawą do
> Polski. Proszę także pisemnie potwierdzić, czy Mean Well RSP-750-48
> (48 V, 15,7 A) może zasilać ten napęd podczas szybkich nawrotów, jakie jest
> dopuszczalne napięcie/prąd zwrotny oraz czy zalecany układ CN4 z rezystorem
> 10 Ω / 100 W jest kompletny. Proszę podać wymagania radiatora, minimalną
> rezystancję, progi i parametry monitorowania hamowania oraz ewentualny
> zalecany przez Państwa zasilacz lub dodatkowe zabezpieczenie szyny DC.

### 9.2 Gates / dystrybutor przekładni

> Proszę o jedną ofertę i rysunki dla wzajemnie zgodnego kompletu Gates:
> P18-5MGT-15AL nr 78451518 z gotowym otworem 9,525 mm i pełną retencją,
> P90-5MGT-15 nr 77091090, tuleja Gates 1610-20MM nr 78581620 wraz z wpustem
> i śrubami oraz pas 600-5MGT3-15 nr 940055202. Proszę potwierdzić autentyczność,
> dokładne otwory, rowki/wpusty, elementy dołączone, wzajemną kompatybilność,
> stan, termin oraz cenę netto/brutto z dostawą do Polski.

### 9.3 US Digital / Angst+Pfister Polska

> Proszę o ofertę i rysunek dokładnej konfiguracji enkodera
> E6-10000-787-IE-D-H-D-3: 10 000 CPR, otwór 20,0 mm, index, wyjście
> różnicowe 5 V, pokrywa przelotowa i baza D, wraz z właściwym spacerem,
> narzędziami centrującymi, śrubami oraz ekranowanym przewodem
> CA-FC10-SH-NC-6 do wolnych żył. Proszę potwierdzić, że ta kombinacja jest
> produkowana, jej pobór prądu, komplet dostawy, stan/termin i cenę brutto z
> dostawą do Polski.

### 9.4 Aparatura siły i temperatury

> Proszę o ofertę na Mark-10 M3-5, certyfikat CERT z danymi, europejski adapter
> AC1120 i dostawę do Polski. Proszę również podać możliwość krótkiego wynajmu
> wzorcowanego miernika 0–25 N o rozdzielczości nie gorszej niż 0,05 N.
> Osobno proszę o ofertę na Pico PP222 z trzema samoprzylepnymi sondami
> powierzchniowymi typu K dla obudowy serwa, łożyska i rezystora oraz jedną
> sondą temperatury otoczenia, z zakresem obejmującym temperaturę rezystora.

## 10. Następna decyzja

Najpierw należy wysłać cztery powyższe zapytania. Dopiero odpowiedzi pozwolą:

1. zatwierdzić lub odrzucić RSP-750-48 i układ hamowania;
2. zamrozić dokładny komplet Gates;
3. poprawić prześwit sprzęgła i mocowanie E6 w CAD;
4. zbudować pełny koszt P1 i zdecydować, co kupić, wynająć lub pożyczyć.

Żadne pole bramki zamówienia w `docs/p1-procurement-checklist.md` nie jest na
tym etapie spełnione samym rozeznaniem internetowym.
