---
slug: how-to-send-email-with-python-the-hard-way
title: Success! How I Finally Got Password Reset Emails Working for My Blog
category: web-dev
description: Discover how I use SendGrid and Linode to get password reset emails for blogthedata.com, and the code changes I made for DKIM, DMARC, and SPF protection.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/email.png
legacyImage: post_metaimgs/email.png
imageAlt: Lots of letters (emails) streaming out of a computer
imageAttribution: ""
imageWidth: 1280
imageHeight: 716
published: "2022-05-08T22:43:50Z"
updated: "2026-09-07T14:25:05.474Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Discover how I use SendGrid and Linode to get password reset emails for blogthedata.com, and the code changes I made for DKIM, DMARC, and SPF protection.</p>
legacyId: 42
related:
  - Migrating-from-apache-to-Nginx-Gunicorn
  - how-to-get-a-perfect-mozilla-observatory-score
  - finding-reliable-information
---

After jumping through lots of hoops, I finally have password reset emails working for blogthedata.com! If you have an account, try resetting your email <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/password-reset/">here</a>. If you don't have an account and want one (so you can add comments to posts)...reach out to me via <a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/in/jsolly/">LinkedIn</a>.

Back in the early days of the blog, I used my personal Gmail account to send password reset emails to users who wanted to reset their passwords. You can learn more about this implementation in Corey Schafer's video on <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=-tyBEsHSv7w">Django Email and Password Reset</a>. The only issue with the video is that insecure app authentication is no longer supported by google...keep reading for more details!

One day my friend Dylan discovered he wasn't able to reset his password. Turns out that Gmail had tightened the reigns on their Gmail API. I used a username/password to authenticate which is 'less secure app access.' This worked for a year until they made a change that would turn this setting off if not in active use. I don't have very many users on blogthedata.com so inevitably, the setting would turn off. The final nail in the coffin was Google's decision to <a target="_blank" rel="noopener noreferrer" href="https://support.google.com/accounts/answer/6010255?hl=en">disable insecure app authentication May 30th, 2022</a>.

I decided that the best path forward would be to drop Gmail and go a different route. I signed up for an email delivery service called <a target="_blank" rel="noopener noreferrer" href="https://app.sendgrid.com">SendGrid</a>. SendGrid provides several useful features you can read about on their '<a target="_blank" rel="noopener noreferrer" href="https://sendgrid.com/email-delivery/">Why SendGrid</a>' page. It's free to get started. You only have to pay if you're sending thousands of emails a day.

First, I needed to convince SendGrid that I am the owner of blogthedata.com. Here's an email from SendGrid support regarding my application to use their services.

<blockquote><p>XXXXXXXX (SendGrid)<br>Apr 14, 2022, 8:57 PM PDT</p><p>Hello there,</p><p>Thank you for your patience. I can assure you that we are doing everything to make sure your account is activated.</p><p>Can you please respond to this thread with a business email that uses the domain blogthedata.com?</p><p>I look forward to your reply.</p><p>Best,<br>XXXXXXXX</p></blockquote>

I didn't realize that when you purchase a domain, you also own the right to send emails using the domain. Essentially, I can use any email address that ends with @blogthedata.com. It also turns out my primary email provider, ProtonMail, allows <a target="_blank" rel="noopener noreferrer" href="https://proton.me/support/custom-domain">connecting a custom domain</a> so I can forward SMTP emails to a target ProtonMail server.

In order to do that, I needed to add several records to my DNS provider, Linode. By the way, you can check the DNS provider of any website with the <a target="_blank" rel="noopener noreferrer" href="https://www.cyberciti.biz/faq/linux-unix-dig-command-examples-usage-syntax/?utm_source=Linux_Unix_Command&amp;utm_medium=faq&amp;utm_campaign=nixcmd">unix dig command</a>. Here's what I get when I run it against my domain.

<pre><code class="language-bash">🍁johnsolly:22-05-08:~ $ dig ns blogthedata.com

; &lt;&lt;&gt;&gt; DiG 9.10.6 &lt;&lt;&gt;&gt; ns blogthedata.com
;; global options: +cmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: QUERY, status: NOERROR, id: 2368
;; flags: qr rd ra; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;blogthedata.com.		IN	NS

;; ANSWER SECTION:
blogthedata.com.	86400	IN	NS	ns1.linode.com.
blogthedata.com.	86400	IN	NS	ns2.linode.com.
blogthedata.com.	86400	IN	NS	ns3.linode.com.
blogthedata.com.	86400	IN	NS	ns4.linode.com.
blogthedata.com.	86400	IN	NS	ns5.linode.com.

;; Query time: 130 msec
;; SERVER: 208.67.222.222#53(208.67.222.222)
;; WHEN: Sun May 08 17:52:49 PDT 2022
;; MSG SIZE  rcvd: 141</code></pre>

To get ProtonMail server working with my domain, I needed to add the following DNS records in Lincode. Most of these records are about authenticating with my purchased domain, blogthedata.com.

<p style="text-align:center;"><img class="image_resized" style="width:258px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220508222604-1.png" alt="Image of protonmail DNS certificates. MX, SPF, DKIM, and DMARC are green meaning 'ON'"></p>

<blockquote><p>DKIM, along with&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://www.cloudflare.com/learning/dns/dns-records/dns-spf-record/">Sender Policy Framework (SPF)</a>&nbsp;and&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://www.cloudflare.com/learning/dns/dns-records/dns-dmarc-record/">Domain-based Message Authentication Reporting and Conformance (DMARC)</a>, makes it much more difficult for attackers to impersonate domains in this way. Emails that do not pass DKIM and SPF get marked as "spam" or are not delivered by email servers. If example.com has DKIM, SPF, and DMARC set up for their domain, then Alice will probably never even see Chuck's malicious email because it will either go to her spam folder or be rejected by the email server altogether.</p><p><a target="_blank" rel="noopener noreferrer" href="https://www.cloudflare.com/learning/dns/dns-records/dns-dkim-record/">DKIM, DMARC, SPF</a>&nbsp;(cloudfare doc)</p></blockquote>

Once I added all those records, I replied to SendGrid support from my @blogthedata.com email and they replied that my account was activated.

<blockquote><p>XXXXXXXX (SendGrid)<br>Apr 16, 2022, 5:22 PM PDT</p><p>Hello John,</p><p>Thank you for your continued patience, I am glad to report that your Twilio SendGrid account has been activated.</p></blockquote>

The next roadblock came from my cloud provider, Linode. Linode <a target="_blank" rel="noopener noreferrer" href="https://www.linode.com/community/questions/19082/i-just-created-my-first-linode-and-i-cant-send-emails-why">&nbsp;blocks SMTP ports</a> by default to prevent spam. Okay, time to start another thread with a separate support rep! In order to get the ports unblocked, you just need to inform them:

1 - Which servers you intend to use for mailing

2 - Can you ensure mailing practices will be <a target="_blank" rel="noopener noreferrer" href="https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business">CAN-SPAM</a> compliant.

CAN-SPAM is a law passed by congress in 2003 (Thanks George W. Bush) to curb phone, email, and paper spam. It dictates what businesses can put in promotional emails along with other rules. Failure to comply with CAN-SPAM can screw you over, according to the FTC:

<blockquote><p>Each separate email in violation of the CAN-SPAM Act is subject to penalties of up to $46,517</p></blockquote>

The good news is that most of these requirements are not applicable if your email is of 'transactional nature' 

<blockquote><p>If the message contains only commercial content, its primary purpose is commercial and it must comply with the requirements of CAN-SPAM. If it contains only transactional or relationship content, its primary purpose is transactional or relationship. In that case, it may not contain false or misleading routing information, but is otherwise exempt from most provisions of the CAN-SPAM Act.</p><p>- <a target="_blank" rel="noopener noreferrer" href="https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business">FTC</a></p></blockquote>

Great! Armed with this information, I reached out to Linode support:

<blockquote><p>NEW Support Ticket XXXXXXXX has been opened by jsolly:</p><p>--------------------------------------------------<br>Hello!</p><p>Could port 587 be unblocked for my linode, https://cloud.linode.com/linodes/XXXXXXXX ?&nbsp;</p><p>I followed this blog post to configure my DNS settings so I can send password reset emails for my blog (https://blogthedata.com) via SendGrid.<br>https://www.linode.com/community/questions/19082/i-just-created-my-first-linode-and-i-cant-send-emails-why</p><p>Here are the answers to your questions:<br><strong>1- Which Linodes will be used for mailing?</strong><br>https://cloud.linode.com/linodes/XXXXXXXX</p><p><strong>2 - Can you confirm that your mailing practices are CAN-SPAM compliant?</strong><br>Yes. I am only going to use this server for password reset emails where users will only get emails if they explicitly request that their password be reset. This should fall under the category of 'transactional emails.' There will be NO advertizements or promotions. I just want users who signed up on my website to be able to reset their passwords.&nbsp;</p><p>Based on these statements, can we open port 587 on my Linode for password reset emails?</p><p>Best,<br>John</p></blockquote>

I got a reply a couple days later...

<blockquote><p>Support Ticket XXXXXXXX has been updated by XXXXXXXX:</p><p>Hi there,</p><p>Thanks so much for providing us that information. These restrictions have now been lifted for your account, and you can begin sending email as soon as you'd like.</p><p>We ask that you configure rDNS for any mailing Linodes you deploy. Our guides on configuring DNS and rDNS records within the Linode Manager are linked below:</p><p>https://www.linode.com/docs/platform/manager/dns-manager/#add-dns-records<br>https://www.linode.com/docs/networking/dns/configure-your-linode-for-reverse-dns/<br>Once your DNS configuration is complete, you can confirm that these records have been configured correctly by running the following commands:</p><p># for checking the A record<br>dig +short $Domain</p><p># for checking rDNS<br>dig -x $IPaddress +short</p><p>Thanks,</p><p>XXXXXXXX<br>Linode Support Team</p></blockquote>

I ran those commands and forward/reverse DNS seem to work as expected.

<pre><code class="language-bash">🍁johnsolly:22-05-08:~ $ dig +short blogthedata.com
69.164.205.120
🍁johnsolly:22-05-08:~ $ dig -x 69.164.205.120 +short
www.blogthedata.com.</code></pre>

The <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/bd104fd94b8012f5afca2fb4d8d235a449b350ba">final code change</a> was simply adjusting the EMAIL\_HOST variable to point to SendGrid instead of Gmail.

I just tried resetting my password at my <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/password-reset/">password reset route</a> and it works! Users can now reset their passwords. Woot!

From a code perspective, Django makes password reset emails pretty easy out of the box.
