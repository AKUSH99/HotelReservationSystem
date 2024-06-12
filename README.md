# Project_Structure
This repository has the structure for to create an application with a single entry point.
This structure will be updated from time to time, please watch the commits.


        # Hotel nach Hotelname suchen:
        # name = input("Enter name hotel name: ")
        # hotel_name = sm.get_hotels_by_name(name)
        # for hotel in hotel_name:
        #     print(hotel)

Das README.md File muss folgendes enthalten:

###########

# Project Members:
# Name und Vorname der Teammitglieder die am Projekt mitgearbeitet haben
Philippe Rhiner
Sujani Ragumar
Almidin Bangoji
Berivan Zorcakmakci

# Team Roles:
#Eine kurze Übersicht, wer zu welchen Projekt-Themen beigetragen hat (also z.B. zu welchen Use-Stories, Files, Projektphasen, Rollen innerhalb des Teams etc.). Themen, die durch mehrere Teammitglieder bearbeitet wurden, dürft ihr bei allen jeweiligen Teammitgliedern aufführen.
Philippe Rhiner:
XY

Sujani Ragumar:
XY

Almidin Bangoji:
XY

Berivan Zorcakmakci:
SearchManager und UserManager u.a. die folgenden User Stories:
- 1.1.4.
- 1.1.5.
- 1.1.6.
- 1.2.
- 1.2.1.
- 1.2.2.
- 1.3.
- 1.4.
- 1.5.
- 1.6.

# Instructions:
#Instruktion für uns, wie eure Applikation benutzt werden muss (Schritt-für-Schritt Anleitung insb. welches File(s) ausgeführt werden müssen).

SearchManager
Anleitung:
SearchManager ausführen! UI-Fenster für das Hotelreservierungssystem geht auf.
Hotelsuche:
•	Auf „Suchen“ klicken! Alle Hotels werden angezeigt. Wenn man auf dem einzelnen Hotel klickt, werden alle Zimmer pro Hotel angezeigt.
•	Eingabe Stadt: alle Hotels in der entsprechenden City werden angezeigt.
•	Eingabe Sterne: alle Hotels mit den entsprechenden Sternen werden angezeigt.
•	Eingabe Max Gäste: alle Hotels mit den entsprechenden max. Gäste werden angezeigt.
•	Eingabe Startdatum und Enddatum: alle verfügbaren Zimmer werden angezeigt.
•	Eingabe Stadt und Gästeanzahl: alle Hotels in der entsprechenden Stadt mit der entsprechende Gästezahl
•	
Enthält User Storys:
1.1.	Als Gastnutzer möchte ich die verfügbaren Hotels durchsuchen, damit ich dasjenige auswählen kann, welches meinen Wünschen entspricht. 
1.1.1.	Ich möchte alle Hotels in einer Stadt durchsuchen, damit ich das Hotel nach meinem bevorzugten Standort (Stadt) auswählen kann. 
1.1.2.	Ich möchte alle Hotels in einer Stadt nach der Anzahl der Sterne durchsuchen. 
1.1.3.	Ich möchte alle Hotels in einer Stadt durchsuchen, die Zimmer haben, die meiner Gästezahl entsprechen (nur 1 Zimmer pro Buchung), entweder mit oder ohne Anzahl der Sterne. 
1.1.4. Ich möchte alle Hotels in einer Stadt durchsuchen, die während meines Aufenthaltes ("von" (start_date) und "bis" (end_date)) Zimmer für meine Gästezahl zur Verfügung haben, entweder mit oder ohne Anzahl der Sterne, damit ich nur relevante Ergebnisse sehe. 
1.1.5. Ich möchte die folgenden Informationen pro Hotel sehen: Name, Adresse, Anzahl der Sterne.
1.1.6. Ich möchte ein Hotel auswählen, um die Details zu sehen (z.B. verfügbare Zimmer [siehe 1.2]) 
1.2. Als Gastnutzer möchte ich Details zu verschiedenen Zimmertypen (EZ, DZ, Familienzimmer), die in einem Hotel verfügbar sind, sehen, einschliesslich der maximalen Anzahl von Gästen für dieses Zimmer, Beschreibung, Preis und Ausstattung, um eine fundierte Entscheidung zu treffen. 
1.2.1. Ich möchte die folgenden Informationen pro Zimmer sehen: Zimmertyp, max. Anzahl der Gäste, Beschreibung, Ausstattung, Preis pro Nacht und Gesamtpreis. 
1.2.2. Ich möchte nur die verfügbaren Zimmer sehen 



