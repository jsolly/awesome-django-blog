---
slug: how-to-get-a-perfect-mozilla-observatory-score
title: "How I Improved My Security Score With Mozilla Observatory: A Guide"
category: web-dev
description: Discover how to improve your rating using Mozilla Observatory's security assessment tool. See the steps I took to upgrade my score from a 'F' to an 'A+'.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/mozilla_observatory_results.png
legacyImage: post_metaimgs/mozilla_observatory_results.png
imageAlt: An A+ rating on Mozilla Observatory
imageAttribution: ""
imageWidth: 562
imageHeight: 372
published: "2022-05-03T14:30:38Z"
updated: "2026-09-07T18:01:33.453Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Discover how to improve your rating using Mozilla Observatory's security assessment tool. See the steps I took to upgrade my score from a 'F' to an 'A+'.</p>
legacyId: 36
related:
  - implement-continuous-integration-github-actions
  - Adding-views-likes-to-posts
  - how-to-implement-content-security-policy-django
---

A few weeks ago, I made a post about getting a <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/google-lighthouse-perfect-score/">perfect* score on Google Lighthouse</a>, a tool for assessing website performance, SEO and best practices. I've now set my sights on a security audit tool called <a target="_blank" rel="noopener noreferrer" href="https://observatory.mozilla.org">Mozilla Observatory</a>.

I started out with an 'F' failing rating, but after implementing everything below, I have a D-. The end goal is to have a more secure site and bragging rights with an A+ score!

At a high level, we want to make sure the following pieces are secure

1 - The Django app itself. 

2 - The web server and what it serves

3 - Certificates and DNS

## Securing Django at the app level

Starting with the Django application, the best place to find up-to-date information on security best practices is the official <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/">Django development checklist</a>. The easiest way to see what still needs to be done is to run

<pre><code class="language-bash">manage.py&nbsp;check&nbsp;--deploy</code></pre>

This will give you a printout of what you need to do before deploying your app into production. You'll want to make sure you’ve:

1 - Secured your SECRET\_KEY

2 - Specified ALLOWED\_HOSTS

3 - Ensured various security settings are on (secured cookies, CSRF tokens)

I secured my SECRET\_KEY by placing it into a configuration file at ~/etc/django\_config.

In order to access the values from this JSON file, I open it from within settings.py:

<pre><code class="language-python">import json
with open("/etc/django_config.json", encoding="utf-8") as config_file:
    config = json.load(config_file)

SECRET_KEY = config.get("SECRET_KEY")</code></pre>

This way, I can still commit all my project files to source control without exposing my SECRET\_KEY in plaintext. The only way someone could get access to my SECRET\_KEY is if they had file access on my server (more about stopping that later).

The next thing you'll want to do is work out your ALLOWED\_HOSTS. This setting specifies which IP addresses may host your application. I have different settings for this one on my local development server compared to production.

On prod, I've only enabled the IP address of the Linode machine hosts my app. This way, no one can try to host from a different machine. The app can ONLY run on the linode box and my registered domain.

<pre><code class="language-python">"ALLOWED_HOSTS": ["69.164.205.120", "www.blogthedata.com", "blogthedata.com"],</code></pre>

For my local dev machine, ALLOWED\_HOSTS includes localhost since I coding/test on my local machine. The ngrok.io address is for mobile testing.

<pre><code class="language-python">{"ALLOWED_HOSTS": [ "127.0.0.1", ".ngrok.io", "localhost"]}</code></pre>

I didn't want to have a separate settings.py file for both development and prod, so I added conditional logic that changes security settings depending on the value of DEBUG.

<pre><code class="language-python"># SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
CAPTCHA_TEST_MODE = False

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# HSTS SETTINGS
SECURE_HSTS_SECONDS = 31557600 # One year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

if config['DEBUG'] == 'True':
    DEBUG = True
    CAPTCHA_TEST_MODE = True

    # HTTPS SETTINGS
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

    # HSTS SETTINGS
    SECURE_HSTS_PRELOAD = False
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False</code></pre>

I'll now walk through all these settings as best I understand them.

