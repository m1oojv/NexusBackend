import requests
import logging
from time import sleep


# Secure headers for website
class HeaderScanner:
    def __init__(self, domain, max_tries=5):
        """
        this class takes the passed url and checks it for the required secure headers

        :param domain:  the domain that you'd like to check
        :type domain:   string
        """
        self.url = 'https://' + domain
        for i in range(max_tries):
            try:
                response = requests.get(self.url, timeout=10)
            except requests.exceptions.Timeout as e:
                logging.warning(f"Request timeout. Trying again...")
                if i < max_tries - 1:
                    sleep(5)
                    continue
                else:
                    raise e
            logging.debug(response.headers)
            if not response.status_code // 100 == 2:
                logging.warning(f"Unexpected response {response}")
                if i < max_tries - 1:
                    sleep(5)
                    continue
            response.raise_for_status()
            self.headers = response.headers
            self.cookies = response.cookies
            break

    def scan_xxss(self):
        """config failure if X-XSS-Protection header is not present"""
        item = {"xxss": False}
        try:
            if self.headers["X-XSS-Protection"]:
                logging.debug("[+] X-XSS-Protection : pass")
                item["xxss"] = True
            else:
                logging.debug("[-] X-XSS-Protection header not present : fail!")
        except KeyError:
            logging.debug("[-] X-XSS-Protection header not present : fail!")
        return item

    def scan_nosniff(self):
        """X-Content-Type-Options should be set to 'nosniff' """
        item = {"nosniff": False}
        try:
            if self.headers["X-Content-Type-Options"].lower() == "nosniff":
                logging.debug("[+] X-Content-Type-Options : pass")
                item["nosniff"] = True
            else:
                logging.debug("[-] X-Content-Type-Options header not set correctly : fail!")
        except KeyError:
            logging.debug("[-] X-Content-Type-Options header not present : fail!")
        return item

    def scan_xframe(self):
        """X-Frame-Options should be set to DENY or SAMEORIGIN"""
        item = {"xframe": False}
        try:
            if "deny" in self.headers["X-Frame-Options"].lower():
                logging.debug("[+] X-Frame-Options : pass")
                item["xframe"] = True
            elif "sameorigin" in self.headers["X-Frame-Options"].lower():
                logging.debug("[+] X-Frame-Options : pass")
                item["xframe"] = True
            else:
                logging.debug("[-] X-Frame-Options header not set correctly : fail!")
        except KeyError:
            logging.debug("[-] X-Frame-Options header not present : fail!")
        return item

    def scan_hsts(self):
        """config failure if HSTS header is not present"""
        item = {"hsts": False}
        try:
            if self.headers["Strict-Transport-Security"]:
                logging.debug("[+] Strict-Transport-Security : pass")
                item["hsts"] = True
            else:
                logging.debug("[-] Strict-Transport-Security header not configured correctly : fail!")
        except KeyError:
            logging.debug("[-] Strict-Transport-Security header not present : fail!")
        return item

    def scan_policy(self):
        """config failure if Security Policy header is not present"""
        item = {"policy": False}
        try:
            if self.headers["Content-Security-Policy"]:
                logging.debug("[+] Content-Security-Policy : pass")
                item["policy"] = True
            else:
                logging.debug("[-] Content-Security-Policy header not configured correctly : fail!")
        except KeyError:
            logging.debug("[-] Content-Security-Policy header not present : fail!")
        return item

    @staticmethod
    def scan_secure(cookie):
        """Set-Cookie header should have the secure attribute set"""
        item = {"secure": False}
        if cookie.secure:
            logging.debug("[+] Secure : pass")
            item["secure"] = True
        else:
            logging.debug("[-] Secure attribute not set : fail!")
        return item

    @staticmethod
    def scan_httponly(cookie):
        """Set-Cookie header should have the HttpOnly attribute set"""
        item = {"httponly": False}
        if cookie.has_nonstandard_attr('httponly') or cookie.has_nonstandard_attr('HttpOnly'):
            logging.debug("[+] HttpOnly : pass")
            item["httponly"] = True
        else:
            logging.debug("[-] HttpOnly attribute not set : fail!")
        return item

    def run(self):
        xxss = self.scan_xxss()
        nosniff = self.scan_nosniff()
        xframe = self.scan_xframe()
        hsts = self.scan_hsts()
        policy = self.scan_policy()

        cookies = []
        for cookie in self.cookies:
            logging.debug(f"Set-Cookie: {cookie.name}")
            secure = self.scan_secure(cookie)
            httponly = self.scan_httponly(cookie)
            cookie_result = {"name": cookie.name, "value": cookie.value, **secure, **httponly}
            cookies.append(cookie_result)

        return {"cookies": cookies, **xxss, **nosniff, **xframe, **hsts, **policy}
