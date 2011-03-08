# License: PSF
# see: LICENSE
# for full text of the license
# 
# OO oriented Sugar Interface
# above the pysugar transport interface
#
# Original Idea: Florent Aide, <florent.aide@gmail.com>
# Design: Christophe de Vienne, <cdevienne@alphacent.com>
# Co-design : Florent Aide, <florent.aide@gmail.com>
#

from sugarobjects import SugarModule, SugarModuleCollection, SugarObject
from sugarobjects import sugar_str_field, sugar_date_field, \
        sugar_bool_field, sugar_relation_field, sugar_integer_field, \
        sugar_datetime_field, sugar_time_field, \
        init_SugarObject

class Lead(SugarObject):
    table_name = 'leads'

class User(SugarObject):
    '''
    For creating a valid user for normal usage,
    sugar needs at least these values:
        
        user.user_name = 'myloginname'
        user.last_name = 'MyLastName'
        user.user_hash = md5.new('myuserpassword').hexdigest()
        user.status = 'Active'
        user.employee_status = 'Active'
        
    '''
    table_name = 'users'

class Task(SugarObject):
    table_name = 'tasks'

class Meeting(SugarObject):
    table_name = 'meetings'

init_SugarObject(
        Lead,
        [
            sugar_str_field('portal_app'),
            sugar_str_field('portal_name'),
            sugar_bool_field('invalid_email'),
            sugar_bool_field('email_opt_out'),
            sugar_bool_field('do_not_call'),
            sugar_bool_field('deleted'),
            sugar_bool_field('converted'),
            sugar_str_field('status'),
            sugar_str_field('status_description'),
            sugar_str_field('lead_source'),
            sugar_str_field('lead_source_description'),
            sugar_str_field('description'),
            sugar_str_field('salutation'),
            sugar_str_field('title'),
            sugar_str_field('first_name'),
            sugar_str_field('last_name'),
            sugar_str_field('email1'),
            sugar_str_field('email2'),
            sugar_str_field('primary_address_street'),
            sugar_str_field('alt_address_street'),
            sugar_str_field('primary_address_city'),
            sugar_str_field('alt_address_city'),
            sugar_str_field('primary_address_postalcode'),
            sugar_str_field('alt_address_postalcode'),
            sugar_str_field('primary_address_state'),
            sugar_str_field('alt_address_state'),
            sugar_str_field('primary_address_country'),
            sugar_str_field('alt_address_country'),
            sugar_str_field('department'),
            sugar_str_field('phone_other'),
            sugar_str_field('phone_home'),
            sugar_str_field('phone_work'),
            sugar_str_field('phone_mobile'),
            sugar_str_field('phone_fax'),
            sugar_str_field('account_name'),
            sugar_str_field('account_description'),
            sugar_relation_field('account', 'account_id', 'Accounts'),
            sugar_str_field('opportunity_amount'),
            sugar_str_field('opportunity_name'),
            sugar_str_field('assigned_user_name'),
            sugar_relation_field('assigned_user', 'assigned_user_id', 'Users'),
            sugar_relation_field('reports_to', 'reports_to_id', 'Users'),
            sugar_relation_field('contact', 'contact_id', 'Contacts'),
            sugar_str_field('created_by_name'),
            sugar_relation_field('created_by', 'created_by', 'Users'),
            sugar_str_field('report_to_name'),
            sugar_str_field('modified_by_name'),
            sugar_relation_field('modified_user', 'modified_user_id', 'Users'),
            sugar_datetime_field('date_entered'),
            sugar_datetime_field('date_modified'),
            sugar_str_field('campaign_id'),
            #sugar_str_field('employee_c'),
            #sugar_str_field('Product_c'),
            sugar_str_field('refered_by'),
            #sugar_str_field('revenue_c'),
            sugar_relation_field('opportunity', 'opportunity_id',
                    'Opportunities'),
            #sugar_str_field('prospect_list_name'),
        ]
        )