<ul><li>DEBUG - One of the most important security settings. When set to True, users get complete access to tracebacks along with tons of information about the server configuration. When False, users won't get all that information and errors simply result in 404 and 500 pages with no additional information.</li><li>CAPTCHA_TEST_MODE - This is a setting that is part of <a target="_blank" rel="noopener noreferrer" href="https://django-simple-captcha.readthedocs.io/en/latest/usage.html#">django-captcha</a>. If set to TRUE, captcha verification is turned off. This is useful for unit tests because I just want to know that the capcha functionality is working, not that my test scripts are actually trying to solve the CPATCHA!</li><li>SESSION, CSRF, REDIRECT… These further enforce that pages serve cookies, and tokens over https.</li><li>HSTS OPTIONS - Similar to the previous settings, these make sure your app always runs in https, and there's no chance pages downgrade to http.</li></ul>

My biggest suggestion with any security settings is to start with everything locked down and then explicitly loosen constraints as you need them. This way, if you make a mistake, it's much more likely that your site is more locked down than you wanted instead of less secure than you needed.

## Securing the Web Server

My app is running on apache2, so the changes I suggest are specific to that web server. At a high level we will want to make sure

1 - Correct file permissions

2 - Lock down server access

3 - Serve content securely

4 - Correct http security headers

The first thing you'll want to do is make sure a firewall is enabled. In my case, I am using the ufw firewall.

<pre><code class="language-bash">sudo apt-get install ufw -y
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow http/tcp
sudo ufw enable # put all the previous rules into effect</code></pre>

I am enabling ssh and the default http/tcp port (port 80), but block all other incoming traffic.

The second thing I do is make sure that the only way someone can only access the web server through a public/private asymmetric key relationship. The next changes turn off password authentication as well as prevent root login.

<pre><code class="language-bash">sudo nano /etc/ssh/sshd_config # disable logging in as root user and password authentication
# Change PermitRootLogin to no
# Change PasswordAuthentication to no</code></pre>

Even if a hacker gets ahold of a username/password, they shouldn't be able to access the webserver unless they are accessing from my machine.

Next, you'll want to lock down the file permissions for the accounts. I will admit I don't think I've done this correctly, but there should be at least 3 users on your server, with varying permission levels.

 1 - A user used by apache that has read access to the needed files as well as write access to folders needed to write to (like log files). Users should follow the <a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/Principle_of_least_privilege">Principle of Least Privilege</a> and only have access to the minimum amount of permissions in order to do their job, but no more.

2 - A user to administer the machine. I associate this one with the public/private key used to SSH into the machine.

3 - A root user that cannot be used to SSH in, but is accessible if you need (but cannot SSH into the machine directly)

### Hide server version from http header

This is a pretty minor issue, but for added security, you can choose to not disclose your server version in the standard http header. To check your site, run this command in the terminal.

<code>$&nbsp;curl -I &nbsp;http://example.com</code>

If you haven't explicitly hid it, the server version will show up.

<pre><code class="language-bash">$ curl -I  https://blogthedata.com
HTTP/1.1 200 OK
Date: Tue, 03 May 2022 23:15:38 GMT
Server: Apache/2.4.53 (Ubuntu)
Content-Length: 13817
X-Frame-Options: DENY
Vary: Cookie,Accept-Encoding
Strict-Transport-Security: max-age=300; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Set-Cookie: csrftoken=BL1ILPOtPNUVAITVL00Wnne6ZVVhzE8sJvhu8cnVW9YWAaIB7jqLgeoo6Y3ELDO6; expires=Tue, 02 May 2023 23:15:38 GMT; Max-Age=31449600; Path=/; SameSite=Lax; Secure
Content-Type: text/html; charset=utf-8</code></pre>

In apache2, you can hide the server version by adding these properties to the configuration file. For me, it’s located here:

<code>/etc/apache2/apache2.conf</code>

<code>ServerTokens Prod</code>  
<code>ServerSignature Off</code>

Now after re-running the cURL command, the server version is no longer disclosed. It simply says 'Apache'

<code><strong>Server</strong>: Apache</code>

## Certificate and DNS settings

