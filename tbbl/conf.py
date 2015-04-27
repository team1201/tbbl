########################################
# conf.py
#
# Author: zrong
# Creation: 2015-04-20
########################################

class ConfBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def build(self):
        noAnyArgs = True
        return noAnyArgs

