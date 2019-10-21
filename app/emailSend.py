import smtplib
import email.message

class EmailClass():
    def sendEmail(fullname, receipt_id, productname):
        message = """Hey {a}! <br> <br>
                    Your order for <i>{b}</i> has sucessfully been placed and will be delivered to you shortly. <br> <br>
                    Thank you for choosing <i> QuadCore.com </i> <br> <br>
                    Sincerely, <br>
                    <b>QuadCore Systems</b>""".format(a=fullname, b = productname)

        msg = email.message.Message()
        msg['Subject'] = 'Subject 1.7'
        msg['From'] = "systems.quadcore@gmail.com"
        msg['To'] = receipt_id
        msg.add_header('Content-Type','text/html')
        msg.set_payload(message)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("systems.quadcore@gmail.com",
                "Quadcore00")
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()


EmailClass.sendEmail("Sai Khurana", "sai.khurana_ug21@ashoka.edu.in", "Casio Watch")