To enable https on your site, you will need to register your domain with a certificate authority. One of the easiest ways to do this is using <a target="_blank" rel="noopener noreferrer" href="https://certbot.eff.org">certbot</a>. With a handful of terminal commands, you'll be up and running with https and the certificate will be auto-renewed before expiring.

From here, various additional extensions and security options can be added. Here is the list of things I came across.

### DNSSEC

According to <a target="_blank" rel="noopener noreferrer" href="https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en">ICANN</a>, 

<blockquote><p>Domain Name System Security Extensions (DNSSEC) allow registrants to digitally sign information they put into the Domain Name System (DNS). This protects consumers by ensuring DNS data that has been corrupted, either accidentally or maliciously, doesn't reach them.</p></blockquote>

I discovered that my cloud hosting service, Linode, <a target="_blank" rel="noopener noreferrer" href="https://www.linode.com/community/questions/158/is-dnssec-going-to-be-supported">does not currently support DNSSEC</a>! Maybe I should switch providers! The original request made at least 4 years ago and it’s still not fixed!

### OCSP Stapling

The <a target="_blank" rel="noopener noreferrer" href="https://ssltools.godaddy.com/views/certChecker">Godaddy cert checker</a> says my site doesn't implement this. According to <a target="_blank" rel="noopener noreferrer" href="https://www.digicert.com/kb/enabling-ocsp-stapling.htm">digicert</a>, 

<blockquote><p>OCSP stapling can enhance the OCSP protocol by letting the webhosting site be more proactive in improving the client (browsing) experience. OCSP stapling allows the certificate presenter (i.e. web server) to query the OCSP responder directly and then cache the response. This securely cached response is then delivered with the TLS/SSL handshake via the&nbsp;<strong>Certificate Status Request</strong>&nbsp;extension response, ensuring that the browser gets the same response performance for the certificate status as it does for the website content.</p></blockquote>

See this <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/issues/42">open issue</a> for my implementation of OCSP.

### CAA Record

You can check the CAA record status of your site using <a target="_blank" rel="noopener noreferrer" href="https://geekflare.com/tools/website-audit">geekflare's website audit tool.</a> The CAA record further locks down your site by specifying the certificate authorities that may issue certificates for your domain. In my case, I added a record for letsencrypt.org since that is the CA I use for this site. Linode has an <a target="_blank" rel="noopener noreferrer" href="https://www.linode.com/docs/products/networking/dns-manager/guides/caa-record/">easy to follow article</a> on how to do this yourself!

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220503153928-1.png" alt="CAA record showing letsencrypt.org as the supported CA" width="800" height="93">

## False Alarms and things I can't change

Be careful with scanners and auditing tools. For example, <a target="_blank" rel="noopener noreferrer" href="https://www.immuniweb.com/websec/blogthedata.com/bBPGxHoS/"> immuniweb</a> said my app was missing the <code>Public-Key-Pins</code> security header, but after reading the <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expect-CT">mdn docs on this header</a>, I found it is no longer recommended!

immuniweb also stated that cookies on my site were missing the HttpOnly flag. After checking the <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-CSRF_COOKIE_HTTPONLY">Django documentation</a>, they say it's not an issue:

<blockquote><h3><code>CSRF_COOKIE_HTTPONLY</code><a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-cookie-httponly" title="Permalink to this headline">¶</a></h3><p>Default:&nbsp;<code>False</code></p><p>Whether to use&nbsp;<code>HttpOnly</code>&nbsp;flag on the CSRF cookie. When&nbsp;<code>True</code>, client-side JavaScript cannot access the CSRF cookie.</p><p>Designating the CSRF cookie as&nbsp;<code>HttpOnly</code>&nbsp;doesn’t offer any practical protection because CSRF is only to protect against cross-domain attacks. If an attacker can read the cookie via JavaScript, they’re already on the same domain as far as the browser knows, so they can do anything they like anyway. (XSS is a much bigger hole than CSRF.)</p><p>Although the setting offers little practical benefit, it’s sometimes required by security auditors.</p></blockquote>

I emailed ImmuniWeb to tell them about these depreciated properties. I hope they incorporate my feedback to improve the tool!

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/immuniweb_message.png" alt="Screenshot of Immuniweb email. They said &quot;Dear John Solly, Thank you for your message! We've transfered this information to the Development Team.&quot;" width="458" height="228">

