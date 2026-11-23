# madutours.com

Statische Website von Madutours (Merzouga, Marokko), Spanisch und Englisch.
Nachfolger der WordPress-Seite von 2016, deren Inhalte und Fotos hier übernommen wurden.

## Struktur

- `dist/` – fertige Website, wird von Netlify ausgeliefert (`publish = "dist"`).
- `_src/content.py` – alle Texte in ES und EN, Kontaktdaten ganz oben in `SITE`.
- `_src/build.py` – Generator (Python 3 + Pillow). Erzeugt `dist/` inkl. Bildgrößen.
- `_src/style.css`, `_src/main.js` – Stylesheet und das wenige JavaScript (Menü, Lightbox, Video, Formular).
- `_src/uploads/` – Originalfotos (123 Dateien) aus dem alten WordPress-Upload-Ordner.

## Inhalt ändern

```bash
cd _src
python3 build.py
```

Danach `dist/` committen und pushen, Netlify deployt automatisch.

## Domain

madutours.com ist bei Nominalia registriert. DNS dort auf Netlify zeigen lassen
(A-Record `@` → 75.2.60.5, CNAME `www` → `<site>.netlify.app`) oder die Nameserver
auf Netlify DNS umstellen.
