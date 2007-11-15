# Zope Captcha generation
import random
import sha
import string
import sys

from zope.interface import implements
from Acquisition import aq_inner
from Products.Five import BrowserView

from interfaces import ICaptchaView

CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789@:.-/' # no 0/O and I/1 confusion

COOKIE_ID = 'captchasessionid'
WORDLENGTH = 7

class Captcha(BrowserView):
    implements(ICaptchaView)
    
    _session_id = None
    __name__ = 'captcha'
    
    def _generate_session(self):
        """Ensure a session id exists
        
        Returns an integer counter of the number of captcha sessions active
        besides ourselves. Use this counter to ensure we get the correct
        session for an image or file.
        
        """
        if self._session_id is None:
            id = sha.new(str(random.randrange(sys.maxint))).hexdigest()
            self.request.response.setCookie(COOKIE_ID, id, path='/')
            self._session_id = id
    
    def _generate_word(self):
        """Create a word for the current session"""
        session = self.request[COOKIE_ID]
        seed = sha.new(session).digest()
        
        word = []
        for i in range(WORDLENGTH):
            index = ord(seed[i]) % len(CHARS)
            word.append(CHARS[index])
        return ''.join(word)
        
    def publishTraverse(self, name, request):
        try:
            counter = int(name)
        except ValueError:
            raise KeyError('No such captcha session')
        self._id_count = counter
        return self
    
    def _url(self, type):
        self._generate_session()
        return '/'.join((
            aq_inner(self.context).absolute_url(), 
            '@@' + self.__name__,
            type))
    
    def image_tag(self):
        return '<img src="%s" />' % (self._url('image'),)
    
    def audio_url(self):
        return self._url('audio')
        
    def verify(self, input):
        try:
            result = input.upper() == self._generate_word()
            # Delete the session key, we are done with this captcha
            self.request.response.expireCookie(COOKIE_ID, path='/')
        except KeyError:
            result = False # No cookie
        
        return result
        
    def image(self):
        pass
    
    def audio(self):
        pass

