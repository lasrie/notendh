# -*- coding: utf-8 -*-
#Author: Lasse Riess, DHBW Stuttgart WWI2013F, 2014
import re
import mechanize
from bs4 import BeautifulSoup
import smtplib
import os.path
from time import *

lt = localtime()
print "################## Neuer Durchgang ######################"
print strftime("Datum: %d.%m.%Y", lt)
print strftime("Uhrzeit: %H:%M:%S", lt)

#----------------------------------------------------------HTML-Datei abrufen-----------------------------------------------------------------------------------------------------------
br = mechanize.Browser()
#Willkomensseite aufrufen
response = br.open("https://dualis.dhbw.de/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N000000000000001,-N000324,-Awelcome")
#Loginform auswaehlen
br.select_form('cn_loginForm')
#und ausfuellen
control = br.form.find_control("usrname")
control.value = "#######"
control = br.form.find_control("pass")
control.value = "#####"
response = br.submit()

#Aus den Links auf der Seite nach dem Login den heraussuchen, dessen Text mit 'Leistungs' anfaengt -> 'ae'-Problem
for link in br.links():
    str = link.text
    if str.startswith('Leistungs'):
#dem Link folgen
	response1 = br.follow_link(link)
#Leistungsuebersicht ausgeben
	html = response1.read()

#-----------------------------------------------------------Faecher und Noten aus der HTML Datei lesen------------------------------------------------------------------------------------
soup = BeautifulSoup(html)
table = soup.find("table", { "class" : "nb list students_results" })
i = 0
faecher = []
noten = []
for row in table.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) > 5:
	best = cells[5]
	img = best.find('img')
	bestanden = img.get('title')
	if bestanden != 'Offen':
		loknoten = []
		fachname = cells[1].find('a').text
		ausgabeString = cells
		note = cells[4].text
		faecher.append(fachname)
		loknoten.append(fachname)
		loknoten.append(bestanden)
		loknoten.append(note)
		noten.append(loknoten)

faecherStr = ';'.join(faecher)
faecherStr = faecherStr.replace(u"ü","ue")
faecherStr = faecherStr.replace(u"ö","oe")
faecherStr = faecherStr.replace(u"ä","ae")
faecherStr = faecherStr.replace(u"ß","ss")
faecherStr = faecherStr.replace(u"Ä","Ae")
faecherStr = faecherStr.replace(u"Ö","Oe")
faecherStr = faecherStr.replace(u"Ü","Ue")

#-----------------------------------------------------------Daten lesen/speichern, um zu entscheiden, ob Mails gesendet werden muessen----------------------------------------------------
neueFaecher = []
if os.path.isfile("./fachspeicher.dat"):
    f = open('./fachspeicher.dat', 'r+')
    dateiText = f.read()
    print len(dateiText)
    if len(dateiText) == len(faecherStr):
        #Daten in der Datei sind aktuell
        print "Datei ist aktuell"
        mailSenden = False
    else:
        #Daten sind nicht aktuell, werden neu in die Datei geschrieben
        f.write(faecherStr)
        print "Datei neu geschrieben"
        mailSenden = True
        #Herausfinden, welches Fach hinzugekommen ist
        faecherArr = faecherStr.split(";")
        dateiArr = dateiText.split(";")
        i = 0
        for fach in faecherArr:
            if dateiArr[i] == fach:
                i = i + 1
            else:
                neueFaecher.append(fach)
else:
    f = open('./fachspeicher.dat', 'a')
    mailSenden = False
    print "Datei neu erstellt, Skript muss erneut laufen"


#----------------------------------------------------------Emails senden------------------------------------------------------------------------------------------------------------------
if mailSenden:
    msgIch = "\n Hallo Lasse,\n Na, alles klar? \n \n Es gab neue Noten: \n \n \n "
    for note in noten:
        note[0] = note[0].replace(u"ü","ue")
        note[0] = note[0].replace(u"ö","oe")
        note[0] = note[0].replace(u"ä","ae")
        note[0] = note[0].replace(u"ß","ss")
        note[0] = note[0].replace(u"Ä","Ae")
        note[0] = note[0].replace(u"Ö","Oe")
        note[0] = note[0].replace(u"Ü","Ue")
        msgIch = msgIch + note[0] + " hast du mit einer Note von " + note[2] + " " + note[1] + "\n \n"


    msgIch = msgIch + "Gruss, \n\nDein Lasse :)"
  #Emails einfuegen!



    msg = "\n" + "Hallo,"+"\n\n" + "Es sind Noten in den folgenden Fächern online:\n"
    print neueFaecher
    for fach in neueFaecher:
        msg = msg +"\n"+ fach.encode('ascii', 'ignore')+ "\n"

    smtpserver = smtplib.SMTP("smtp.1und1.de",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(user, pwd)
    header = 'To:' + to + '\n' + 'From: ' + user + '\n' + 'Subject:Neue Noten online! \n'
    msgIchk = header + msgIch
    smtpserver.sendmail(user, to,msgIchk)

    header = 'To:' + to2 + '\n' + 'From: ' + user + '\n' + 'Subject:Neue Noten online! \n'
    msgk = header + msg
    smtpserver.sendmail(user, to2,msgk)
    smtpserver.close()
