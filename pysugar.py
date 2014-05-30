#!/usr/bin/env python
# License: PSF
# see: LICENSE
# for full text of the license
#
from elementsoap import ElementSOAP
from elementtree.ElementTree import tostring, dump
import md5
import xml
from pytz import timezone
import datetime
import base64
import urllib2
import types
from pysugar_version import version, major_version, minor_version, mid_version

__version__ = version
__author__ = "Florent Aide"
__doc__ = '''This is the transport layer for the pysugar library.
It uses ElementSOAP in order to communicate with the Sugar NuSoap Server.
'''

def item_to_name_value(item):
    '''
    takes a real item dictionnary and prepare it for soap
    returns a name value formated list of dictionnaries
    '''
    nv_list = []
    for key in item:
        nv_list.append({'name':key, 'value':item[key]})
    
    return nv_list

def name_value_to_item(nv_list):
    '''
    takes a name/value list from a sugar answer and returns a
    dictionnary mapping item
    '''
    #print tostring(nv_list)
    item = {}

    #piece = nv_list.find('item')
    item['id'] = nv_list.findtext('id') 
    item['module_name'] = nv_list.findtext('module_name')

    nv = nv_list.find('name_value_list')
    for el in nv.findall('item'):
        item[el.findtext('name')] = el.findtext('value')

    return item
        
class SugarError(Exception):
    '''
    This is the base class for our errors
    '''
    pass

class SugarOperationnalError(SugarError):
    '''
    when some unknow & weird error occurs
    '''
    pass

class SugarLoginError(SugarError):
    '''
    When a login error occurs, we raise this one
    '''
    pass

class SugarLogoutError(SugarError):
    '''
    in case of error during logout phase
    '''
    pass

class SugarCredentialError(SugarError):
    '''
    When a function call requiring a valid session id is call without
    one, this exception will be raised
    '''
    pass

class SugarVersionError(SugarError):
    '''
    If an error occurs on the version number
    '''
    pass

class SugarConnectError(SugarError):
    '''
    any connection error
    '''
    pass

class SugarDataError(SugarError):
    '''
    An error where the data from the server does not macth what we
    were expecting.
    '''
    pass

class SugarService(ElementSOAP.SoapService):
    '''
    This is the transport part of pysugar, it implements the soap
    calls necessary to talk to the NuSOAP server.
    This class should no be used directly by end-users.
    End-users should prefer to use the SugarSession class
    that encapsulates the notion of session and takes care of
    providing the session_id to the underlying sugar service
    '''
    def __init__(self, url):
        self.url = url
        self.application_name = "pysugar"
        ElementSOAP.SoapService.__init__(self, url)
    
    def login(self, user, password):
        """
        this will log into sugar given a username and a password
        it will return the uuid for the session

        if an error occurs, a SugarLoginError is raised.
        """
        pass_hash = md5.new(password).hexdigest()
        action = 'login'
        request = ElementSOAP.SoapRequest(action)
        user_auth = ElementSOAP.SoapElement(request, "user_auth")
        ElementSOAP.SoapElement(user_auth, "user_name", "string", user)
        ElementSOAP.SoapElement(user_auth, "password", "string", pass_hash)
        ElementSOAP.SoapElement(user_auth, "version", "string", '1.2')
        ElementSOAP.SoapElement(request, "application_name",
                "string", self.application_name)
        
        response = self.call(action, request)
        result = response.find('return')
        error_element = result.find('error')
        if not error_element is None:
            # there was a problem we need to raise an exception
            raise SugarLoginError('number: %s, name: %s, desc: %s' % (
                    error_element.findtext('number'),
                    error_element.findtext('name'),
                    error_element.findtext('description')
                    ))

        return result.findtext('id')
    
    def logout(self, session_id):
        '''
        given a session id, will make sure to invalidate this session
        so it cannot be used subsequently.
        For security reasons it is important to use this method
        '''
        action  = 'logout'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)

        response = self.call(action, request)
        ret = response.find('return')
        error = int(ret.findtext('number'))
        if error:
            name = ret.findtext('name')
            desc = ret.findtext('description')
            raise SugarLogoutError('name: "%s", desc: "%s"' % (name, desc))

    def get_user_id(self, session_id):
        '''
        given a session_id, will return the user_id that is logged in
        '''
        action = 'get_user_id'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)

        response = self.call(action, request)
        return response.findtext('return')

    def test(self, teststring):
        '''
        a ping function to make sure the NuSOAP server is up and running
        '''
        
 #No longer available in Sugar 6.1 JH
        
        #action = 'test'
        #request = ElementSOAP.SoapRequest(action)
        #ElementSOAP.SoapElement(request, "string", "string", teststring)
        
        #response = self.call(action, request)
        #return response.findtext('return')
    
        return self.get_server_version()

    def get_gmt_time(self):
        '''
        '''
        action = 'get_gmt_time'
        request = ElementSOAP.SoapRequest(action)

        response = self.call(action, request)
        return response.findtext('return')

    def get_server_version(self):
        '''
        '''
        action = 'get_server_version'
        request = ElementSOAP.SoapRequest(action)

        response = self.call(action, request)
        return response.findtext('return')

    def set_entry(self, session_id, module, item):
        '''
        creates an item in the given module
        module is a string representing the module ie: 'Leads' or 'Contacts'
        This will return the id for the newly created item or raise
        a SugarError in case of problem.
        '''
        action = 'set_entry'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "module", "string", module)
        nv_list = ElementSOAP.SoapElement(request, "name_value_list", "Array")
        for key in item:
            item_el = ElementSOAP.SoapElement(nv_list, "item")
            ElementSOAP.SoapElement(item_el, 'name', 'string', key)
            ElementSOAP.SoapElement(item_el, 'value', 'string', item[key])

        #print tostring(request)

        response = self.call(action, request)
        ret = response.find('return')

        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        return ret.findtext('id')
    
    def set_entries(self, session_id, module, items):
        '''
        create multiple entries at the same time in the specified module
        '''
        action = 'set_entries'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "module", "string", module)
        vlists = ElementSOAP.SoapElement(request, "name_value_lists", "Array")
        for item in items:
            vlist = ElementSOAP.SoapElement(vlists, "name_value_list", "Array")
            for key in item:
                item_el = ElementSOAP.SoapElement(vlist, "item")
                ElementSOAP.SoapElement(item_el, 'name', 'string', key)
                ElementSOAP.SoapElement(item_el, 'value', 'string', item[key])

        #print tostring(request)
        
        response = self.call(action, request)
        ret = response.find('return')

        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        ids_el = ret.find('ids').findall('item')
        ids = []
        for el in ids_el:
            ids.append(el.text)

        return ids

    def get_entry(self, session_id, module, id, select_fields):
        '''
        given a session_id this method enables us
        to interrogate a specified module
        an to ask for a specific object by id
        the select_fields is a way to ask for only
        some fields to be returned instead
        of the whole object : currently does nothing...

        In case of error this module will raise a SugarError exception
        '''
        action = 'get_entry'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "module", "string", module)
        ElementSOAP.SoapElement(request, "id", "string", id)
        ElementSOAP.SoapElement(request, "selection", "list", select_fields)

        response = self.call(action, request)
        ret = response.find('return')
        entry_list = ret.find('entry_list')

        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        item = entry_list.find('item')

        return name_value_to_item(item)

    def get_entry_list(self, session_id, module, query, order_by,
                offset, selection, max_result, deleted):
        '''
        Get a list of entries for a specified module in essence the same
        as a get_entry call where the result will be a list of items
        instead of just one.
        query must be of the form:
        "leads.last_name LIKE 'T%'"
        or
        "leads.last_name is not NULL"
        '''
       
        action = 'get_entry_list'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "module", "string", module)
        ElementSOAP.SoapElement(request, "query", "string", query)
        ElementSOAP.SoapElement(request, "order_by", "string", order_by)
        ElementSOAP.SoapElement(request, "offset", "integer", offset)
        ElementSOAP.SoapElement(request, "select_fields", "string", selection)
        ElementSOAP.SoapElement(request, "max_results", "integer", max_result)
        ElementSOAP.SoapElement(request, "deleted", "integer", deleted)
       
        print query
        print action
       
        response = self.call(action, request)
        
        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))
       
        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        entries = ret.find('entry_list').findall('item')
        elist = []
        for entry in entries:
            elist.append(name_value_to_item(entry))

        # TODO: we should also return the next offset and friends...
        return elist

    def get_available_modules(self, session_id):
        '''
        returns the list of modules names (strings)
        we can access with our login
        '''
        action = 'get_available_modules'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)

        response = self.call(action, request)
        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        modules_el = ret.find('modules')
        modules_list = []
        for i in modules_el:
            modules_list.append(i.text)

        return modules_list

    def get_note_attachment(self, session_id, attachement_id):
        '''
        given a session_id and an attachement_id this function will
        return a 2-tuple containing the filename and the actual file content
        the file content is binary data as if it were the result of a read()
        operation on a file like object...
        '''
        action = 'get_note_attachment'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "id", "string", attachement_id)

        response = self.call(action, request)
        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        note_attachm = ret.find('note_attachment')
        filename = note_attachm.findtext('filename')
        file = base64.b64decode(note_attachm.findtext('file'))

        return (filename, file)

    def get_relationships(self, session_id, module_name, module_id,
            related_module, related_module_query, deleted=False):
        '''
        session_id: a valid session id
        module_name: a module name such as 'Accounts'
        module_id: a valid object id in the module name
        related_module: a valid module name such as 'Contacts' that
                may have objects related the the already given module_id
        related_module_query: a string representing a subset of the
                SQL Query that will be executed on the server!!!
                (seems dangerous)
        deleted: a boolean. If True, then all records will be returned even
                the deleted ones. Defaults to False if nothing given


        returns: a list of ids for the related module objects that were found
                matching your search criterions


        Discussion:

        There are some limitations currently enforced on the server side
        by the PHP code. You have only access to a limited amount of base
        modules (module_name) and for each module_name you only can
        name a restricted list of related modules...

        If you specify something else the server will return an error stating
        that the module does not exist

        An excerpt of the
        PHP comment follows:

        ----
        * Only the listed combinations below are supported.  On the left is the
        * primary module.  Under each primary module is a
        * list of available related modules.
        *  'Contacts'=>
        *              'Calls'
        *              'Meetings'
        *              'Users'
        *  'Users'=>
        *              'Calls'
        *              'Meetings'
        *              'Contacts'
        *  'Meetings'=>
        *              'Contacts'
        *              'Users'
        *  'Calls'=>
        *              'Contacts'
        *              'Users'
        *  'Accounts'=>
        *              'Contacts'
        *              'Users'
        ----

        Exemple Use:
        >>> rels = sugar_session.get_relationships(
        '644b1fa1de5937ba1484516777e34aae',
        'Accounts', 'e8151a7f-136d-3b8e-b026-456ae620866d',
        'Contacts', '')
        >>> rels
        ['4841ac25-083a-f629-da32-456b061467d0']

        Background:
        the PHP code executed on the server is this one:

        ----
        $result = $r_mod->db->query("SELECT id, date_modified FROM " \
        .$r_mod->table_name \
        . " WHERE id IN $in AND ( $related_module_query )");
        ----

        as you can see: the related module query is passed
        'as is' in the WHERE clause.
        Please note we are NOT the authors of the PHP code. For any inquiries
        about this you should direct your questions to the Sugar CRM team.

        '''
        if not isinstance(deleted, types.BooleanType):
            msg='deleted keyword must be an integer, not: %s' % type(deleted)
            raise ValueError(msg)

        action = 'get_relationships'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "module_name", "string", module_name)
        ElementSOAP.SoapElement(request, "module_id", "string", module_id)
        ElementSOAP.SoapElement(request, "related_module",
                "string", related_module)
        ElementSOAP.SoapElement(request, "related_module_query",
                "string", related_module_query)
        ElementSOAP.SoapElement(request, "deleted", "string", deleted)

        response = self.call(action, request)
        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        items_el = ret.find('ids')
        id_list = []
        for item in items_el:
            id_list.append(item.findtext('id'))

        return id_list

    def set_relationship(self, session_id, module1,
            module1_id, module2, module2_id):
        '''
        set a relationship beetween module1_id and module2_id
        the same rules apply that are described in get_relationships
        '''
        action = 'set_relationships'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        srv = ElementSOAP.SoapElement(request, "set_relationship_value")
        ElementSOAP.SoapElement(srv, "module1", "string", module1)
        ElementSOAP.SoapElement(srv, "module1_id", "string", module1_id)
        ElementSOAP.SoapElement(srv, "module2", "string", module2)
        ElementSOAP.SoapElement(srv, "module2_id", "string", module2_id)

        response = self.call(action, request)
        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        return ret

    def prune_meetings(self, session_id, date_from, date_to):
        '''
        remove ALL the meetings from the database !!!
        USE AT YOUR OWN RISK.
        You need to know what you want to do when using this function
        please make sure you do some tests before using this function
        on a live server
        This function is ONLY available if you install the meeting extension
        from the install directory of the pysugar distribution
        '''
        assert isinstance(date_from, datetime.date), \
            "date_from should be a datetime.date instance"
        assert isinstance(date_to, datetime.date), \
            "date_to should be a datetime.date instance"

        action = 'prune_meetings'
        request = ElementSOAP.SoapRequest(action)
        ElementSOAP.SoapElement(request, "session", "string", session_id)
        ElementSOAP.SoapElement(request, "date_from",
            "string", date_from.strftime('%Y-%m-%d'))
        ElementSOAP.SoapElement(request, "date_to", 
            "string", date_to.strftime('%Y-%m-%d'))
        response = self.call(action, request)

        ret = response.find('return')
        error_elem = ret.find('error')
        error = int(error_elem.findtext('number'))

        if error:
            name = error_elem.findtext('name')
            desc = error_elem.findtext('description')
            raise SugarError('number: %s, name: "%s", desc: "%s"' % (
                    error, name, desc))

        return ret

