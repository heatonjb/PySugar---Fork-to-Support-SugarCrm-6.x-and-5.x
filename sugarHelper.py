from pysugar import *
from django.conf import settings

class SugarSingleton :

    # Create a class variable that will hold a reference
    # to the single instance of SugarSingleton.

    instance = None

    # Define a helper class that will override the __call___
    # method in order to provide a factory method for SugarSingleton.

    class SugarSingletonHelper :
        
        
        def sugar_username(self):
            if settings.SUGAR_USE_DEV_SERVER :
                return settings.SUGAR_DEV_USER
            else:
                return settings.SUGAR_PROD_USER
        
        def sugar_password(self):
            if settings.SUGAR_USE_DEV_SERVER :
                return settings.SUGAR_DEV_PASS
            else:
                return settings.SUGAR_PROD_PASS
            
        def sugar_url(self):
            if settings.SUGAR_USE_DEV_SERVER :
                return settings.SUGAR_DEV_URL
            else:
                return settings.SUGAR_PROD_URL
        

        def __call__( self, *args, **kw ) :

            # If an instance of SugarSingleton does not exist,
            # create one and assign it to SugarSingleton.instance.
            
            if SugarSingleton.instance is None :
                object  = SugarSession(self.sugar_username(), self.sugar_password(), self.sugar_url(),'TRUE')
                SugarSingleton.instance = object
               
                
            # Return SugarSingleton.instance, which should contain
            # a reference to the only instance of SugarSingleton
            # in the system.
            
            #Test to see if a connection is working and operational, if not create a new session.
            try:
                print SugarSingleton.instance.get_gmt_time()
            except pysugar.SugarError:
                SugarSingleton.instance = SugarSession(self.sugar_username(), self.sugar_password(), self.sugar_url(),'TRUE')
            
            return SugarSingleton.instance
        
        def test_connection( self, *args, **kw ) :
            try:
                print SugarSingleton.instance.get_gmt_time()
            except pysugar.SugarError:
                SugarSingleton.instance = SugarSession(self.sugar_username(), self.sugar_password(), self.sugar_url(),'TRUE')

    # Create a class level method that must be called to
    # get the single instance of SugarSingleton.

    getInstance = SugarSingletonHelper()

    # Initialize an instance of the SugarSingleton class.

    def __init__( self ) :

        # Optionally, you could go a bit further to guarantee
        # that no one created more than one instance of SugarSingleton:

        if not SugarSingleton.instance == None :
            raise RuntimeError, 'Only one instance of SugarSingleton is allowed!'

        #Continiue initialization...


