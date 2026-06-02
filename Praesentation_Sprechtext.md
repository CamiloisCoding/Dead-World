# Dead World — Sprechtext für die Präsentation

**Vortragende:** Camilo (Entwickler) & Jannik
**Aufteilung:** Camilo = Folien 1, 5, 6, 9, 10, 11 · Jannik = Folien 2, 3, 4, 7, 8, 12 · Folie 13 gemeinsam

> Hinweis: Die Texte sind frei gesprochen gedacht — lest sie nicht 1:1 ab, sondern nutzt sie als roten Faden. Klammern `(...)` sind Regie-Hinweise, nicht zum Vorlesen.

---

## Folie 1 — Titel  → **CAMILO**

"Hallo zusammen. Wir stellen euch heute unser Spiel vor: *Dead World*.
Ich bin Camilo und habe das Spiel programmiert, und mit mir präsentiert Jannik.
*Dead World* ist ein Text-Survival-Horror im Terminal-Stil — also kein klassisches Spiel mit Maus und bunten Grafiken, sondern eines, das man komplett über Texteingaben steuert. Geschrieben ist es in Python mit Pygame, insgesamt etwa 9.000 Zeilen Code.
Jannik gibt euch jetzt einen Überblick, was euch in den nächsten Minuten erwartet."

---

## Folie 2 — Gliederung  → **JANNIK**

"Danke, Camilo. Hier seht ihr unseren Ablauf.
Wir starten mit einer kurzen Vorstellung des Spiels und der Spielidee. Danach schauen wir uns die Ziele des Spielers und die besonderen Konzepte an, die *Dead World* ausmachen. Anschließend stellen wir die NPCs und die Steuerung vor.
Camilo erklärt dann den technischen Aufbau, welche Schwierigkeiten es beim Entwickeln gab und was er dabei gelernt hat. Zum Schluss werfen wir einen Blick in die Zukunft des Projekts — und natürlich gibt es am Ende eine kurze Demo.
Fangen wir mit der Vorstellung an."

---

## Folie 3 — Vorstellung des Spiels  → **JANNIK**

"*Dead World* ist im Genre Survival-Horror angesiedelt, kombiniert mit einem klassischen Text-Adventure und einem Post-Apokalypse-Setting mit Zombies.
Es läuft auf dem PC unter Windows und wurde mit Python und Pygame entwickelt — und ist komplett auf Deutsch.
Die Grundidee: Eine sogenannte Toxoplasma-Seuche hat die Welt in Zombies verwandelt. Man spielt Albert Wesker Cristal und flüchtet sich zu Beginn in einen Bunker.
Von dort aus erkundet man über ein Retro-Terminal eine zerstörte Stadt — Krankenhaus, Bibliothek, ein Walddorf, ein Casino und sogar ein Geheimlabor. Das Ziel: überleben, kämpfen, looten und herausfinden, was hinter der Seuche steckt."

---

## Folie 4 — Spielidee & Konzept  → **JANNIK**

"Im Kern trifft hier ein klassisches Text-Adventure auf eine moderne Zombie-Apokalypse.
Das Spiel steht auf mehreren Säulen:
**Erkunden** — es gibt rund 100 handgebaute Räume, durch die man sich per Himmelsrichtung und Karte bewegt.
**Überleben** — man muss Gesundheit, Essen und Heilung im Blick behalten.
**Kämpfen** — sowohl im Nah- als auch im Fernkampf gegen Zombies und Bosse.
**Looten** — Waffen, Munition und Medkits finden und Container durchsuchen.
Dazu kommt die **Atmosphäre** mit dynamischer Musik und Sound, und natürlich **Geheimnisse** wie das Labor und versteckte Orte.
Camilo, erzähl mal, was der Spieler konkret erreichen soll."

---

## Folie 5 — Ziele des Spielers  → **CAMILO**

