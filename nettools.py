import gzip
import logging
import os
import GeoIP
import urllib
import socket
import whois

from errbot import botcmd, BotPlugin

FLAGS = 'http://media.xfire.com/images/flags/%s.gif'
RESULT = """\
     City: %(city)s [%(postal_code)s]
   Region: %(region_name)s [%(region)s]
  Country: %(country_name)s
Time Zone: %(time_zone)s
Longitude: %(longitude)f
 Latitude: %(latitude)f
"""

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error: # not a valid address
        return False
    return True


class Nettools(BotPlugin):
    min_err_version = '1.6.8'

    def activate(self):
        GEOIP_DB = self.plugin_dir + os.sep + 'GeoLiteCity.dat'
        if not os.path.exists(GEOIP_DB + '.gz'):
            logging.warning('I am downloading the geoip DB, please wait ...')
            urllib.urlretrieve ("http://www.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz", GEOIP_DB + '.gz')
        if not os.path.exists(GEOIP_DB):
            logging.warning('Ungzipping the geoip DB, please wait ...')
            with open(GEOIP_DB, 'w') as f:
                f.write(gzip.open(GEOIP_DB + '.gz').read())

        self.gi = GeoIP.open(GEOIP_DB, GeoIP.GEOIP_STANDARD)
        super(Nettools, self).activate()



    def deactivate(self):
        self.gi = None

    @botcmd
    def geoip(self, mess, args):
        """
        Display geographical information about the given IP / machine name
        """
        if not args:
            return 'What should I look for ?'

        result = self.gi.record_by_addr(args) if is_valid_ipv4_address(args) else self.gi.record_by_name(args)
        self.send(mess.getFrom(), FLAGS % result['country_code'].lower(), message_type=mess.getType())
        return RESULT % result

    @botcmd
    def whois(self, mess, args):
        """
        Display whois information about the given IP / machine name
        """
        if not args:
            return 'What should I look for ?'

        domain = whois.query(str(args))
        return '\n'.join(['%25s : %s' % (k,v) for k,v in domain.__dict__.iteritems()])
