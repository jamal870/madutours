# madutours.com – neue Website live schalten

Die neue Seite ist eine reine HTML-Seite (kein WordPress, kein PHP, keine Datenbank).
Sie läuft auf dem bestehenden Nominalia-Hosting (wepanel, Benutzer pv2cwyoo).

## Was in der Zip steckt

`madutours-site.zip` enthält den kompletten Inhalt des Web-Ordners:
index.html (Spanisch), en/ (Englisch), css/, js/, img/, robots.txt, sitemap.xml, 404.html,
favicon-32.png, apple-touch-icon.png, .well-known/security.txt.
Alle alten Adressen (/rutas/, /riad/, /jaimas/, /quad-buggys/, /reservas/, /contacto/ …) bleiben gültig.

## Live schalten in 5 Schritten (ohne Ausfallzeit, altes WordPress bleibt als Backup)

1. wepanel → Dateimanager → im Hauptordner `pv2cwyoo` einen neuen Ordner anlegen: `madutours_neu`
2. In diesen Ordner wechseln, oben „Upload files“, die Datei `madutours-site.zip` hochladen.
3. Rechtsklick auf die Zip → „Extract“ (bzw. „Entpacken“) in den aktuellen Ordner. Danach die Zip löschen.
   Prüfen: direkt in `madutours_neu` muss `index.html` liegen (nicht in einem Unterordner).
4. wepanel → Domains → Zeile madutours.com → „Optionen“ → „Verzeichnis ändern“ →
   `/home/pv2cwyoo/madutours_neu` wählen und speichern.
5. In der gleichen Zeile „HTTP-Umleitung erzwingen“ einschalten (http → https).

Danach madutours.com im privaten Fenster aufrufen. Fertig.

Der alte Ordner `/home/pv2cwyoo/madutours.com` mit WordPress bleibt unangetastet als Backup.
Nach ein paar Wochen kann er gelöscht werden (vorher ggf. `wp-content/uploads` sichern).

## Danach bitte prüfen / anpassen

- Telefon / WhatsApp: aktuell `+212 661 352 895` (aus der alten Seite). Stimmt die Nummer noch?
- E-Mail: aktuell `info@madutours.com`. Existiert das Postfach noch? Falls nicht, im wepanel ein
  Postfach anlegen oder eine andere Adresse eintragen.
- Beides steht zentral in `_src/content.py` ganz oben (SITE = {...}). Nach einer Änderung:
  `cd _src && python3 build.py` → neuer Inhalt liegt in `dist/`.
- Bei Google Search Console die neue sitemap.xml einreichen: https://madutours.com/sitemap.xml

## Technik

- Generator: `_src/build.py` (Python 3, braucht nur Pillow). Inhalte: `_src/content.py`.
  Originalbilder: `_src/uploads/` (123 Dateien, 77 MB, vom alten Server gesichert).
- Formular „Reservas“ öffnet WhatsApp oder das Mailprogramm mit vorformuliertem Text, kein Server nötig.
- Videos (Vimeo/YouTube) laden erst nach Klick. Karte: Google-Maps-Einbettung ohne API-Key.
- Zwei Sprachen: `/` = Spanisch, `/en/` = Englisch, mit hreflang-Tags.
