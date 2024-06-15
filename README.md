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

Wir starteten ursprünglich alle gemeinsam mit der Zusammenarbeit am SearchManager, was uns einen grundlegenden Einblick in die Anforderungen und die technische Struktur gab. 
Jedoch wurde bald klar, dass dieser Ansatz nicht effizient war, deshalb haben wir die Aufgaben verteilt.
Um den Workflow zu optimieren, teilten wir das Team in kleinere Gruppen, wobei sich jede auf spezifische Aufgaben in den diversen Managern konzentrierte – ReservationManager, UserManager, InventoryManager und SearchManager. 
Diese Neustrukturierung ermöglichte es uns, parallel an verschiedenen Systemkomponenten zu arbeiten, wodurch wir schneller vorankamen und flexibler auf Änderungen reagieren konten. 
Mit der Zunahme der Komplexität stellten wir aber vermehrt fest, dass wir bei Problemen nicht alleine weiter kamen. Deshalb haben wir angefangen wieder in zweier Teams oder teilweise in der ganzen Gruppe Probleme zu besprechen und zu programmieren.
Diese dynamische und kollektive Arbeitsweise verbesserte nicht nur die Produktivität, sondern auch die Qualität des Endprodukts, indem jeder Einblick und Einfluss auf die Gestaltung jeder Komponente hatte. 
Durch diese Erfahrung lernten wir die Bedeutung von Anpassungsfähigkeit und Teamarbeit in der Softwareentwicklung schätzen, was sich deutlich in der Zufriedenheit im Team und der Leistungsfähigkeit des fertigen Systems widerspiegelte.

Fazit: Alle Mitglieder haben praktisch zu allen Managern etwas beigetragen.

# Instructions:
#Instruktion für uns, wie eure Applikation benutzt werden muss (Schritt-für-Schritt Anleitung insb. welches File(s) ausgeführt werden müssen).

# SearchManager
## Enthält User Storys:
1.1.	Als Gastnutzer möchte ich die verfügbaren Hotels durchsuchen, damit ich dasjenige auswählen kann, welches meinen Wünschen entspricht. 
1.1.1.	Ich möchte alle Hotels in einer Stadt durchsuchen, damit ich das Hotel nach meinem bevorzugten Standort (Stadt) auswählen kann. 
1.1.2.	Ich möchte alle Hotels in einer Stadt nach der Anzahl der Sterne durchsuchen. 
1.1.3.	Ich möchte alle Hotels in einer Stadt durchsuchen, die Zimmer haben, die meiner Gästezahl entsprechen (nur 1 Zimmer pro Buchung), entweder mit oder ohne Anzahl der Sterne. 
1.1.4.  Ich möchte alle Hotels in einer Stadt durchsuchen, die während meines Aufenthaltes ("von" (start_date) und "bis" (end_date)) Zimmer für meine Gästezahl zur Verfügung haben, entweder mit oder ohne Anzahl der Sterne, damit ich nur relevante Ergebnisse sehe. 
1.1.5.  Ich möchte die folgenden Informationen pro Hotel sehen: Name, Adresse, Anzahl der Sterne.
1.1.6.  Ich möchte ein Hotel auswählen, um die Details zu sehen (z.B. verfügbare Zimmer [siehe 1.2]) 
1.2.    Als Gastnutzer möchte ich Details zu verschiedenen Zimmertypen (EZ, DZ, Familienzimmer), die in einem Hotel verfügbar sind, sehen, einschliesslich der maximalen Anzahl von Gästen für dieses Zimmer, Beschreibung, Preis und Ausstattung, um eine fundierte Entscheidung zu treffen. 
1.2.1.  Ich möchte die folgenden Informationen pro Zimmer sehen: Zimmertyp, max. Anzahl der Gäste, Beschreibung, Ausstattung, Preis pro Nacht und Gesamtpreis. 
1.2.2.  Ich möchte nur die verfügbaren Zimmer sehen 

## Anleitung:
SearchManager ausführen! GUI-Fenster für das Hotelreservierungssystem öffnet sich.
Hotelsuche:
-	SearchManager.py ausführen, GUI Fenster öffnet sich
-	Um alle Hotels anzuzeigen, reicht es, ohne Angabe eines Kriteriums auf Search zu klicken
-	Ansonsten können einzelne Kriterien ausgewählt werden (Stadt, Anzahl Sterne, Anzahl Gäste und das Buchungsdatum)
-	Nach einem Klick auf Suche werden alle Hotels angezeigt, welche den Kriterien entsprechen
-	Hier kann zur Wahl eines Hotels dessen ID eingegeben werden, so dass die Zimmer des Hotels angezeigt werden
-	Danach kann die ID eines Raums ausgewählt werden, um dessen Details anzuzeigen
-	Hinweis: Zum Abschliessen der Suche müssen die einzelnen Fenster geschlossen werden