class SugarSession:
    '''
    This class is the entry point to the rest of the API.
    A Sugar Session is the first thing we need in order to
    communicate with the Sugar Server.
    When we have a session all other requests to the server will
    be called on the session object.
    '''
    
    
    def __init__(self, username, password, base_url,
            debug=True, user_management=False, nusoapfile='soap.php'):
        '''
        username: a string representing the login
        password: a string with the password for the login
        base_url: a string containing the url for the sugar server
                without the soap.php?wsdl trailer
        debug: a boolean, False by default
        user_management: a boolean, False by default
        nusoapfile: the name of the nusoap file (php script) that will
        be used. This is here so that users can write their own php nusoap
        servers for sugar and connect to it.
        
        example:
            s = SugarSession('myuser', 'mypass', 'http://myserver/sugar')
        
        Here s should be a pysugar.SugarSession object ready to be used
        '''
        
        self.user_management = user_management
        self._session_id = False
        self._debug = debug

        self.base_url = base_url
        self.application_name = 'pysugar'
        #soap_url = base_url + '/soap.php?wsdl'
        user_url = base_url + '/soap_users.php?wsdl'
        soap_url = base_url + "/" + nusoapfile
        
        try:
            urllib2.urlopen(soap_url)
        except urllib2.HTTPError, e:
            msg = "Can't resolve %s." % e.geturl()
            raise SugarConnectError(msg)

        if user_management:
            try:
                urllib2.urlopen(user_url)
            except urllib2.HTTPError, e:
                msg = "Can't resolve %s.\n" % e.geturl()
                msg += "Maybe you should deploy the soap_users.php script ?"
                raise SugarConnectError(msg)

        self.service = SugarService(soap_url)
        #try:
        #    self.soap_proxy = SOAPpy.WSDL.Proxy(soap_url)
        #
        #except xml.parsers.expat.ExpatError, args:
        #    msg = 'Cannot communicate with server,'
        #    msg += 'please check the url. msg= %s' % args
        #    raise SugarError(msg)

        #if user_management:
        #    try:
        #        self.user_proxy = SOAPpy.WSDL.Proxy(user_url)
        #    except xml.parsers.expat.ExpatError, args:
        #        msg = 'Cannot communicate with server,'
        #        msg += 'please check the url. msg= %s' % args
        #        raise SugarError(msg)

        if not self.get_gmt_time():
            msg = "The Sugar server seems to be offline"
            msg += "or unresponsive"
            raise SugarError(msg)
        else:
            self.login(username, password)

   

     

    def __validate_login(self):
        '''
        this method is for internal use only. It is used to make sure
        there as been a successful login in the past for our session.
        Each method that requires a valid session should call this before
        anything else.
        If no session has been opened already this method will spit an
        SugarCredentialError exception
        If session is OK this method returns nothing
        '''
        if not self._session_id:
            raise SugarCredentialError(
                    'A valid session id is required to use this method')

    def login(self, username, password):
        '''
        tries to log into the Sugar server with the given credentials
        '''
        
        session_id = self.service.login(username, password)
        self._session_id = session_id

        if self._debug:           
            self.get_user_id()
            
        
    def get_entry_list(self, module, query, order_by,
            offset, selection, max_result, deleted):
        '''
        this raw call enables to ask any modules to give its list of data
        ie: Leads module will return a list of leads selected according to
        our search criterions.
        the query string must be of the form:
        "leads.last_name LIKE 'T%'"
        this is basically an SQL WHERE clause. To have more abstraction about
        these things we will use the sugarobjects module.
        '''
        self.__validate_login()

        return self.service.get_entry_list(self._session_id,
                module, query, order_by, offset,
                selection, max_result, deleted)
    
        #next_offset = res.next_offset
        #field_list = res.field_list
        #module_list = res.entry_list
        #errors = res.error
        #num_result = res.result_count
    
        #my_items = []

        #for item in module_list:
        #    my_items.append(dict(item.name_value_list))

        #return my_items

    def get_entry(self, module, id, selection):
        '''
        This method is the way to get entries according to their ids
        '''
        self.__validate_login()
        return self.service.get_entry(self._session_id, module,
                id, selection)

    def set_entry(self, module, item):
        '''
        create a new entry in Sugar
        if an error occurs a SugarError will be raised
        if the operation is a success, a string representing the id of the
        created/modified entry will be returned
        '''
        self.__validate_login()
        return self.service.set_entry(self._session_id, module, item)

    def set_entries(self, module, items):
        '''
        create a batch of new entries in Sugar for the same module
        '''
        self.__validate_login()
        return self.service.set_entries( self._session_id,
                module, items)

    def set_note_attachment(self, note):
        '''
        create a new note attachment in Sugar
        '''
        raise NotImplementedError
    
    def get_note_attachment(self, id):
        '''
        retrieve a note attachement from sugar using its id
        returns a 2-tuple containing the filename of the attachment
        and the binary content of the file attached to the note
        '''
        self.__validate_login()
        res = self.service.get_note_attachment(self._session_id, id)

        return res
    
    def relate_note_to_module(self, note_id, module_name, module_id):
        '''
        ???
        '''
        raise NotImplementedError

    def get_related_notes(self, module_name, module_id, selection):
        '''
        ???
        '''
        raise NotImplementedError

    def logout(self):
        '''
        destroy the given session on the server
        '''
        self.__validate_login()
        res = self.service.logout(self._session_id)
        # make sure session id is now invalid
        self._session_id = None
    
    def get_user_id(self):
        '''
        this will return a user id string
        if the session is invalid the returned user id will be '-1'
        '''
        self.__validate_login()
        return self.service.get_user_id(self._session_id)

    def get_module_fields(self, module_name):
        self.__validate_login()
        return self.soap_proxy.get_module_fields(
                self._session_id,
                module_name
                )
                
    def get_available_modules(self):
        '''
        Lists the modules present on the server we are logged in
        '''
        self.__validate_login()
        res = self.service.get_available_modules(self._session_id)

        return res
        #error = res.error
        #if error.number == '0':
        #    modules = res.modules
        #    return list(modules)
        #else:
        #    raise SugarError('%s' % error.description)

    def update_portal_user(self, username, name_value_list):
        '''
        ???
        '''
        raise NotImplementedError
    
    def create_user(self, user_name, password):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        self.__validate_login()

        res = self.user_proxy.create_user(
                self._session_id,
                user_name,
                password)

        if res.id == '-1':
            print res.error
        return res.id

    def test(self):
        '''
        test that the given url responds something we can use
        and the NuSoap php xmlrpc server is indeed present
        '''
        onetest = 'OneStringOfTest'
        #res = self.soap_proxy.test(onetest)
        res = self.service.test(onetest)
        if res == onetest:
            return True
        else:
            return False

    def get_server_time(self):
        '''
        returns the time on the server
        in local time.
        I did not implement this one since we have the GMT one
        and times seem to alway come back in UTC from sugar server:
        ie: when you look at a last modified timestamp from a sugar lead
        you will see that it is sent to you in UTC time by the server.
        '''
        raise NotImplementedError
    
    def get_gmt_time(self):
        '''
        returns the server time in GTM
        the returned time is a datetime.datetime instance in UTC timezone
        the timezone IS specified in the intance using the pytz library
        You can use this function without being logged into the server.
        '''
        res = self.service.get_gmt_time()
        utc = timezone('UTC')

        (ymd, hms) = res.split(' ')

        (year, month, day) = ymd.split('-')
        (hour, minute, second) = hms.split(':')

        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        
        return datetime.datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                0,
                tzinfo=utc
                )
    
    def get_server_version(self):
        '''
        returns the version number of the server
        this function can be used without a login...
        '''
        res = self.service.get_server_version()
        if res == '1.0':
            msg = 'The server does not disclose this information'
            raise SugarVersionError(msg)
        else:
            return res

    def get_user_role_ids(self, user_id):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        self.__validate_login()

        return self.user_proxy.get_user_role_ids(
                self._session_id,
                user_id)

    def remove_user_role(self, role_id, user_id):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        self.__validate_login()

        return self.user_proxy.remove_user_role(
                self._session_id,
                role_id,
                user_id)

    def get_relationships(self, module_name, module_id, related_module,
            related_module_query, deleted=False):
        '''
        session_id: a valid session id
        module_name: a module name such as 'Accounts'
        module_id: a valid object id in the module name
        related_module: a valid module name such as 'Contacts' that
                may have objects related the the already given module_id
        related_module_query: a string representing a subset of the
                SQL Query that will be executed on the server!!!
                (seems dangerous)
        deleted: a boolean. If True, then all records will be returned even
                the deleted ones. Defaults to False if nothing given


        returns: a list of ids for the related module objects that were found
                matching your search criterions


        Discussion:

        There are some limitations currently enforced on the server side
        by the PHP code. You have only access to a limited amount of base
        modules (module_name) and for each module_name you only can
        name a restricted list of related modules...

        If you specify something else the server will return an error stating
        that the module does not exist

        An excerpt of the
        PHP comment follows:

        ----
        * Only the listed combinations below are supported.  On the left is the
        * primary module.  Under each primary module is a list of
        * available related modules.
        *  'Contacts'=>
        *              'Calls'
        *              'Meetings'
        *              'Users'
        *  'Users'=>
        *              'Calls'
        *              'Meetings'
        *              'Contacts'
        *  'Meetings'=>
        *              'Contacts'
        *              'Users'
        *  'Calls'=>
        *              'Contacts'
        *              'Users'
        *  'Accounts'=>
        *              'Contacts'
        *              'Users'
        ----

        Exemple Use:
        >>> rels = sugar_session.get_relationships(
        '644b1fa1de5937ba1484516777e34aae',
        'Accounts', 'e8151a7f-136d-3b8e-b026-456ae620866d',
        'Contacts', '')
        >>> rels
        ['4841ac25-083a-f629-da32-456b061467d0']

        Background:
        the PHP code executed on the server is this one:

        ----
        $result = $r_mod->db->query("SELECT id, date_modified FROM " \
        .$r_mod->table_name \
        . " WHERE id IN $in AND ( $related_module_query )");
        ----

        as you can see: the related module query is passed
        'as is' in the WHERE clause.
        Please note we are NOT the authors of the PHP code. For any inquiries
        about this you should direct your questions to the Sugar CRM team.
        '''
        self.__validate_login()
        return self.service.get_relationships(
               self._session_id,
               module_name,
               module_id,
               related_module,
               related_module_query,
               deleted)
        

    def set_relationship(self, module1, module1_id, module2, module2_id):
        self.__validate_login()
        return self.service.set_relationship(
                self._session_id, module1, module1_id,
                module2, module2_id)
            
    def set_relationships(self, set_relationship_list):
        '''
        ???
        '''
        raise NotImplementedError
    
    def set_document_revision(self, document_revision):
        '''
        ???
        '''
        raise NotImplementedError
    
    def prune_meetings(self, date_from, date_to):
        '''
        this method will only work if the meeting extension has been installed
        on the server. All information regarding this extension can be found
        in the install directory or the pysugar distribution.
        '''
        self.__validate_login()
        return self.service.prune_meetings(
            self._session_id, date_from, date_to)

# vim: expandtab tabstop=4 shiftwidth=4:
