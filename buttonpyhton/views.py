from django.shortcuts import render
from .models import OneEmail
import requests

#Imports of the reading
import imapclient
import pyzmail
from imapclient import IMAPClient

#helping with dates
from datetime import datetime, timedelta

def button(request):
    return render(request , 'home.html')


def output(request):
    data = requests.get("https://reqres.in/api/users")
    print(data.text)
    data = data.text
    return render(request , 'home.html' , {'data' : data})



def external(request):
    listOfEmail = []
    search_inp = request.POST.get('param')
    dates = request.POST.get('dateDropdown')
    
   
    #for Dates
    today = datetime.now()
    y = today - timedelta(days=int(dates))
    date = y.strftime("%d-%b-%Y")
    


    imapObj = IMAPClient('imap.gmail.com', ssl=True)
    imapObj.login('ITSMOHITMK99@gmail.com', 'mxuulimltcpnzxzy')

    imapObj.select_folder('INBOX', readonly=True)
    

    #**********************IF THE SERCH AREA IS EMPTY******************
    if(search_inp ==""):

        UIDs = imapObj.search([u'SINCE', date ,u'SUBJECT' , "meeting"])
        #counter for id
        count = 1
        for i in UIDs:
            rawMessages = imapObj.fetch([i], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(rawMessages[i][b'BODY[]'])
            random = message.text_part.get_payload().decode(message.text_part.charset)

            
            begin_detail1 = random.find("My Webex meeting is in progress")
            begin_detail2 = random.find("inviting you to a scheduled Webex meeting.")
            
            if(begin_detail1>begin_detail2):
                extraLen = len("My Webex meeting is in progress")
                begin_detail = begin_detail1+extraLen 
            else:
                extraLen = len("inviting you to a scheduled Webex meeting.")
                begin_detail = begin_detail2 + extraLen
                
                
            end_detail = random.find("India Time (Mumbai, GMT+05:30")
            if(end_detail== -1):
                end_detail = random.find("(UTC+05:30) Chennai, Kolkata, Mumbai")
            
            nameAndTime = random[begin_detail:end_detail]

            #Meeting Link!!!!!!!!!
            end_meeting1 = random.find("https://meet.google.com")
            
            if(end_meeting1 == -1):
                end_meeting2 = random.find("https://sses.webex.com")

            #Creating an Object aand Adding to the list
            email = OneEmail()
            email.id = count
            count = count+1



            if(end_meeting1 != -1 or end_meeting2 != -1):
                if(end_meeting1 != -1):
                    meetingLink = random[end_meeting1:end_meeting1+37]
                else:
                    meetingLink = random[end_meeting2:end_meeting2+73]
            
                #########
                email.link = meetingLink
                #details
                if(begin_detail1 !=-1 or begin_detail2 != -1):
            
                    ###########
                    email.messege = nameAndTime
                    
                else:
                
                    #########
                    msg1 = message.get_subject() + '\n' + str(message.get_addresses('from'))
                    email.messege = msg1

            
                print(email.link)
                listOfEmail.append(email)
    
    else:

        UIDs = imapObj.gmail_search(search_inp)
        count = 1
        for i in UIDs:
            rawMessages = imapObj.fetch([i], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(rawMessages[i][b'BODY[]'])
            if(message.text_part != None):
                random = message.text_part.get_payload().decode(message.text_part.charset)
            #Creating an Object aand Adding to the list
                email = OneEmail()
            
                email.id = count
                count = count+1
                email.messege = message.get_subject() 
            
                end_meeting1 = random.find("https://meet.google.com")
            
                if(end_meeting1 == -1):
                    end_meeting2 = random.find("https://sses.webex.com")
            
                if(end_meeting1 != -1 or end_meeting2 != -1):
                    if(end_meeting1 != -1):
                        meetingLink = random[end_meeting1:end_meeting1+37]
                    else:
                        meetingLink = random[end_meeting2:end_meeting2+73]
                    
                    email.link = meetingLink

                else:
                    email.link = "No Link Available"



            listOfEmail.append(email)
            
    imapObj.logout()
    return render(request , 'home.html' , {'listEmails' : listOfEmail})