# ReservationManager
## Enthält User Storys:
1.3.    Als Gastbenutzer möchte ich ein Zimmer in einem bestimmten Hotel buchen, um meinen Urlaub zu planen. 
1.4.    Als Gastnutzer möchte ich möglichst wenig Informationen über mich preisgeben, damit meine Daten privat bleiben. 
1.5.    Als Gastnutzer möchte ich die Details meiner Reservierung in einer lesbaren Form erhalten (z.B. die Reservierung in einer dauerhaften Datei speichern), damit ich meine Buchung später überprüfen kann. 
1.6.    Als Gastbenutzer möchte ich mich mit meiner E-Mail-Adresse und einer persönlichen Kennung (Passwort) registrieren können, um weitere Funktionalitäten nutzen zu können (z.B. Buchungshistorie, Buchungsänderung etc. [siehe 2.1]. 
2.1.    Als registrierter Benutzer möchte ich mich in mein Konto einloggen, um auf meine Buchungshistorie zuzugreifen ("lesen"), damit ich meine kommenden Reservierungen verwalten kann. 
2.1.1.  Die Anwendungsfälle für meine Buchungen sind "neu/erstellen", "ändern/aktualisieren", "stornieren/löschen". 

## Anleitung:
-	ReservationManager.py ausführen (funktioniert in Konsole)
  -	Wahl aus drei Optionen (Eingabe über Tastatur):
1: «Proceed as guest with minimal information» – Erstellt eine Buchung ohne Registrierung als Nutzer und erhält kein Login
  	Vorname, Nachname und E-Mail Adresse erfassen
  	City (Ort für Hotel) erfassen
  	Gewünschte maximale Anzahl Gäste erfassen
  	Sterne (optional) erfassen
  	Street, ZIP-Code und City erfassen (Adresse des Gastes)
  	Datumsangaben erfassen (Start und Enddatum, Format YYYY.MM.DD)
  	Danach kann ein Hotel ausgewählt werden anhand der ID 
  	Aus den verfügbaren Zimmern des gewählten Hotels kann das gewünschte ausgewählt werden
  	Daraufhin wird die Buchung in die Datenbank geschrieben, die Booking ID wird angezeigt und ein CSV-File mit den Buchungsdetails erstellt
2: «Register as a new user» - Buchung mit Registrierung als Nutzer (erhält ein Login)
  	Vorname, Nachname und E-Mail Adresse erfassen
  	Username und Passwort setzen
  	Adresse des Gastes erfassen
  	Anschliessend Suche nach Hotel mit der Angabe der Stadt, Anzahl Gäste, Reisedaten und optional Sterne
  	Anzeige der passenden Hotels, die Hotel ID wird ausgewählt
  	Es folgt eine Liste der verfügbaren Zimmer, aus welchen anhand der ID eines ausgewählt werden kann
  	Daraufhin wird die Buchung wiederum in die Datenbank geschrieben, die Booking ID wird angezeigt und ein CSV-File mit den Buchungsdetails erstellt
3: “Log in to an existing account” – Einloggen in einen bestehenden Account (hat bereits ein Login)
  	Eingabe des Nutzernamens (Beispiel: sabrina.schmidt@bluemail.ch
  	Eingabe des Passworts (Beispiel: SuperSecret)
  	Anschliessend Suche nach Hotel mit der Angabe der Stadt, Anzahl Gäste, Reisedaten und optional Sterne
  	Anzeige der passenden Hotels, die Hotel ID wird ausgewählt
  	Es folgt eine Liste der verfügbaren Zimmer, aus welchen anhand der ID eines ausgewählt werden kann
  	Daraufhin wird die Buchung wiederum in die Datenbank geschrieben, die Booking ID wird angezeigt und ein CSV-File mit den Buchungsdetails erstellt




# UserManager

## Anleitung:
UserManager ausführen! Siehe Konsole.

Login als Admin mit username und password: admin/password
	- erfolgreich eingeloggt
	- Folgende Meldung erscheint "Do you want to register a new admin? (yes/no): "
    	-"yes" eingeben
	  		-ein neues username und password für den neuen Admin eingeben.
	  		-Das neue Admin Login wird erfolgreich registriert.
	  		-Programm wird beendet.
  		-"no" eingeben
-			-Admin wird ausgeloggt. Programm wrid beendet.

Login als registrierter User auch möglich. Es können aber keine weiteren Schritte ausgeführt werden. 


# InventoryManager

## Enthält User Storys:
3.1.    Als Admin-Nutzer des Buchungssystems möchte ich die Möglichkeit haben, Hotelinformationen zu pflegen, um aktuelle Informationen im System zu haben. 
3.1.1.  Ich möchte neue Hotels zum System hinzufügen 
3.1.2.  Ich möchte Hotels aus dem System entfernen 
3.1.3.  Ich möchte die Informationen bestimmter Hotels aktualisieren, z. B. den Namen, die Sterne usw. 
3.2.    Als Admin-Nutzer des Buchungssystems möchte ich alle Buchungen aller Hotels sehen können, um eine Übersicht zu erhalten. 
3.3.    Ich möchte alle Buchungen bearbeiten können, um fehlende Informationen zu ergänzen (z.B. Telefonnummer) [Optional]. 
3.4.    Ich möchte in der Lage sein, die Zimmerverfügbarkeit zu verwalten und die Preise in Echtzeit im Backend-System der Anwendung zu aktualisieren [Optional].

## Anleitung:
InventoryManager starten: UI-Fenster poppt auf
Login als Admin:
-	Mit folgendem Username «admin» und Passwort «password»
-	Klicke auf Login
-	Fenster Login successful poppt auf, ok klicken.
Neues Fenster poppt auf:
1.	Um ein neues Hotel hinzuzufügen, klicke auf «Add Hotel»
-	Neues Fenster poppt auf «Add Hotel»
-	Beispieldaten eingeben (Hier müssten wir Pflicht Felder definieren, sodass alle Felder ausgefüllt werden und wir müssten die gleiche Methode wie bei user registration anwenden, um nicht bestehende Hotels nochmals hinzuzufügen. Zudem ist hier ein Fehler, vermutlich wegen der Logout Funktion: wenn man ein Hotel erfolgreich geaddet hat, muss man sich zuerst ausloggen um weitere hinzuzufügen oder zu entfernen etc. )
-	Konsole in Pycharm anschauen: «Hotel «neu hinzugefügte Hotel» wurde erfolgreich hinzugefügt». (Können wir dies noch in die UI integrieren?)
-	sqliteonline.com aufrufen und das DB File öffnen. Mit einem rechtsklick auf die Tabelle «Hotel» klicken und SELECT (Show table) wählen.
-	Das neu hinzugefügte Hotel sollte nun auch in der Datenbank ersichtlich sein. ID merken!
-	Mit dem Button «Logout» ausloggen oder Programm.

-	Melde dich für die nächste Funktion, um ein Hotel zu entfernen erneut an.
2.	Um ein bestehendes Hotel zu entfernen, klicke auf «Remove Hotel»
-	Ein neues Fenster poppt auf. Hotel ID eingeben.
-	In der Konsole steht: «Hotel mit ID (entfernte Hotel ID) erfolgreich entfernt.»
-	Zurückkehren zu sqliteonline.com und Datenbank neu hinzufügen, nun sieht man, dass das gewünschte Hotel entfernt wurde. 
-	Das UI-Fenster (im PyCharm) schliessen oder mit Button «Logout» ausloggen.

-	InventoryManager wieder starten und nochmals einloggen als admin, um eine Hotel Information zu ändern.
3.	Auf «Update Hotel Info» klicken 
-   Im sqliteonline.com die Hotel ID suchen, welche geändert werden soll 
-   Änderung durchführen. Beispiel: Eine neue Sternenanzahl eingeben. 
-   Auf submit klicken 
-   Im PyCharm in der Konsole erscheint die Meldung «Hotel mit ID (erscheint die ID vom geänderten Hotel) erfolgreich aktualisiert.» 
-   Zurückkehren zu sqliteonline.com und Datenbank neu hinzufügen, nun sieht man, die Änderung, welche eben gemacht wurde. 
-   Das UI-Fenster (im PyCharm) schliessen oder mit Button «Logout» ausloggen.

-   InventoryManager wieder starten und nochmals einloggen als admin, um die Bookinglist aufzurufen. 
4.  Auf «List Booking» klicken   
-   Ein Fenster mit den Booking-Daten poppt auf. Dies ist nützlich für Mitarbeitende, um die Bookings zu überprüfen.
-   Booking ID merken
5.  Auf «Update Booking» klicken
-   Boodking ID eingeben und die gewünschte Änderung.
-   Zurückkehren zu sqliteonline.com und Datenbank neu hinzufügen, nun sieht man, die Änderung, welche eben gemacht wurden. Dafür mit einem rechtsklick auf die Tabelle «Booking» klicken und SELECT (Show table) wählen.
-   Das UI-Fenster (im PyCharm) schliessen oder mit Button «Logout» ausloggen.

-   InventoryManager wieder starten und nochmals einloggen als admin, um eine Buchung zu löschen.
6.  Auf «Delete Booking" klicken
-   sqliteonline.com in der Tabelle "Booking" eine "Booking ID" auswählen, welche gelöscht werden soll. 
-   Die ausgewählte Booking ID im UI-Fenster eingeben
-   Auf submit klicken 
-   Im PyCharm in der Konsole erscheint die Meldung «Buchung mit ID (Booking ID, welche eben gelöscht wurde) erfolgreich gelöscht.»
-   Zurückkehren zu sqliteonline.com und Datenbank neu hinzufügen, nun sieht man, in der Booking Tabelle die gelöschte Buchung nicht mehr.
-   Das UI-Fenster (im PyCharm) schliessen oder mit Button «Logout» ausloggen.

-  	InventoryManager wieder starten und nochmals einloggen als admin, um die Preise für die Räume zu aktualisieren.
7.  Auf «Update Room Price» klicken
-   sqliteonline.com in der Tabelle "Room" eine "Room ID" auswählen, in der der Preis geändert werden soll.
-   Room ID im UI-Fenster eingeben
-   Auf submit klicken
-   Im PyCharm in der Konsole erscheint die Meldung «Preis des Zimmers mit ID (erscheint die Room ID, bei der der Preis geändert wurde) erfolgreich aktualisiert.»
-   Das UI-Fenster (im PyCharm) schliessen oder mit Button «Logout» ausloggen.

InventoryManager starten: UI-Fenster poppt auf
Login als registrierter User:
-	Mit folgendem Username «sabrina.schmidt@bluemail.ch» und Passwort «SuperSecret» 
-	Klicke auf Login
-	Fenster Login successful poppt auf, ok klicken.
Neues Fenster poppt auf:
1.  Auf «View my Booking» klicken, um alle Buchungen zu sehen (eigene Buchungen)  
2.  Auf «Update my Booking» klicken, um eine Buchung zu ändern (eigene Buchung)
3.  Auf «Delete my booking» klicken, um eine Buchung zu stornieren/löschen (eigene Buchung) 



# MainMenu

## Anleitung:

MainMenu ausführen! Siehe Konsole.

Option "1. Login to an existing account" eingeben, um in ein bereits existierendes Konto einzuloggen

	Username und Password eingeben: registrierter admin: admin /password
    - Siehe Konsole: Sie werden eingeloggt.
	- Folgende Optionen erschienen
		1. ADMIN MENU!
		- Das Admin Menu befindet sich in InventoryManager. Um das Admin MainMenu zu verwalten, InventoryManager starten!
		2. To register a new admin!
		- Um einen neuen Admin anzulegen, UserManager starten!
		3. Logout and return to Main Menu!
		- Admin wird ausgelogt und kehrt zurück zum Main Menu.
 
	Username und Password eingeben: registrierter user: sabrina.schmidt@bluemail.ch /SuperSecret
	-Siehe Konsole: Sie werden eingeloggt als registrierter User.
	-Folgende Optionen erscheinen:
		1. Logout and return to Main Menu!
		- Sie werden ausgeloggt und kehren zurück zum Main Menu.
		2. Show all Hotels
		- Alle Hotels werden angezeigt. Um eine detaillierte Suche durchzuführen, SearchManager starten.
		3. Make a Reservation
		- Um eine Reservation durchzuführen, ReservationManager starten.
		4. Manage Bookings
		- Um Buchungen zu verwalten, InventoryManager starten.
		5. Exit
		- Sie werden aus dem System ausgeloggt.
 
Option "2. Create an account as a registered user" um einen registrierten user zu erstellen.
	- username, password, fristname, lastname, email, street, zip und city eingeben.
  	- Sie werden eingeloggt.
  	-Folgende Optionen erscheinen:
      	1. Show all Hotels
      	- Alle Hotels werden angezeigt. Um eine detaillierte Suche durchzuführen, SearchManager starten
      	2. Search by Name
      	- Name eines existierenden Hotel eingeben. Alle angeben zu diesem Hotel erscheinen.
      	3. Book a Room for your stay
      	- Um eine Reservation durchzuführen, ReservationManager starten.
      	4. Exit
      	- Sie werden aus dem System ausgeloggt.

Option "3. Search Hotels (without register)", um alle Hotels anzuschauen und nach Namen zu recharchieren.
	-Folgende Optionen erscheinen:
		1. Show all Hotels
		- Alle Hotels werden angezeigt. Um eine detailierte Suche durchzuführen, SearchManager starten
		2. Search by Name
		- Name eines existierenden Hotel eingeben. Alle angeben zu diesem Hotel erscheinen.
		3. Exit
		-System wird geschlossen.


Option "4. Exit" wählen, um das System zu beenden.
	-Folgende Meldung erscheint "Thank you for visiting. See you next time!" 
	-System wird geschlossen.


# Assumtions / Interpretations:
#Annahmen und Interpretationen, falls welche vorhanden sind

-Guest hat kein login, kann aber Buchungen vornehmen (kann sie nicht einsehen).
-