"Gerne. Das oberste Ziel ist simpel: **überleben** — also möglichst lange am Leben bleiben und dabei Gesundheit und Vorräte managen.
Darüber hinaus geht es darum, die **Stadt zu erkunden** und neue Gebiete freizuschalten, **Ausrüstung zu sammeln**, also bessere Waffen und Heilmittel zu finden, und **Zombies zu besiegen**, wofür man Punkte bekommt.
Man kann außerdem **Verbündete finden** — dazu gleich mehr — und am Ende geht es darum, **das Geheimnis zu lösen**: Man dringt ins Geheimlabor vor und deckt die Wahrheit über die Seuche auf.
Was *Dead World* dabei besonders macht, zeige ich euch auf der nächsten Folie."

---

## Folie 6 — Besondere Spielkonzepte  → **CAMILO**

"Ein paar Sachen waren mir beim Entwickeln besonders wichtig.
Zuerst das **echte Terminal-Feeling**: ein Amber-Phosphor-Look wie bei alten Monitoren, ein Schreibmaschinen-Effekt beim Text und fünf verschiedene Farbthemen zur Auswahl.
Dann der **intelligente Text-Parser**: Er versteht viele Verben und Synonyme — und reagiert sogar mit witzigen Antworten, wenn man Unsinn eingibt, zum Beispiel 'Iss die Waffe'.
Außerdem gibt es **dynamische Musik**, die zwischen Erkundung und Kampf wechselt, ein **Begleiter-System**, ein **Speicher- und Lade-System** und einige **versteckte Inhalte** wie das Geheimlabor mit Boss.
Den Begleiter und die Gegner stellt euch Jannik genauer vor."

---

## Folie 7 — NPCs & Begleiter  → **JANNIK**

"Der wichtigste NPC ist **Christopher Thomson** — 32 Jahre alt. Man trifft ihn unterwegs, und wenn man mit ihm spricht und sein Vertrauen gewinnt, schließt er sich einem an.
Danach folgt er einem, kämpft an der Seite mit, kann auf Befehl warten und hat eigene Lebenspunkte. Man ist also nicht mehr allein.
Auf der Gegenseite gibt es eine ganze **Gegner-Datenbank**: normale Toxoplasma-Zombies, infizierte Menschen, einen richtigen Boss im Labor mit 280 Lebenspunkten — und sogar einen geheimen Spezial-Gegner, der gegen normale Waffen immun ist und einen eigenen Schwachpunkt hat.
Wie steuert man das Ganze? Das zeige ich euch jetzt."

---

## Folie 8 — Steuerung / Gameplay  → **JANNIK**

"Wie gesagt: Alles läuft über Texteingaben, es gibt kein Maus-Gameplay.
Man **bewegt** sich mit Himmelsrichtungen wie n, o, s, w oder auch hoch und runter.
Mit Befehlen wie *schaue*, *untersuche* oder *karte* verschafft man sich einen **Überblick**.
**Items** nimmt man mit *nimm*, liest mit *lese*, isst mit *esse* oder benutzt sie mit *nutze*.
Im **Kampf** rüstet man eine Waffe aus und nutzt dann *schieße*, *schlage* oder *stich* — und muss zwischendurch nachladen.
Den **Begleiter** steuert man mit *folge mir* oder *bleib hier*, und mit *save*, *restore* oder *hilfe* gibt es die typischen **System-Befehle**.
Wie das technisch alles zusammenkommt, erklärt euch jetzt Camilo."

---

## Folie 9 — Technischer Aufbau  → **CAMILO**

"Technisch besteht das Projekt aus mehreren Dateien, damit der Code übersichtlich bleibt.
Die Hauptdatei mit dem Spielablauf hat rund 5.500 Zeilen. Daneben gibt es eine Datei nur für die Befehlslogik, eine für Events, eine für die Konstanten wie Waffen und Gegner, eine fürs Zeichnen der Oberfläche und einen Launcher, der das Spiel startet und Updates prüft.
Am Ende baue ich das alles mit PyInstaller zu einer fertigen .exe zusammen, die man einfach starten kann.
Auf der technischen Seite nutze ich Python und Pygame für Grafik und Sound, einen selbst geschriebenen Text-Parser, ein JSON-basiertes Speichersystem, und das Spiel läuft mit 60 Bildern pro Sekunde inklusive CRT-Effekt — auflösbar bis Full HD."

