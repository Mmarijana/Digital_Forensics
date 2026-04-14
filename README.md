# 🔍 FB - Forensics Viewer

FB - Forensics Viewer je desktop aplikacija razvijena u Pythonu za digitalnu forenzičku analizu Facebook arhive. Aplikacija omogućava pregled, analizu i vizualizaciju podataka iz Facebook ZIP arhive kroz moderan korisnički interfejs.

---

## 🚀 Glavne funkcionalnosti

* 📂 Učitavanje Facebook ZIP arhive
* 👤 Prikaz osnovnih informacija o nalogu
* 🔐 Analiza login aktivnosti (lokacija, IP adrese)
* 🤖 AI detekcija sumnjivih aktivnosti
* 📊 Generisanje grafikona (lokacije, vremenski tok)
* 🕒 Timeline događaja sa filtriranjem
* 💬 Analiza poruka (forenzika komunikacije)
* 🧠 Detekcija anomalija (ML – Isolation Forest)
* 🗺️ Vizualizacija login lokacija na mapi
* 🖼️ Analiza slika (detekcija AI generisanog sadržaja)
* 🧾 Export izveštaja (PDF i HTML)

---

## 🧠 Arhitektura sistema

Aplikacija je razvijena korišćenjem modularne arhitekture:

* `ui/` – korisnički interfejs (MainWindow, views)
* `*_engine.py` – logika obrade podataka (Risk, ML, Timeline, Messages)
* `archive_loader.py` – učitavanje i parsiranje arhive
* `report_generator.py` – generisanje izveštaja

Ovakav pristup omogućava jasno razdvajanje između prikaza i logike (*separation of concerns*), kao i lakšu nadogradnju sistema.

---

## 🛠️ Tehnologije

* Python
* Tkinter (GUI)
* Matplotlib (grafici)
* scikit-learn (ML analiza)
* Folium / TkinterMapView (mape)
* ReportLab (PDF izveštaji)

---

## ▶️ Pokretanje aplikacije

1. Klonirati repozitorijum:

```
git clone https://github.com/USERNAME/Digital_Forensics.git
```

2. Instalirati zavisnosti:

```
pip install -r requirements.txt
```

3. Pokrenuti aplikaciju:

```
python main.py
```

---

## 📁 Struktura projekta

```
Digital_Forensics/
│
├── ui/
├── archive_loader.py
├── risk_engine.py
├── ml_engine.py
├── timeline_engine.py
├── messages_engine.py
├── map_engine.py
├── report_generator.py
├── main.py
└── README.md
```

---

## 📌 Napomena

Aplikacija koristi test Facebook arhive koje korisnik može preuzeti sa svog naloga putem Facebook Data Export opcije.

---

## 🎓 Autor

Marijana Cvetković
Projekat iz oblasti digitalne forenzike

---
