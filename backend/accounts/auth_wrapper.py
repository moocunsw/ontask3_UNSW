''' LTI AUTHENTICATION '''
from django.conf import settings
from jwt import decode, ExpiredSignature
from cryptography.fernet import Fernet
from .auth_handler import UserAuthHandler

class LTIAuthHandler(UserAuthHandler):
    '''Login methods for LTI authentication'''

    def authenticate_user(self, payload):
        print "########### LTI PAYLOAD #############"
        print payload
        print "########### LTI PAYLOAD #############"
        return None



class AAFAuthHandler(UserAuthHandler):
    '''Login methods for AAF Rapid connect'''
    def __init__(self):
        '''Initializes the configurations for the AAF authentication'''
        # Maps the AAF configuration from the settings file
        self.config = settings.AAF_CONFIG
        self.cipher_suite = Fernet(settings.CIPHER_SUITE_KEY)

    def authenticate_user(self, jwt_payload):
        '''Verifies if AAF has authenticated the user and returns a User object'''
        try:
            # Verifies signature and expiry time
            # TODO remap the input variable to the value
            # passed from AAF [self.request.POST['assertion']]
            verified_jwt = decode(jwt_payload['assertion'], self.config['secret_key'], audience=self.config['aaf.edu.au']['aud'])

            # TODO  - Check: In a complete app we'd also store and
            # validate the jti value to ensure there is no replay attack
            if verified_jwt['aud'] == self.config['aaf.edu.au']['aud'] \
            and verified_jwt['iss'] == self.config['aaf.edu.au']['iss']:
                user_attributes = verified_jwt['https://aaf.edu.au/attributes']
                email = user_attributes["mail"]
                fullname =  user_attributes["displayname"]
                password = self.cipher_suite.encrypt(email)
                role = self.extract_user_role(user_attributes["edupersonscopedaffiliation"])
                user = self.authenticate(email, fullname, password, role)
                return user
            else:
                #self.status = 403
                #TODO logging
                #self.response.write('Error: Not for this audience')
                print "############ 403 Not Authorized ##############"
        except ExpiredSignature:
            #self.status = 403
            #TODO logging
            #self.response.write('Error: Security cookie has expired')
            print "############ 403 ExpiredSignature ##############"
        return None

    def extract_user_role(self, user_role_mapping):
        '''Retrieves the correct role mapping to set the
        permissions against user authenticated against AAF'''

        role_domain = user_role_mapping.split(";")

        # Check for a Staff role
        for role in role_domain:
            if role in self.config['role_mappings']['staff']:
                return 'STAFF'
        return 'STUDENT'