---

## Folie 10 — Schwierigkeiten beim Entwickeln  → **CAMILO**

"Natürlich lief nicht alles glatt.
Die größte Herausforderung war, dass meine Hauptdatei mit über 5.500 Zeilen riesig wurde — ich musste sie in mehrere Module aufteilen, damit ich überhaupt noch den Überblick behalte.
Auch der Text-Parser war knifflig: Er muss Tippfehler, viele Synonyme und unerwartete Eingaben abfangen.
Dazu kam, die rund 100 Räume sauber zu verbinden, das Kampf-Balancing fair einzustellen, Musik und Sounds richtig zu mischen und das Speichersystem zuverlässig hinzubekommen.
Und manche Bugs traten nur in bestimmten Räumen oder in einer bestimmten Reihenfolge auf — die zu finden hat oft am längsten gedauert."

---

## Folie 11 — Was ich gelernt habe  → **CAMILO**

"Aus dem ganzen Projekt habe ich eine Menge mitgenommen.
Vor allem, wie wichtig **Planung** ist — ein Game Design Document am Anfang hätte mir viel Arbeit gespart.
Ich habe gelernt, **Code in Module aufzuteilen**, wie man einen **eigenen Parser** baut und wie man Probleme im Code systematisch findet und behebt.
Außerdem, wie man **Grafik, Sound und Spiellogik** mit Pygame verbindet und am Ende alles als **fertige .exe** für andere bereitstellt.
Und ganz wichtig: dass sich ein Projekt während der Entwicklung stark verändern kann — man muss flexibel bleiben.
Jannik sagt euch jetzt noch, was wir in Zukunft vorhaben."

---

## Folie 12 — Zukunft / Verbesserungen  → **JANNIK**

"Das Spiel ist noch lange nicht fertig — es gibt viele Ideen.
Geplant sind **mehr Story-Inhalte**, Quests und ein richtiges Ende, dazu **weitere NPCs** und ein Handels- bzw. Shop-System.
Außerdem soll ein **Crafting-System** dazukommen, mit dem man eigene Items bauen kann.
Auf der technischen Seite will Camilo den Code weiter aufteilen, die Dokumentation verbessern, mehr automatische Tests einbauen, um Bugs früher zu finden, und das Speichersystem noch robuster machen.
Und vielleicht kommt irgendwann ein Tag-Nacht- oder Hunger-System dazu.
Aber genug geredet — jetzt zeigen wir euch das Spiel live."

---

## Folie 13 — Demo des Spiels  → **CAMILO + JANNIK**

**Camilo:** "Kommen wir zur Demo. Ich starte das Spiel kurz und zeige euch den Einstieg — den Bunker, die ersten Befehle und einen kleinen Kampf."

*(Spiel starten, Intro zeigen, ein paar Befehle eingeben: z. B. `schaue`, `nimm feuerlöscher`, `inventar`, eine Bewegung, einen Kampf.)*

**Jannik:** "Wie ihr seht, läuft alles über Eingaben, und das Terminal reagiert sofort darauf."

**Camilo:** "Damit sind wir am Ende unserer Präsentation. Vielen Dank fürs Zuhören — habt ihr noch Fragen?"

---

### Tipps für den Vortrag
- Redet **langsam** und macht nach jedem Folienwechsel eine kurze Pause.
- Schaut beim Sprechen ins Publikum, nicht auf die Leinwand.
- Plant für die Demo **etwas Puffer** ein, falls eine Eingabe mal nicht klappt.
- Gesamtdauer-Richtwert: ca. 8–12 Minuten plus Demo.
