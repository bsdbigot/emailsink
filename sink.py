#!/usr/local/bin/python

#PLEASE take care to read through the inline notes.  There aren't many.



import asyncore

from datetime import datetime
from smtpd import SMTPServer

#numpy is a third-party add-on which will have to be installed
import numpy







#set this to the public IP, or whatever IP you want to catch mail on
bindip = '192.168.5.245'
#set this to the port this server should bind to
#WARNING: you may need root privs, depending on the port
bindport = 25
#set this to 1 if you want to save copies of every inbound email
#note that even if we bounce the email, we will save a copy
savefile = 0

#place your bounce messages in returnmap dictionary.  Total weighted values should add up to less than 1.0
#later, the proc will calculate 1.0 - total bounce values and use that for success messages
#so, if you have >= 100 of these in here at 0.01, you're going never going to get success

returnmap = {
	'421 4.4.5 Server busy, try again later.': 0.01,
	'421 4.7.0 IP not in whitelist for RCPT domain, closing connection.': 0.01,
	'421 4.7.0 Our system has detected an unusual rate of unsolicited mail originating from your IP address. To protect our users from spam, mail sent from your IP address has been temporarily blocked. Review our Bulk Senders Guidelines.': 0.01,
	'421 4.7.0 Temporary System Problem. Try again later.': 0.01,
#	'421 4.7.0 TLS required for RCPT domain, closing connection.': 0.01,
	'421 4.7.0 Try again later, closing connection. This usually indicates a Denial of Service (DoS) for the SMTP relay at the HELO stage.': 0.01,
	'450 4.2.1 The user you are trying to contact is receiving mail too quickly. Please resend your message at a later time. If the user is able to receive mail at that time, your message will be delivered. For more information, review this article.': 0.01,
	'450 4.2.1 The user you are trying to contact is receiving mail at a rate that prevents additional messages from being delivered. Please resend your message at a later time. If the user is able to receive mail at that time, your message will be delivered. For more information, review this article.': 0.01,
	'450 4.2.1 Peak SMTP relay limit exceeded for customer. This is a temporary error. For more information on SMTP relay limits, please contact your administrator or review this article.': 0.01,
	'451 4.3.0 Mail server temporarily rejected message.': 0.01,
	'451 4.3.0 Multiple destination domains per transaction is unsupported. Please try again.': 0.01,
	'451 4.4.2 Timeout - closing connection.': 0.01,
#	'451 4.5.0 SMTP protocol violation, see RFC 2821. ': 0.01,
	'452 4.2.2 The email account that you tried to reach is over quota. Please direct the recipient to this article.': 0.01,
	'452 4.5.3 Domain policy size per transaction exceeded, please try this recipient in a separate transaction.': 0.01,
#	'452 4.5.3 Your message has too many recipients. For more information regarding Google\'s sending limits, review this article.': 0.01,
#	'454 4.5.0 SMTP protocol violation, no commands allowed to pipeline after STARTTLS, see RFC 3207.': 0.01,
#	'454 4.7.0 Cannot authenticate due to temporary system problem. Try again later.': 0.01,
#	'454 5.5.1 STARTTLS may not be repeated.': 0.01,
#	'501 5.5.2 Cannot Decode response.': 0.01,
#	'501 5.5.4 HELO/EHLO argument is invalid, please review this article.': 0.01,
#	'502 5.5.1 Too many unrecognized commands, goodbye.': 0.01,
#	'502 5.5.1 Unimplemented command.': 0.01,
#	'502 5.5.1 Unrecognized command.': 0.01,
#	'503 5.5.1 EHLO/HELO first.': 0.01,
#	'503 5.5.1 MAIL first.': 0.01,
#	'503 5.5.1 RCPT first.': 0.01,
#	'503 5.7.0 No identity changes permitted.': 0.01,
#	'504 5.7.4 Unrecognized Authentication Type.': 0.01,
#	'530 5.5.1 Authentication Required. Learn more here.': 0.01,
#	'530 5.7.0 Must issue a STARTTLS command first.': 0.01,
#	'535 5.5.4 Optional Argument not permitted for that AUTH mode.': 0.01,
#	'535 5.7.1 Application-specific password required. Learn more here.': 0.01,
#	'535 5.7.1 Please log in with your web browser and then try again. Learn more here.': 0.01,
#	'535 5.7.1 Username and Password not accepted. Learn more here.': 0.01,
	'550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, review this article.': 0.01,
	'550 5.2.1 The email account that you tried to reach is disabled.': 0.01,
	'550 5.2.1 The user you are trying to contact is receiving mail at a rate that prevents additional messages from being delivered. For more information, review this article.': 0.01,
	'550 5.4.5 Daily sending quota exceeded. Learn more here.': 0.01,
#	'550 5.4.5 Daily SMTP relay limit exceeded for user. For more information on SMTP relay sending limits please contact your administrator or review this article.': 0.01,
#	'550 5.7.0 Mail relay denied.': 0.01,
#	'550 5.7.0 Mail Sending denied. This error occurs if the sender account is disabled or not registered within your G Suite domain.': 0.01,
	'550 5.7.1 Email quota exceeded.': 0.01,
#	'550 5.7.1 Invalid credentials for relay.': 0.01,
	'550 5.7.1 Our system has detected an unusual rate of unsolicited mail originating from your IP address. To protect our users from spam, mail sent from your IP address has been blocked. Review our Bulk Senders Guidelines.': 0.01,
	'550 5.7.1 Our system has detected that this message is likely unsolicited mail. To reduce the amount of spam sent to Gmail, this message has been blocked. For more information, review this article.': 0.01,
	'550 5.7.1 The IP you\'re using to send mail is not authorized to send email directly to our servers. Please use the SMTP relay at your service provider instead. For more information, review this article.': 0.01,
	'550 5.7.1 The user or domain that you are sending to (or from) has a policy that prohibited the mail that you sent. Please contact your domain administrator for further details. For more information, review this article.': 0.01,
	'550 5.7.1 Unauthenticated email is not accepted from this domain.': 0.01,
	'550 5.7.1 Daily SMTP relay limit exceeded for customer. For more information on SMTP relay sending limits please contact your administrator or review this article.': 0.01,
	'552 5.2.2 The email account that you tried to reach is over quota.': 0.01,
	'552 5.2.3 Your message exceeded Google\'s message size limits. Please review our size guidelines.': 0.01,
	'553 5.1.2 We weren\'t able to find the recipient domain. Please check for any spelling errors, and make sure you didn\'t enter any spaces, periods, or other punctuation after the recipient\'s email address.': 0.01,
	'554 5.6.0 Mail message is malformed. Not accepted.': 0.01,
#	'554 5.6.0 Message exceeded 50 hops, this may indicate a mail loop.': 0.01,
#	'554 5.7.0 Too Many Unauthenticated commands.': 0.01,
	'555 5.5.2 Syntax error.': 0.01
}


















##############################################
#
# Shouldn't need to mess with stuff below here
#
##############################################

class EmlServer( SMTPServer ):
    no = 0

    #adding in the default for '250 Message accepted' or whatever success message 
    weights = 0
    for weight in list( returnmap.values() ):
        weights += weight

    remainder = 1 - weights
    returnmap[None] = remainder

    def process_message( self, peer, mailfrom, rcpttos, data ):
        if ( 1 == savefile ):
            filename = '%s-%d.eml' % ( datetime.now().strftime( '%Y%m%d%H%M%S' ), self.no )
        else:
            filename = '/dev/null'
        f = open( filename, 'w' )
        f.write( data )
        f.close
        print '%s saved (message %d).' % ( filename, self.no )
        self.no += 1
        return numpy.random.choice( returnmap.keys(), p = list( returnmap.values() ) )


def run():
    foo = EmlServer( ( bindip, bindport ), None )
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
