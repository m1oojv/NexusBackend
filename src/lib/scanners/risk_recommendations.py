risk_recommendations = {"creds": {"area": "Leaked Credentials",
                                  "details": {True: {"finding": "",
                                                     "rec": ("<p>Leaked and stolen credentials pose as a huge security "
                                                             "risk to your organisations. Malicious actors can use it "
                                                             "to launch malicious cyberattacks "
                                                             "on your organisations.<br/>"
                                                             "How to remediate leaked credentials?"
                                                             "<ol>"
                                                             "<li>Establish a corporate-wide policy in handling "
                                                             "security credentials.</li>"
                                                             "<li>Implement an enterprise password management solution "
                                                             "strong password creation and diversity.</li>"
                                                             "<li>Implement multi-factor authentication for your users "
                                                             "by using a Microsoft Authenticator and/or security "
                                                             "key.</li>"
                                                             "<li>Consider adopting a zero-trust framework for your "
                                                             "network and systems.</li>"
                                                             "<li>Conduct regular security awareness training to "
                                                             "encourage staff and customers to improve their cyber "
                                                             "hygiene and behaviour.</li>"
                                                             "</ol>"
                                                             "</p>"),
                                                     "report_rec": ('•  Change credentials of impacted users '
                                                                    'immediately.<br/> '
                                                                    '•  Monitor affected corporate accounts for any '
                                                                    'suspicious or malicious activities.<br/> '
                                                                    '•  Establish a corporate-wide policy in handling '
                                                                    'security credentials.<br/> '
                                                                    'Implement an enterprise password management '
                                                                    'solution strong password creation and '
                                                                    'diversity.<br/> '
                                                                    'Implement multi-factor authentication for your '
                                                                    'users by using a Microsoft Authenticator and/or '
                                                                    'security '
                                                                    'key. Multi-factor authentication (MFA or 2FA) '
                                                                    'prevents the majority of credential-based '
                                                                    'attacks.<br/> '
                                                                    '•  Conduct regular security awareness training '
                                                                    'to encourage staff and customers to improve '
                                                                    'their cyber '
                                                                    'hygiene and behaviour.'
                                                                    )
                                                     },
                                              False: {"finding": "",
                                                      "rec": ""}
                                              },
                                  "impact": ("<p>Leaked credentials on the Dark Web are likely made publicly available "
                                             "due to human error and malicious attacks (e.g. phishing). The "
                                             "credentials may be purchased by attackers for further access to data "
                                             "stored in these accounts.</p>"
                                             )
                                  },
                        "vulns": {"area": "Assets Vulnerabilities",
                                  "details": {True: {"finding": "",
                                                     "rec": ("<p>Inevitably, every physical or digital assets will "
                                                             "have vulnerabilities. When a vulnerability is "
                                                             "discovered, it is important that you speak to your "
                                                             "third-party vendor or supplier and follow their "
                                                             "recommendation to patch and secure your assets "
                                                             "correctly.<br/><br/>"
                                                             "It is recommended that you acquire your assets from "
                                                             "reputable and established third-party vendors and avoid "
                                                             "buying them from unsecured supply chains that may "
                                                             "compromise the product.<br/><br/>"
                                                             "You can also conduct penetration testing to pro-actively "
                                                             "seek out unknown vulnerabilities so that you can patch "
                                                             "and remediate them in time.</p>"),
                                                     "report_rec": ('•  Identify the vulnerability through <a href="https://nvd.nist.gov/vuln/search" '
                                                                    'color="#0000EE" underline="true">https://nvd.nist.gov/vuln/search</a>.<br/> '
                                                                    '•  Identify the relevant recommendations and patches under the ‘References to Advisories, '
                                                                    'Solutions, and Tools’ section.<br/> '
                                                                    '•  Contact the system administrator or owner of the impacted asset to apply the patch.<br/>'
                                                                    '•  In some cases, assets cannot be patched due to support expiry from software provider, breach of warranty from '
                                                                    'system provider or patches have not been released. In these situations, assets must be reviewed on a case by case '
                                                                    'basis to assess whether compensating controls can be applied to mitigate the risk of open vulnerabilities.<br/>'
                                                                    '•  Conduct regular vulnerability scans to identify new vulnerabilities on assets.')},
                                              False: {"finding": "",
                                                      "rec": "",
                                                      "report_rec": ""
                                                      }
                                              },
                                  "impact": ("<p>Open vulnerabilities on your public-facing digital assets could "
                                             "result in hackers exploiting them to gain access to your organization’s "
                                             "network or data.</p>"
                                             )
                                  },
                        "ports": {"area": "Services",
                                  "details": {9200: {"finding": "High-risk services (Port 9200)",
                                                     "rec": ("<u>9200</u><br/>"
                                                             "<p>Port 9200 is the default port for Elasticsearch and "
                                                             "is very attractive to malicious actors as it is a "
                                                             "database service. Multiple other services have been used "
                                                             "in conjunction with this port, such as Kibana, which has "
                                                             "led to many more vulnerabilities in recent years.<br/><br/>"
                                                             "By default, port 9200 is open, and you can restrict "
                                                             "client access to this port by using a firewall. "
                                                             "Otherwise, this port should be closed immediately.</p>"),
                                                     "report_rec": ('Port 9200 is the default port for Elasticsearch '
                                                                    'and is very attractive to malicious actors as it '
                                                                    'is a database service. '
                                                                    'Multiple other services have been used in '
                                                                    'conjunction with this port, such as Kibana, '
                                                                    'which has led to many more vulnerabilities '
                                                                    'in recent years.<br/><br/>'
                                                                    'By default, port 9200 is open, and you can '
                                                                    'restrict client access to this port by using a '
                                                                    'firewall. Otherwise, this port should '
                                                                    'be closed immediately.'
                                                                    )
                                                     },
                                              445: {"finding": "High-risk services (Port 445)",
                                                    "rec": ("<u>445</u><br/>"
                                                            "<p>Port 445 is used by Microsoft for the Server Message "
                                                            "Block (SMB) as a communication protocol. This service is "
                                                            "known for its security vulnerabilities and has been "
                                                            "linked to ransomware attacks such as WannaCry.<br/><br/>"
                                                            "We recommend closing this port immediately and using a "
                                                            "more secure and modern communication protocol.</p>"),
                                                    "report_rec": ('Port 445 is used by Microsoft for the Server Message Block (SMB) as a communication protocol. This service is known for its '
                                                                   'security vulnerabilities and has been linked to ransomware attacks such as WannaCry.<br/><br/>'
                                                                   'We recommend closing this port immediately and using a more secure and modern communication protocol.'
                                                                   )
                                                    },
                                              8080: {"finding": "Medium-risk services (Port 8080)",
                                                     "rec": ("<u>8080</u><br/>"
                                                             "<p>Developers commonly use port 8080 for testing and "
                                                             "prototyping. It is often opened for a short amount of "
                                                             "time and can be left open by mistake.<br/><br/>"
                                                             "Though Port 8080 can also be used for unsecured web "
                                                             "traffic, you should use Port 80 instead.<br/><br/>"
                                                             "Unsecured web traffic and the associated ports are "
                                                             "susceptible to cross-site scripting and forgeries, "
                                                             "buffer-overflow attacks and SQL injection "
                                                             "attacks.<br/><br/>"
                                                             "Close the open port immediately.</p>"),
                                                     "report_rec": ('Developers commonly use port 8080 for testing and prototyping. It is often opened for a short '
                                                                    'amount of time and can be left open by mistake.<br/><br/>'
                                                                    'Though Port 8080 can also be used for unsecured web traffic, you should use Port 80 instead.<br/><br/>'
                                                                    'Unsecured web traffic and the associated ports are susceptible to cross-site scripting and forgeries, '
                                                                    'buffer-overflow attacks and SQL injection attacks.<br/><br/>'
                                                                    'Close the open port immediately.'
                                                                    )
                                                     },
                                              8081: {"finding": "Medium-risk services (Port 8081)",
                                                     "rec": ("<u>8081</u><br/>"
                                                             "<p>Developers commonly uses port 8081 for testing and "
                                                             "prototyping. It is often opened for a short amount of "
                                                             "time and can be left open by mistake.<br/><br/>"
                                                             "Though Port 8081 can also be used for unsecured web "
                                                             "traffic, you should use Port 80 instead.<br/><br/>"
                                                             "Unsecured web traffic and the associated ports are "
                                                             "susceptible to cross-site scripting and forgeries, "
                                                             "buffer-overflow attacks and SQL injection "
                                                             "attacks.<br/><br/>"
                                                             "Close the open port immediately.</p>"),
                                                     "report_rec": (
                                                         'Developers commonly use port 8081 for testing and prototyping. It is often opened for a short '
                                                         'amount of time and can be left open by mistake.<br/><br/>'
                                                         'Though Port 8081 can also be used for unsecured web traffic, you should use Port 80 instead.<br/><br/>'
                                                         'Unsecured web traffic and the associated ports are susceptible to cross-site scripting and forgeries, '
                                                         'buffer-overflow attacks and SQL injection attacks.<br/><br/>'
                                                         'Close the open port immediately.'
                                                         )
                                                     },
                                              3389: {"finding": "Medium-risk services (Port 3389)",
                                                     "rec": ("<u>3389</u><br/>"
                                                             "<p>Microsoft uses port 3389 for its Remote Desktop "
                                                             "Protocol (RDP), enabling remote connections to other "
                                                             "computers.<br/><br/>"
                                                             "Malicious actors often exploit misconfigured RDP ports "
                                                             "to gain network access and to potentially move "
                                                             "laterally throughout a network, escalate privileges, "
                                                             "access and exfiltrate sensitive information, harvest "
                                                             "credentials, or deploy a wide variety of malware.<br/><br/>"
                                                             "Close the open port immediately if not in use.</p>"
                                                             ),
                                                     "report_rec": ('Microsoft uses port 3389 for its Remote Desktop '
                                                                    'Protocol (RDP), enabling remote connections '
                                                                    'to other computers.<br/><br/>'
                                                                    'Malicious actors often exploit misconfigured RDP '
                                                                    'ports to gain network access and to potentially '
                                                                    'move laterally '
                                                                    'throughout a network, escalate privileges, '
                                                                    'access and exfiltrate sensitive information, '
                                                                    'harvest credentials, or '
                                                                    'deploy a wide variety of malware.<br/><br/>'
                                                                    'Close the open port immediately if not in use.'
                                                                    )
                                                     },
                                              8888: {"finding": "Medium-risk services (Port 8888)",
                                                     "rec": ("<u>8888</u><br/>"
                                                             "<p>Developers commonly use port 8888 for testing and "
                                                             "prototyping. It is often opened for a short amount of "
                                                             "time and can be left open by mistake.<br/><br/>"
                                                             "Though Port 8888 can also be used for unsecured web "
                                                             "traffic, you should use Port 80 instead.<br/><br/>"
                                                             "Unsecured web traffic and the associated ports are "
                                                             "susceptible to cross-site scripting and forgeries, "
                                                             "buffer-overflow attacks and SQL injection "
                                                             "attacks.<br/><br/>"
                                                             "Close the open port immediately.</p>"),
                                                     "report_rec": (
                                                         'Developers commonly use port 8888 for testing and prototyping. It is often opened for a short '
                                                         'amount of time and can be left open by mistake.<br/><br/>'
                                                         'Though Port 8888 can also be used for unsecured web traffic, you should use Port 80 instead.<br/><br/>'
                                                         'Unsecured web traffic and the associated ports are susceptible to cross-site scripting and forgeries, '
                                                         'buffer-overflow attacks and SQL injection attacks.<br/><br/>'
                                                         'Close the open port immediately.'
                                                     ),
                                                     },
                                              5432: {"finding": "Medium-risk services (Port 5432)",
                                                     "rec": ("<u>5432</u><br/>"
                                                             "<p>The PostgreSQL database uses port 5432 for Adaptive "
                                                             "Authentication (TCP). It should not be open to the "
                                                             "internet. Because it is related to the database, it is a "
                                                             "common port exploited by malicious actors and should be "
                                                             "closed immediately.</p>"),
                                                     "report_rec": ('The PostgreSQL database uses port 5432 for '
                                                                    'Adaptive Authentication (TCP). It should not '
                                                                    'be open to the internet. Because it is related '
                                                                    'to the database, it is a common port exploited '
                                                                    'by malicious actors and should be closed '
                                                                    'immediately.'
                                                                    ),
                                                     },
                                              },
                                  "impact": ("<p>Exposed services could result in them being exploited by hackers to "
                                             "gain access to your organization’s network or data.</p>"
                                             )
                                  },
                        "ssl_expiry": {"area": "Certificates",
                                       "details": {True: {"finding": "SSL/TLS Expiry",
                                                          "rec": ("<p>An expired SSL certificate can pose severe cyber "
                                                                  "and business risks to your organization. Most "
                                                                  "browsers will flag your website and warn your users "
                                                                  "about the risk of accessing your website. This will "
                                                                  "reduce your website traffic and damage your "
                                                                  "reputation, customer trust, and business "
                                                                  "revenue.<br/><br/>"
                                                                  "Malicious actors are also known to search out "
                                                                  "expired SSL certificate websites to launch phishing "
                                                                  "and man-in-the-middle attacks.<br/><br/>"
                                                                  "Renewing your SSL certificate is a relatively easy "
                                                                  "process; we recommend you renew your SSL "
                                                                  "certificate immediately.</p>"),
                                                          "report_rec": ('Renew your SSL certificate immediately. An expired SSL certificate can pose severe cyber '
                                                                         'and business risks to your organization. Most browsers will flag your website and warn your users about '
                                                                         'the risk of accessing your website. This will reduce your website traffic and damage your reputation, '
                                                                         'customer trust, and business revenue.<br/><br/>'
                                                                         'Malicious actors are also known to search out expired SSL certificate websites to launch phishing and '
                                                                         'man-in-the-middle attacks.'
                                                                         ),
                                                          },
                                                   False: {"finding": "",
                                                           "rec": ""},
                                                   },
                                       "impact": ("<p>Expired certificates makes your website insecure, scares customers "
                                                  "away and prevent secure transactions.</p>"),
                                       },
                        "marketplace": {"area": "Marketplace Mentions",
                                        "details": {True: {"finding": "Ransom Leak",
                                                           "rec": ("<p>Ransom Leaks happen after your organisation "
                                                                   "suffered a ransomware attack and your "
                                                                   "organisation&apos;s data has been put up for sale "
                                                                   "on the dark web.<br/><br/>"
                                                                   "Security vulnerabilities happen when your devices, "
                                                                   "software, and applications are outdated. In "
                                                                   "addition, the lack of proper backup and "
                                                                   "cybersecurity plan often increases the risk and "
                                                                   "probability of a ransomware attack.<br/><br/>"
                                                                   "<b>What to do in the case of a ransom leak?</b>"
                                                                   "<ol>"
                                                                   "<li>Get confirmation of the breach and what type "
                                                                   "of information/data was stolen.</li>"
                                                                   "<li>Understand what, where, why and how the breach "
                                                                   "happens and take steps to remediate your "
                                                                   "system&apos;s vulnerabilities.</li>"
                                                                   "<li>Seek legal advice and comply with your "
                                                                   "regulatory requirements such as PDPA/GDPR, PCI "
                                                                   "DSS, HIPAA etc.</li>"
                                                                   "<li>Communicate clearly with your customers about "
                                                                   "the types of data stolen and its implication. "
                                                                   "Provide help to assist them in rectifying and "
                                                                   "remediating the breach if necessary.</li>"
                                                                   "<li>Work on your Lessons Learn report and improve "
                                                                   "your current cybersecurity posture to minimise the "
                                                                   "risk of having similar incidents from happening "
                                                                   "again. We recommend following the NIST "
                                                                   "Cybersecurity Framework and/or ISO/IEC 27001 to "
                                                                   "secure your environments.</li>"
                                                                   "</ol>"
                                                                   "</p>"
                                                                   ),
                                                           "report_rec": ('Marketplace mentions could indicate nerferious cyber activities happening in your company’s '
                                                                          'environment and could be an early warning of a cyber breach.<br/><br/> '
                                                                          'We recommend the following actions to ascertain this:<br/> '
                                                                          '•  Conduct anti-malware scans on all hosts in your environment to detect malicious software.<br/> '
                                                                          '•  Review public facing firewall logs for suspicious activities, domains or IP addresses.<br/> '
                                                                          '•  Review access logs for privileged accounts or accounts that can access sensitive data.<br/> '
                                                                          '•  Contact a professional cyber incident response provider if any malicious activities are found.'
                                                                          )
                                                           },
                                                    False: {"finding": "Ransom Leak",
                                                            "rec": ""},
                                                    },
                                        "impact": ("<p>Marketplace mentions could signify an interest by hackers to "
                                                   "target your organization. Typically, these are early signs of a "
                                                   "compromise and your organization will need to remediate the other "
                                                   "findings in the report in order to close any gaps that hackers can "
                                                   "use against you.</p>"
                                                   )
                                        },
                        "email_security": {"area": "Email Security",
                                           "details": {"spf": {"finding": "No SPF Record",
                                                               "rec": ("<p>A Sender Policy Framework (SPF) record is "
                                                                       "an email authentication standard that helps to "
                                                                       "protect senders and recipients from spam, "
                                                                       "spoofing, and phishing. By adding an SPF "
                                                                       "record to your Domain Name System (DNS), you "
                                                                       "will specify which IP addresses are authorised "
                                                                       "to send an email on behalf of a particular "
                                                                       "domain. An SPF-protected domain is less "
                                                                       "attractive to malicious actors and is less "
                                                                       "likely to be blacklisted by spam filters. SPF "
                                                                       "records also ensure that legitimate email from "
                                                                       "the domain is delivered.<br/><br/>The easiest "
                                                                       "way to generate an SPF record is to use an SPF "
                                                                       "generator. You can find them on google.<br/><br/>"
                                                                       "Be sure to include the SPF record to all your "
                                                                       "sending and non-sending domains, as it is "
                                                                       "common for malicious actors to try to spoof "
                                                                       "your non-sending domains too.<br/><br/>"
                                                                       "After your SPF records have been generated, "
                                                                       "add them to your respective domain&apos;s DNS "
                                                                       "record via a TXT entry.<br/><br/>"
                                                                       "Once completed, check your entries using an "
                                                                       "SPF Checker.</p>"),
                                                               "report_rec": (
                                                                   "•  Use a SPF generator to generate a record.<br/>"
                                                                   "•  Include SPF records to all your sending and non-sending domains to prevent email spoofing.<br/>"
                                                                   "•  Add SPF records to your domain’s DNS record via a TXT entry.<br/>"
                                                                   "•  Verify your entries using an SPF Checker.<br/>")
                                                               },
                                                       "dmarc": {"finding": "No DMARC Record",
                                                                 "rec": ("<p>Domain-based Message Authentication "
                                                                         "Reporting and Conformance (DMARC) is used to "
                                                                         "authenticate an email by aligning SPF and "
                                                                         "DKIM records. It helps protect against email "
                                                                         "compromises such as phishing and "
                                                                         "spoofing.<br/><br/>"
                                                                         "With DMARC, you will be able to inform the "
                                                                         "internet on how to handle the unauthorised "
                                                                         "use of your email domains by instituting "
                                                                         "a policy in your DMARC record.<br/><br/>"
                                                                         "There are three types of DMARC policies:"
                                                                         "<ol>"
                                                                         "<li><b>p=none</b><br/>Monitors your email "
                                                                         "traffic. No further actions are taken.</li>"
                                                                         "<li><b>p=quarantine</b><br/>Sends "
                                                                         "unauthorised emails to the spam folder.</li>"
                                                                         "<li><b>p=reject</b><br/>This ensures that "
                                                                         "unauthorised email does not get delivered at "
                                                                         "all.</li>"
                                                                         "</ol>"
                                                                         "To publish a DMARC record:"
                                                                         "<ol>"
                                                                         "<li>Log in to your DNS management "
                                                                         "console.</li>"
                                                                         "<li>Under Hostname, enter <i>_dmarc</i>.</li>"
                                                                         "<li>Under Resource Type, select TXT</li>"
                                                                         "<li>Under Value, create your DMARC policy in "
                                                                         "the following format.<br/><b>V=DMARC1;</b> "
                                                                         "<i>[policy type such as p=none]</i><b>; "
                                                                         "rua=mailto: &quot;email@yourdomain.com&quot;"
                                                                         "</b><br/>"
                                                                         "Note that the &quot;rua&quot; tag is the "
                                                                         "email address to send DMARC aggregate "
                                                                         "reports.</li>"
                                                                         "</ol>"
                                                                         "Once completed, check your entry using a "
                                                                         "DMARC checker.</p>"),
                                                                 "report_rec": ("Institute DMARC policies<br/>"
                                                                                "•  To monitor your email traffic: "
                                                                                "p=none<br/> "
                                                                                "•  To send unauthorised emails to "
                                                                                "the spam folder: p=quarantine<br/> "
                                                                                "•  To ensure that unauthorised "
                                                                                "emails are not delivered at all: "
                                                                                "p=reject<br/> "
                                                                                "Publish DMARC records<br/>"
                                                                                "•  Log in to DNS management "
                                                                                "console<br/> "
                                                                                "•  Under Hostname, enter _dmarc<br/>"
                                                                                "•  Under Resource Type, select TXT "
                                                                                "Value<br/> "
                                                                                "•  Create your DMARC policy in the "
                                                                                "following format: V=DMARC1; [policy "
                                                                                "type such as p=none]; rua=mailto: "
                                                                                "email@yourdomain.com<br/> "
                                                                                "•  Once completed, check your entry "
                                                                                "using a DMARC checker "
                                                                                ),
                                                                 },
                                                       },
                                           "impact": ("<p>Your domain may be spoofed by attackers to send malicious "
                                                      "emails on your behalf. Your corporate emails may also be "
                                                      "susceptible to spam and phishing attacks. Outgoing emails from "
                                                      "your organization may also be marked as spam or rejected.</p>"
                                                      ),
                                           },
                        "security_headers": {"area": "Secure Headers",
                                             "details": {"xframe": {"finding": "No X-Frame",
                                                                    "rec": ("<p>The X-Frame-Options HTTP "
                                                                            "response header helps to indicate "
                                                                            "if a browser should be allowed to "
                                                                            "render a page in a &lt;frame&gt;, "
                                                                            "&lt;iframe&gt;, "
                                                                            "&lt;embed&gt; or &lt;object&gt;. This can "
                                                                            "be used to prevent clickjacking attacks "
                                                                            "and prevent your content from being "
                                                                            "embedded into other websites.<br/><br/>"
                                                                            "The X-Frame-Options header provides three "
                                                                            "values:"
                                                                            "<ol>"
                                                                            "<li><b>DENY</b>, which prevents any "
                                                                            "domain from framing the content. The "
                                                                            "&quot;DENY&quot; setting is recommended "
                                                                            "unless a specific need has been "
                                                                            "identified.</li>"
                                                                            "<li><b>SAMEORIGIN</b>, which only allows "
                                                                            "the current site to frame the content."
                                                                            "</li>"
                                                                            "<li><b>ALLOW-FROM</b> uri permits the "
                                                                            "specified &apos;uri&apos; to frame this "
                                                                            "page. (e.g., ALLOW-FROM "
                                                                            "https://www.example.com)</li>"
                                                                            "</ol>"
                                                                            "Do check the limitations of your browser "
                                                                            "if X-Frame-Options is supported, as some "
                                                                            "support the new Content-Security-Policy "
                                                                            "(CSP) frame-ancestors directive instead."
                                                                            "</p>"),
                                                                    "report_rec": (
                                                                        "<p>The X-Frame-Options HTTP response "
                                                                        "header helps to prevent clickjacking attacks "
                                                                        "and prevent your content from being "
                                                                        "embedded into other websites.<br/><br/>"
                                                                        "You can choose to use the following X-Frame-Options header values:<br/>"
                                                                        "1.  <b>DENY</b>, which prevents any "
                                                                        "domain from framing the content. The "
                                                                        "&quot;DENY&quot; setting is recommended "
                                                                        "unless a specific need has been "
                                                                        "identified.<br/>"
                                                                        "2.  <b>SAMEORIGIN</b>, which only allows "
                                                                        "the current site to frame the content.<br/>"
                                                                        "3.  <b>ALLOW-FROM</b> uri permits the "
                                                                        "specified &apos;uri&apos; to frame this "
                                                                        "page. (e.g., ALLOW-FROM "
                                                                        "https://www.example.com)<br/><br/>"
                                                                        "Contact your web hosting provider or web development team to implement the changes."
                                                                        "</p>")},
                                                         "hsts": {"finding": "No HSTS",
                                                                  "rec": ("<p>HTTP Strict Transport Security (HSTS) "
                                                                          "response header informs browsers that the "
                                                                          "site should only be accessed using HTTPS. "
                                                                          "Any future attempts to access it using HTTP "
                                                                          "should automatically be converted to "
                                                                          "HTTPS.<br/><br/>"
                                                                          "Once a supported browser receives this "
                                                                          "header, it will prevent any communication "
                                                                          "from being sent over HTTP to the specified "
                                                                          "domain and will send all communications "
                                                                          "over HTTPS. This is a more secure method "
                                                                          "than simply configuring an HTTP or HTTPS "
                                                                          "(301) redirect on your server, where the "
                                                                          "initial HTTP connection is still vulnerable "
                                                                          "to a man-in-the-middle attack. It also "
                                                                          "prevents HTTPS click through prompts on "
                                                                          "browsers.<br/><br/>"
                                                                          "<u>There are three main methods to "
                                                                          "implement HSTS:</u>"
                                                                          "<ol>"
                                                                          "<li><b>Strict-Transport-Security: max-age="
                                                                          "</b><i>&lt;expire-time&gt;</i></li>"
                                                                          "<li><b>Strict-Transport-Security: max-age="
                                                                          "</b><i>&lt;expire-time&gt;; "
                                                                          "includeSubDomains</i></li>"
                                                                          "<li><b>Strict-Transport-Security: max-age="
                                                                          "</b><i>&lt;expire-time&gt;; preload</i></li>"
                                                                          "</ol>"
                                                                          "To start, we recommend that you use "
                                                                          "<b>Strict-Transport-Security: max-age=</b>"
                                                                          "<i>&lt;expire-time&gt;</i><br/><br/>"
                                                                          "<u>Example</u><br/>"
                                                                          "<b>Strict-Transport-Security: max-age="
                                                                          "31536000</b><br/><br/>"
                                                                          "<b><u>Directives</u></b><br/>"
                                                                          "<b>Max-age=</b><i>&lt;expire-time&gt;"
                                                                          "</i><br/>"
                                                                          "The time, in seconds, that the browser "
                                                                          "should remember to access a site using "
                                                                          "HTTPS.<br/><br/>"
                                                                          "<b>IncludeSubDomains</b> (optional)<br/>"
                                                                          "If this optional parameter is specified, "
                                                                          "this rule applies to all the site&apos;s "
                                                                          "subdomains.<br/><br/>"
                                                                          "<b>Preload</b> (optional)<br/>The site owner "
                                                                          "can submit the domain to the HSTS preload "
                                                                          "list for their domain to be preloaded. "
                                                                          "However, this can have PERMANENT "
                                                                          "CONSEQUENCES and prevent users from "
                                                                          "accessing your site and its subdomains.<br/>"
                                                                          "To read more about HSTS and how it works "
                                                                          "please visit <a href='"
                                                                          "https://developer.mozilla.org/en-US/docs/"
                                                                          "Web/HTTP/Headers/Strict-Transport-"
                                                                          "Security'>Mdn Web Docs</a> by Mozilla for "
                                                                          "more information.</p>"),
                                                                  "report_rec": (
                                                                      "<p>HTTP Strict Transport Security (HSTS) "
                                                                      "response header informs browsers that the "
                                                                      "site should only be accessed using HTTPS. "
                                                                      "Any future attempts to access it using HTTP "
                                                                      "should automatically be converted to "
                                                                      "HTTPS.<br/><br/>"
                                                                      "Once a supported browser receives this "
                                                                      "header, it will prevent any communication.<br/><br/>"
                                                                      "We recommend implementing the following header in your website:<br/><br/>"
                                                                      "<b>Strict-Transport-Security: max-age=31536000</b><br/><br/>"
                                                                      "Contact your web hosting provider or web development team to implement the changes.</p>")},
                                                         "nosniff": {"finding": "No X-Content-Type-Options",
                                                                     "rec": ("<p>The X-Content-Type-Options (also "
                                                                             "known as &quot;nosniff&quot;) header "
                                                                             "protects against MIMI sniffing "
                                                                             "vulnerabilities. These vulnerabilities "
                                                                             "can occur when a website allows users to "
                                                                             "upload content; however, the user "
                                                                             "disguises a particular file type as "
                                                                             "something else, allowing them to perform "
                                                                             "cross-site scripting and compromise the "
                                                                             "website.<br/><br/>"
                                                                             "To enable this security header on your "
                                                                             "origin server:<br/><br/>"
                                                                             "<u>For Nginx:</u><br/>"
                                                                             "add_header X-Content-Type-Options &quot;"
                                                                             "nosniff&quot;<br/><br/>"
                                                                             "<u>For Apache</u><br/>"
                                                                             "Header set X-Content-Type-Options &quot;"
                                                                             "nosniff&quot;</p>"),
                                                                     "report_rec": (
                                                                         'The X-Content-Type-Options (also known as &quot;nosniff&quot;) header protects '
                                                                         'against sniffing vulnerabilities. These vulnerabilities can occur when a '
                                                                         'website allows users to upload content; however, the user disguises '
                                                                         'a particular file type as something else, allowing them to perform '
                                                                         'cross-site scripting and compromise the website. <br/><br/> '
                                                                         'To enable this security header on your origin server: <br/><br/> '
                                                                         '<u>For Nginx</u><br/> '
                                                                         '<b>add_header X-Content-Type-Options &quot;nosniff&quot;</b><br/><br/> '
                                                                         '<u>For Apache</u><br/> '
                                                                         '<b>Header set X-Content-Type-Options &quot;nosniff&quot;</b><br/><br/> '
                                                                         'Contact your web hosting provider or web development team to implement the changes.')},
                                                         "policy": {"finding": "No CSP",
                                                                    "rec": ("<p>The HTTP Content-Security-Policy (CSP) "
                                                                            "response header allows website "
                                                                            "administrators to control the resources "
                                                                            "the browser can load for a given page. "
                                                                            "The policies primarily define what and "
                                                                            "where the browser can load from.<br/><br/>"
                                                                            "CSP helps defend against cross-site "
                                                                            "scripting (XSS), clickjacking and cross-"
                                                                            "site leak vulnerabilities.<br/><br/>"
                                                                            "The process of scripting a CSP can be "
                                                                            "complicated and is best done by your "
                                                                            "developer. For more information on how to "
                                                                            "write a CSP, please visit the <a href="
                                                                            "'https://developer.mozilla.org/en-US/docs/"
                                                                            "Web/HTTP/Headers/Content-Security-"
                                                                            "Policy', target='_blank'>Mdn Web Docs by "
                                                                            "Mozilla</a> or <a href='https://"
                                                                            "cheatsheetseries.owasp.org/cheatsheets/"
                                                                            "Content_Security_Policy_Cheat_Sheet."
                                                                            "html', target='_blank'>OWASP Cheat Sheet "
                                                                            "Series.</a><br/><br/>"
                                                                            "<b>CSP Syntax</b><br/>"
                                                                            "<b>Content-Security-Policy:</b> <i>&lt;"
                                                                            "policy-directive&gt;; &lt;policy-directive"
                                                                            "&gt;</i> where <i>&lt;policy-directive&gt;"
                                                                            "</i> consists of: <i>&lt;directive&gt;"
                                                                            "</i> <i>&lt;value&gt;</i> with no "
                                                                            "internal punctuation.</p>"),
                                                                    "report_rec": ('The HTTP Content-Security-Policy (CSP) response header allows website '
                                                                                   'administrators to control the resources the browser can load for a given '
                                                                                   'page. This helps defend against cross-site scripting (XSS), clickjacking '
                                                                                   'and cross-site leak vulnerabilities.<br/><br/> '
                                                                                   'The process of scripting a CSP can be complicated and is best done by consulting '
                                                                                   'your web hosting provider or developer for the specific settings to be used. '
                                                                                   'For more information on how to write a CSP, please visit the <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy"'
                                                                                   'color="#0000EE" underline="true"> Mdn Web Docs by Mozilla</a> '
                                                                                   'or <a href="https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html" '
                                                                                   'color="#0000EE" underline="true"> OWASP Cheat Sheet Series</a>.'
                                                                                   )
                                                                    },
                                                         "cookie": {"finding": "No SSL/TLS Certificate",
                                                                    "rec": ("<p>SSL (Secure Sockets Layers) and TLS "
                                                                            "(Transport Layer Security) are "
                                                                            "cryptographic protocols that provide "
                                                                            "authentication and data encryption "
                                                                            "between servers, machines, and "
                                                                            "applications operating over a "
                                                                            "network.<br/><br/>"
                                                                            "It keeps user data secure, helps verify "
                                                                            "the authenticity of the website's "
                                                                            "ownership, prevents attackers from "
                                                                            "creating a fake version of the site, and "
                                                                            "helps gain user trust.<br/><br/>"
                                                                            "TLS is an updated, more secure version of "
                                                                            "SSL. When you buy an SSL certificate, "
                                                                            "most providers will provide you with the "
                                                                            "most up to date versions.<br/><br/>"
                                                                            "We recommend purchasing an SSL "
                                                                            "certificate even when your website does "
                                                                            "not provide business or e-commerce "
                                                                            "transactions.</p>")}
                                                         },
                                             "impact": ("<p>Insecure headers could result in your website being used "
                                                        "as a stepping stone to attack your website’s visitors.</p>"
                                                        ),
                                             },

                        }