ReservationManager
Anleitung:


Enthält User Storys:
1.3. Als Gastbenutzer möchte ich ein Zimmer in einem bestimmten Hotel buchen, um meinen Urlaub zu planen. 
1.4. Als Gastnutzer möchte ich möglichst wenig Informationen über mich preisgeben, damit meine Daten privat bleiben. 
1.5. Als Gastnutzer möchte ich die Details meiner Reservierung in einer lesbaren Form erhalten (z.B. die Reservierung in einer dauerhaften Datei speichern), damit ich meine Buchung später überprüfen kann. 
1.6. Als Gastbenutzer möchte ich mich mit meiner E-Mail-Adresse und einer persönlichen Kennung (Passwort) registrieren können, um weitere Funktionalitäten nutzen zu können (z.B. Buchungshistorie, Buchungsänderung etc. [siehe 2.1]. 
2.1. Als registrierter Benutzer möchte ich mich in mein Konto einloggen, um auf meine Buchungshistorie zuzugreifen ("lesen"), damit ich meine kommenden Reservierungen verwalten kann. 
2.1.1. Die Anwendungsfälle für meine Buchungen sind "neu/erstellen", "ändern/aktualisieren", "stornieren/löschen". 

UserManager
Anleitung:
UserManager ausführen.
Login (Admin und registrierter Gast)
•	Username und Passwort eingeben, z.B. admin / password (3 Versuche möglich)
•	User wird eingeloggt
•	User wird ausgeloggt
Register as Guest
•	Username, Passwort, Vorname, Nachname, E-mailadresse, Strasse, PLZ und Ort erfassen.
•	Der neu erfasste Gast kann sich nun mit den Logindaten einloggen.
•	Der registrierte Gast wird eingeloggt
•	Der registrierte Gast wird ausgeloggt
Um Buchungen einzusehen/anzupassen usw. gehe zum InventoryManager.



InventoryManager
Anleitung:
InventoryManager starten: UI Fenster poppt auf
Login als Admin:
-	Mit folgendem Username «admin» und Passwort «password» (Hier evtl. noch max. attempts 3x hinzufügen)
-	Klicke auf Login
-	Fenster Login successful poppt auf, ok klicken.
Neues Fenster poppt auf:
1.	Um ein neues Hotel hinzuzufügen, klicke auf «Add Hotel»
-	Neues Fenster poppt auf “Add Hotel»
-	Beispieldaten eingeben (Hier müssten wir Pflicht Felder definieren, sodass alle Felder ausgefüllt werden und wir müssten die gleiche Methode wie bei user registration anwenden, um nicht bestehende Hotels nochmals hinzuzufügen. Zudem ist hier ein Fehler, vermutlich wegen der Logout Funktion: wenn man ein Hotel erfolgreich geaddet hat, muss man sich zuerst ausloggen um weitere hinzuzufügen oder zu entfernen etc. )
-	Konsole in Pycharm anschauen: «Hotel «neu hinzugefügte Hotel» wurde erfolgreich hinzugefügt». (Können wir dies noch in die UI integrieren?)
-	sqliteonline.com aufrufen und das DB File öffnen. Mit einem rechtsklick auf die Tabelle «Hotel» klicken und SELECT (Show table) wählen.
-	Das neu hinzugefügte Hotel sollte nun auch in der Datenbank ersichtlich sein. ID merken!
-	Mit dem Button «Logout» ausloggen oder Programm.

-	Melde dich für die nächste Funktion, um ein Hotel zu entfernen erneut an.
2.	Um ein bestehendes Hotel zu entfernen, klicke auf «Remove Hotel»
-	Ein neues Fenster poppt auf. Hotel ID eingeben.
-	In der Konsole steht: «Hotel mit ID 'entfernte Hotel ID' erfolgreich entfernt.»
-	Zurückkehren zu sqliteonline.com und Datenbank neu hinzufügen, nun sieht man, dass das gewünschte Hotel entfernt wurde. 
-	Mit dem Button «Logout» ausloggen oder Programm.

-	Melde dich für die nächste Funktion, um eine Hotel Information zu ändern erneut an.
3.	Klicke auf Update Hotel Info
4.	Suche in SQLite die Hotel ID, die du ändern möchtest
5.	Gebe beispielsweise eine neue Sternenanzahl an.
6.	Klicke auf submit
7.	Überprüfe in pycharm in der konsole die meldung «Hotel mit ID '1' erfolgreich aktualisiert.»
8.	Wechsle zu Sqlite und aktualisiere die Hotel Tabelle. Du siehst nun die gänderte Information
9.	Melde dich für die nächste Funktion, um die Bookinglist aufzurufen erneut an.
10.	Ein Fenster mit den Booking-Daten poppt auf. Dies ist nützlich für Mitarbeitende, um die Bookings zu überprüfen
11.	(Optional) Melde dich für die nächste Funktion, um ein Booking aus der Bookinglist zu entfernen erneut an.
12.	Klicke auf delete booking
13.	Suche dir in sqlite in der tabelle booking eine booking id aus, die du entfernen möchtest und gebe die id im ui wieder ein.
14.	Klicke auf submit und überprüfe in der konsole in pycharm «Buchung mit ID '38' erfolgreich gelöscht.»
15.	Aktualisiere deine tabelle in sqlite. Du siehst dass die Buchung mit der gewünschten ID auch in der Datenbank entfernt wurde.
16.	Melde dich für die nächste Funktion, um die Preise für die Räume zu aktualisieren erneut an.
17.	Klicke auf «update Room Price»
18.	(Optional) Wechsle zu sqlite und öffne die tabelle «room» Suche eine room ID aus (Problematik: wie füge ich in sqlite eine weitere spalte id für room ein???)
Login als registrierter User:
-	Mit folgendem Username «sabrina.schmidt@bluemail.ch» und Passwort «SuperSecret» (Hier evtl. noch max. attempts 3x hinzufügen)
-	Klicke auf Login
-	Fenster Login successful poppt auf, ok klicken.
«View my Booking» sieht der Nutzer/user alle Buchungen
«Update my Booking» mit booking id, datum ändern
«Delete my booking»


Enthält User Storys:
3.1. Als Admin-Nutzer des Buchungssystems möchte ich die Möglichkeit haben, Hotelinformationen zu pflegen, um aktuelle Informationen im System zu haben. 
3.1.1. Ich möchte neue Hotels zum System hinzufügen 
3.1.2. Ich möchte Hotels aus dem System entfernen 
3.1.3. Ich möchte die Informationen bestimmter Hotels aktualisieren, z. B. den Namen, die Sterne usw. 
3.2. Als Admin-Nutzer des Buchungssystems möchte ich alle Buchungen aller Hotels sehen können, um eine Übersicht zu erhalten. 
3.3. Ich möchte alle Buchungen bearbeiten können, um fehlende Informationen zu ergänzen (z.B. Telefonnummer) [Optional]. 
3.4. Ich möchte in der Lage sein, die Zimmerverfügbarkeit zu verwalten und die Preise in Echtzeit im Backend-System der Anwendung zu aktualisieren [Optional].

MainMenu
Anleitung:
MainMenu ausführen.
Option 1 wählen:
Login (Admin und bereits registrierter Gast)
•	Username und Passwort eingeben, z.B. admin / password (3 Versuche möglich)
•	User wird eingeloggt
•	User wird ausgeloggt
Option 2 wählen:



# Assumtions / Interpretations:
#Annahmen und Interpretationen, falls welche vorhanden sind