Although some tools are outdated, they gave me useful info. For example, ImmuiWeb found was I am using an older version of jQuery. This threw me because my <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/migrating-bs4-to-bs5/">migration from bootstrap 4 to bootstrap 5</a> should have removed jQuery. Turns out that it's my embedded Mailchimp form that is still relying on jQuery. The <a target="_blank" rel="noopener noreferrer" href="https://mailchimp.com/help/troubleshooting-the-embedded-signup-form/">Mailchimp docs</a> state:

<blockquote><p>The embed form code uses&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/JQuery">jQuery</a>&nbsp;to validate the form and display responses such as the success message that appears when someone clicks the Subscribe button to sign up for your emails.</p></blockquote>

### HTTP Security Headers

I also ran a Geekflare tool called '<a target="_blank" rel="noopener noreferrer" href="https://geekflare.com/tools/secure-headers-test">Secure Headers Test</a>' which looks at what the site serves to clients in http response headers.

The following OWASP recommended headers are checked.

<ul><li>HTTP Strict Transport Security</li><li>X-Frame-Options</li><li>X-Content-Type-Options</li><li>Content-Security-Policy</li><li>X-Permitted-Cross-Domain-Policies</li><li>Referrer-Policy</li><li>Clear-Site-Data</li><li>Cross-Origin-Embedder-Policy</li><li>Cross-Origin-Opener-Policy</li><li>Cross-Origin-Resource-Policy</li><li>Cache-Control</li></ul>

Unfortunately, I couldn't fix any of the missing headers. Here are the results for blogthedata.com

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220503174158-1.png" alt="Missing http security headers, Content-Security-Policy, X-Permitted-Cross-Domain-Policies, Clear-Site-Data, Cross-Origin-Embedder-Policy, Cross-Origin-Opener-Policy, Cross-Origin-Resource-Policy-Cache-control" width="800" height="538">I am missing (6) of the suggested headers. 

Cross-Origin-Resource-Policy (CORP), Cross-Origin-Embedder-Policy - Both appear to be <a target="_blank" rel="noopener noreferrer" href="https://code.djangoproject.com/ticket/31923">open issues in Django 4.0</a> that have not been merged in. There might be a workaround to force the headers through apache, but I would rather wait for the PRs to merge for it to be natively supported in Django.

X-Permitted-Cross-Domain-Policies - I don't see this being actively worked on by the official Django team, but I came across this <a target="_blank" rel="noopener noreferrer" href="https://github.com/github/secure_headers">git repo</a> that adds the ability to add this policy in Django 4.0. There’s a way to <a target="_blank" rel="noopener noreferrer" href="https://geekflare.com/cybersecurity/http-header-implementation/"> implement this through apache</a>, but again, I think I will wait to see how this all plays out in 4.0

Cross-Origin-Opener-Policy - They implemented this in Django 4.0. There’s an outstanding issue open to upgrade Django, but there is at least one dependency that prevents me from upgrading.

Cache-control - See this open issue.

Clear-site-date - Django has an <a target="_blank" rel="noopener noreferrer" href="https://code.djangoproject.com/ticket/31425"> open issue</a> for this one.

## Outstanding items to fix

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220504070637-1.png" alt="Image of Mozilla Observatory results. There are two arrows pointing to (2) missing implementations. Content Security Policy and Subresource Integrity." width="800" height="564">

I am now missing two items within the Mozilla Observatory audit. I've captured both requirements in separate GitHub issues.

### Subresource Integrity (SRI)

My understanding is that it's related to adding content on assets like CSS and JS to prevent the files from being changed. It sounds similar to what I will need to do to implement cache-control, so I added this as a consideration in that issue.

### Content Security Policy (CSP) 

By default, Django does not come with a content security policy, but the good folks at the Mozilla Foundation developed a plugin called <a target="_blank" rel="noopener noreferrer" href="https://django-csp.readthedocs.io/en/latest/installation.html">django-csp</a> that adds this functionality. This is a big lift, so I captured the requirement in this issue.