init_SugarObject(
        User,
        [
            sugar_str_field('last_name'),
            sugar_str_field('employee_status'),
            sugar_str_field('user_password', send_only=True),
            sugar_str_field('phone_fax'),
            sugar_str_field('address_state'),
            sugar_str_field('messenger_id'),
            sugar_str_field('email2'),
            sugar_str_field('email1'),
            sugar_str_field('first_name'),
            sugar_datetime_field('date_entered'),
            sugar_str_field('title'),
            sugar_str_field('address_street'),
            sugar_bool_field('receive_notifications'),
            sugar_relation_field('reports_to', 'reports_to_id', 'Users'),
            sugar_relation_field('created_by', 'created_by', 'Users'),
            sugar_str_field('user_hash'),
            sugar_str_field('phone_other'),
            sugar_str_field('user_name'),
            sugar_str_field('status'),
            sugar_str_field('m_accept_status_fields'),
            sugar_str_field('description'),
            sugar_bool_field('deleted'),
            sugar_bool_field('is_group'),
            sugar_str_field('department'),
            sugar_str_field('phone_home'),
            sugar_str_field('c_accept_status_fields'),
            sugar_str_field('messenger_type'),
            sugar_str_field('address_city'),
            sugar_relation_field('modified_user', 'modified_user_id', 'Users'),
            sugar_str_field('phone_work'),
            sugar_date_field('date_modified'),
            sugar_str_field('address_country'),
            sugar_str_field('address_postalcode'),
            sugar_str_field('phone_mobile'),
            sugar_str_field('is_admin'),
            sugar_bool_field('portal_only'),
        ])
        
init_SugarObject(
        Meeting,
        [
            sugar_str_field('created_by_name'),
            sugar_date_field('date_end'),
            sugar_str_field('parent_type'),
            sugar_relation_field('assigned_user', 'assigned_user_id', 'Users'),
            sugar_integer_field('duration_minutes'),
            sugar_str_field('assigned_user_name'),
            sugar_str_field('contact_name'),
            sugar_datetime_field('date_entered'),
            sugar_str_field('outlook_id'),
            sugar_date_field('date_start'),
            sugar_relation_field('created_by', 'created_by', 'Users'),
            sugar_str_field('parent_id'),
            sugar_str_field('location'),
            sugar_str_field('modified_by_name'),
            sugar_str_field('status'),
            sugar_str_field('description'),
            sugar_bool_field('deleted'),
            sugar_time_field('time_start'),
            sugar_relation_field('modified_user', 'modified_user_id', 'Users'),
            sugar_str_field('name'),
            sugar_datetime_field('date_modified'),
            sugar_integer_field('reminder_time'),
            sugar_integer_field('duration_hours'),
        ])

init_SugarObject(
        Task,
        [
            sugar_date_field('date_due'),
            sugar_str_field('created_by_name'),
            sugar_str_field('parent_type'),
            sugar_relation_field('assigned_user', 'assigned_user_id', 'Users'),
            sugar_str_field('assigned_user_name'),
            sugar_str_field('contact_name'),
            sugar_datetime_field('date_entered'),
            sugar_str_field('date_due_flag'),
            sugar_time_field('time_due'),
            sugar_date_field('date_start'),
            sugar_relation_field('created_by', 'created_by', 'Users'),
            sugar_str_field('priority'),
            sugar_str_field('parent_id'),
            sugar_str_field('modified_by_name'),
            sugar_str_field('status'),
            sugar_str_field('description'),
            sugar_bool_field('deleted'),
            sugar_relation_field('contact', 'contact_id', 'Users'),
            sugar_time_field('time_start'),
            sugar_str_field('date_start_flag'),
            sugar_relation_field('modified_user', 'modified_user_id', 'Users'),
            sugar_str_field('name'),
            sugar_datetime_field('date_modified'),
        ])
        
class SugarStore(object):
    def __init__(self, sugar_session):
        self.backend = sugar_session
        self.m = SugarModuleCollection(self.backend)
        self.m.add('Leads', Lead)
        self.m.add('Users', User)
        self.m.add('Meetings', Meeting)
        self.m.add('Tasks', Task)

# vim: expandtab tabstop=4 shiftwidth=4:
