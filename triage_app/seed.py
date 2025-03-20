from triage_app import models
from triage_app.database import SessionLocal
from triage_app.crud import hash_password

def seed_initial_data():
    session = SessionLocal()
    
    # Check if roles (and any other default information) exists
    if session.query(models.Role).count() == 0:
        roles = [
            models.Role(
                name='Level 1',
                permissions='{"ticket.assign":1,"ticket.close":1,"ticket.create":1,"ticket.edit":1,"ticket.reply":1,"ticket.transfer":1}',
                # "task.assign":1,"task.close":1,"task.create":1,"task.delete":1,"task.edit":1,"task.reply":1,"task.transfer":1,"canned.manage":1,"ticket.delete":1, "ticket.link":1,"ticket.markanswered":1,"ticket.merge":1,"ticket.refer":1,"ticket.release":1,"thread.edit":1
                notes='Role with unlimited access'
            ),
            models.Role(
                name='Level 2',
                permissions='{"ticket.assign":1,"ticket.close":1,"ticket.create":1,"ticket.edit":1,"ticket.transfer":1}',
                # "ticket.link":1,"ticket.merge":1,"ticket.reply":1,"ticket.refer":1,"ticket.release":1,"task.assign":1,"task.close":1,"task.create":1,"task.edit":1,"task.reply":1,"task.transfer":1,"canned.manage":1
                notes='Role with expanded access'
            ),
            models.Role(
                name='Level 3',
                permissions='{"ticket.assign":1,"ticket.create":1,"ticket.transfer":1}',
                # "ticket.link":1,"ticket.merge":1,"ticket.refer":1,"ticket.release":1,"task.assign":1,"task.reply":1,"task.transfer":1
                notes='Role with limited access'
            ),
            models.Role(
                name='Level 4',
                permissions='{}',
                notes='Simple role with no permissions'
            )
        ]
        session.add_all(roles)
        session.commit()
    
        
        sla = [
            models.SLA(
                sla_id = 1,
                name='Default SLA',
                grace_period=72,
                notes=''
            )  
        ]
        session.add_all(sla)
        session.commit()


        ticket_priorities_data = [
            models.TicketPriority(  
                priority_id=1,
                priority='low',
                priority_desc='Low',
                priority_color='#DDFFDD',
                priority_urgency=4
            ),
            models.TicketPriority( 
                priority_id=2,
                priority='normal',
                priority_desc='Normal',
                priority_color='#FFFFF0',
                priority_urgency=3
            ),
            models.TicketPriority(  
                priority_id=3,
                priority='high',
                priority_desc='High',
                priority_color='#FEE7E7',
                priority_urgency=2
            ),
            models.TicketPriority(  
                priority_id=4,
                priority='emergency',
                priority_desc='Emergency',
                priority_color='#FEE7E7',
                priority_urgency=1
            ),
        ]
        session.add_all(ticket_priorities_data)
        session.commit()


        ticket_statuses_data = [
            models.TicketStatus(  
                status_id=1,
                name='Open',
                state='open',
                mode='',
                sort='',
                properties='{}'
            ),
            models.TicketStatus(  
                status_id=2,
                name='Resolved',
                state='closed',
                mode='',
                sort='',
                properties='{}'
            ),
            models.TicketStatus(  
                status_id=3,
                name='Closed',
                state='closed',
                mode='',
                sort='',
                properties='{}'
            ),
            models.TicketStatus(  
                status_id=4,
                name='Archived',
                state='archived',
                mode='',
                sort='',
                properties='{}'
            ),
            models.TicketStatus(  
                status_id=5,
                name='Deleted',
                state='deleted',
                mode='',
                sort='',
                properties='{}'
            ),
        ]
        session.add_all(ticket_statuses_data)
        session.commit()
    

        groups_data = [
            models.Group(  
                group_id=1,
                name='Backend',
                notes='This team works on the backend infrastructure',
            ),
        ]
        session.add_all(groups_data)
        session.commit()
    

        departments_data = [
            models.Department(
                dept_id=1,
                sla_id=1,
                email_id='',
                name='Sales',
                signature='From, Sales'
            ),
            models.Department(
                dept_id=2,
                sla_id=2,
                email_id='',
                name='Support',
                signature='From, Support'
            ),
            models.Department(
                dept_id=3,
                sla_id=3,
                email_id='',
                name='Billing',
                signature='From, Billing'
            )
        ]
        session.add_all(departments_data)
        session.commit()


        agents_data = [
            models.Agent(
                agent_id=1,
                email='admin@test.com',
                password=hash_password('admin'),
                username='admin',
                permissions='{"user.create":1,"user.edit":1,"user.delete":1,"user.view":1,"agent.view":1}',
                # "faq.manage":1,"group.create":1,"group.view":1,"group.edit":1,"group.delete":1
                dept_id=1,
                role_id=1,
                firstname='Admin',
                lastname='User',
                signature='Admin User',
                timezone='EST',
                preferences='{"agent_default_page_size":"10","default_from_name":"Email Address Name","agent_default_ticket_queue":1,"default_signature":"My Signature"}',
                status=0,
                admin=1
            )
        ]
        session.add_all(agents_data)
        session.commit()




        forms_data = [
            models.Form(
                form_id=1,
                title='Ticket Details',
                instructions='Extra details to include with each submitted ticket',
                notes='Please fill in all fields'
            )
        ]
        session.add_all(forms_data)
        session.commit()


        form_fields_data = [
            models.FormField(
                field_id=1,
                form_id=1,
                order_id=1,
                type='text',
                label='Company Name',
                name='company name',
                configuration='{}',
                hint='Please input the company name'
            )
        ]
        session.add_all(form_fields_data)
        session.commit()


        topics_data = [
            models.Topic(
                topic_id=1,
                status_id=1,
                priority_id=1,
                dept_id=1,
                agent_id=1,
                sla_id=1,
                form_id=1,
                auto_resp=0,
                topic="Complaint",
                notes=''
            ),
            models.Topic(
                topic_id=2,
                status_id=1,
                priority_id=1,
                dept_id=1,
                agent_id=1,
                sla_id=1,
                form_id=None,
                auto_resp=0,
                topic="Complaint w/o Form",
                notes=''
            ),
            models.Topic(
                topic_id=3,
                status_id=1,
                priority_id=1,
                dept_id=1,
                agent_id=1,
                sla_id=1,
                form_id=1,
                auto_resp=0,
                topic="Incident",
                notes=''
            ),
            models.Topic(
                topic_id=4,
                status_id=1,
                priority_id=1,
                dept_id=1,
                agent_id=1,
                sla_id=1,
                form_id=1,
                auto_resp=0,
                topic="Change",
                notes=''
            ),
            models.Topic(
                topic_id=5,
                status_id=1,
                priority_id=1,
                dept_id=1,
                agent_id=1,
                sla_id=1,
                form_id=1,
                auto_resp=0,
                topic="Problem",
                notes=''
            )
        ]
        session.add_all(topics_data)
        session.commit()
    
        
        queues_data = [
            models.Queue(
                queue_id=1,
                agent_id=None,
                title='Open',
                config="{\"filters\": [[\"ticket_statuses.name\",\"in\",[\"Open\"]]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=2,
                agent_id=None,
                title='Closed',
                config="{\"filters\": [[\"ticket_statuses.name\",\"in\",[\"Closed\"]]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=3,
                agent_id=None,
                title='Unanswered',
                config="{\"filters\": [[\"answered\",\"==\",0]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=4,
                agent_id=None,
                title='Overdue',
                config="{\"filters\": [[\"overdue\",\"==\",1]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=5,
                agent_id=None,
                title='My Tickets',
                config="{\"filters\": [[\"agents.name\",\"in\",[\"Me\"]], [\"ticket_statuses.name\",\"in\",[\"Open\"]]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=6,
                agent_id=None,
                title='Today',
                config="{\"filters\": [[\"created\",\"period\",\"td\"]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=7,
                agent_id=None,
                title='This Week',
                config="{\"filters\": [[\"created\",\"period\",\"tw\"]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=8,
                agent_id=None,
                title='This Month',
                config="{\"filters\": [[\"created\",\"period\",\"tm\"]],\"sorts\": [\"-created\"]}"
            ),
            models.Queue(
                queue_id=9,
                agent_id=None,
                title='This Year',
                config="{\"filters\": [[\"created\",\"period\",\"ty\"]],\"sorts\": [\"-created\"]}"
            )
        ]
        session.add_all(queues_data)
        session.commit()


        default_columns_data = [
            models.DefaultColumn(
                default_column_id=1,
                name='Number',
                primary='number',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=2,
                name='Date Created',
                primary='created',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=3,
                name='Title',
                primary='title',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=4,
                name='User Name',
                primary='user__name',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=5,
                name='Priority',
                primary='ticket_priorities__priority_desc',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=6,
                name='Status',
                primary='ticket_statuses__name',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=7,
                name='Close Date',
                primary='closed',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=8,
                name='Assignee',
                primary='agents__name',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=9,
                name='Due Date',
                primary='due_date',
                secondary='est_due_date',
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=10,
                name='Last Updated',
                primary='updated',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=11,
                name='Department',
                primary='department__name',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=12,
                name='Last Message',
                primary='thread__last_message',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=13,
                name='Last Response',
                primary='thread__last_response',
                secondary=None,
                config='{{}}'
            ),
            models.DefaultColumn(
                default_column_id=14,
                name='Group',
                primary='groups__name',
                secondary=None,
                config='{{}}'
            )
        ]
        session.add_all(default_columns_data)
        session.commit()


        column_id = 1
        for i in range(1, 10):
            session.add(models.Column(
                column_id=column_id,
                queue_id=i,
                default_column_id=1,
                name='Number',
                sort=0,
                width=100
            ))
            session.add(models.Column(
                column_id=column_id + 1,
                queue_id=i,
                default_column_id=3,
                name='Title',
                sort=1,
                width=100
            ))
            session.add(models.Column(
                column_id=column_id + 2,
                queue_id=i,
                default_column_id=10,
                name='Last Updated',
                sort=2,
                width=100
            ))
            session.add(models.Column(
                column_id=column_id + 3,
                queue_id=i,
                default_column_id=5,
                name='Priority',
                sort=3,
                width=100
            ))
            session.add(models.Column(
                column_id=column_id + 4,
                queue_id=i,
                default_column_id=4,
                name='From',
                sort=4,
                width=100
            ))
            column_id += 5
        session.commit()
        
        
        session.add_all([
            models.Settings(namespace='core', key='default_system_email', value=None),
            models.Settings(namespace='core', key='default_alert_email', value=None),
            models.Settings(namespace='core', key='default_admin_email', value=None),
            models.Settings(namespace='core', key='company_name', value=None),
            models.Settings(namespace='core', key='website', value=None),
            models.Settings(namespace='core', key='phone_number', value=None),
            models.Settings(namespace='core', key='address', value=None),
            models.Settings(namespace='core', key='default_dept_id', value='1'),
            models.Settings(namespace='core', key='default_log_level', value='DEBUG'),
            models.Settings(namespace='core', key='default_timezone', value='UTC'),
            models.Settings(namespace='core', key='date_and_time_format', value='Locale Defaults'),
            models.Settings(namespace='core', key='store_attachments', value='s3'),
            models.Settings(namespace='core', key='agent_max_file_size', value='1000000'),
            models.Settings(namespace='core', key='default_ticket_number_format', value='########'),
            models.Settings(namespace='core', key='default_ticket_number_sequence', value='Random'),
            models.Settings(namespace='core', key='default_status_id', value='1'),
            models.Settings(namespace='core', key='default_priority_id', value='2'),
            models.Settings(namespace='core', key='default_sla_id', value='1'),
            models.Settings(namespace='core', key='default_topic_id', value='1'),
            models.Settings(namespace='core', key='lock_semantics', value='Disabled'),
            models.Settings(namespace='core', key='default_ticket_queue', value='1'),
            models.Settings(namespace='core', key='s3_bucket_name', value=None),
            models.Settings(namespace='core', key='s3_bucket_region', value=None),
            models.Settings(namespace='core', key='s3_access_key', value=None),
            models.Settings(namespace='core', key='s3_secret_access_key', value=None),
            models.Settings(namespace='core', key='company_logo', value=None)
            # models.Settings(namespace='core', key='default_page_size', value='25'),
            # models.Settings(namespace='core', key='login_required', value='on'),
            # models.Settings(namespace='core', key='top_level_ticket_counts', value='off'),
            # models.Settings(namespace='core', key='max_open_tickets', value=''),
            # models.Settings(namespace='core', key='human_verification', value='off'),
            # models.Settings(namespace='core', key='collaborator_tickets_visibility', value='off'),
            # models.Settings(namespace='core', key='claim_on_response', value='off'),
            # models.Settings(namespace='core', key='auto_refer_on_close', value='off'),
            # models.Settings(namespace='core', key='require_help_topic_to_close', value='off'),
            # models.Settings(namespace='core', key='allow_external_images', value='off'),
            # models.Settings(namespace='core', key='new_ticket', value='off'),
            # models.Settings(namespace='core', key='new_ticket_by_agent', value='off'),
            # models.Settings(namespace='core', key='new_message_submitter', value='off'),
            # models.Settings(namespace='core', key='new_message_participants', value='off'),
            # models.Settings(namespace='core', key='overlimit_notice', value='off'),
            # models.Settings(namespace='core', key='new_ticket_alert_status', value='enable'),
            # models.Settings(namespace='core', key='new_ticket_alert_admin_email', value='off'),
            # models.Settings(namespace='core', key='new_ticket_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='new_ticket_alert_department_members', value='off'),
            # models.Settings(namespace='core', key='new_ticket_alert_org_manager', value='off'),
            # models.Settings(namespace='core', key='new_message_alert_status', value='enable'),
            # models.Settings(namespace='core', key='new_message_alert_last_respondent', value='off'),
            # models.Settings(namespace='core', key='new_message_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='new_message_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='new_message_alert_org_manager', value='off'),
            # models.Settings(namespace='core', key='new_internal_activity_alert_status', value='disable'),
            # models.Settings(namespace='core', key='new_internal_activity_alert_last_respondent', value='off'),
            # models.Settings(namespace='core', key='new_internal_activity_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='new_internal_activity_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='ticket_assignment_alert_status', value='enable'),
            # models.Settings(namespace='core', key='ticket_assignment_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='ticket_assignment_alert_team_lead', value='off'),
            # models.Settings(namespace='core', key='ticket_assignment_alert_team_members', value='off'),
            # models.Settings(namespace='core', key='ticket_transfer_alert_status', value='disable'),
            # models.Settings(namespace='core', key='ticket_transfer_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='ticket_transfer_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='ticket_transfer_alert_department_members', value='off'),
            # models.Settings(namespace='core', key='overdue_ticket_alert_status', value='enable'),
            # models.Settings(namespace='core', key='overdue_ticket_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='overdue_ticket_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='overdue_ticket_alert_department_members', value='off'),
            # models.Settings(namespace='core', key='system_alerts_system_errors', value='on'),
            # models.Settings(namespace='core', key='system_alerts_sql_errors', value='on'),
            # models.Settings(namespace='core', key='system_alerts_excessive_login_attempts', value='on'),
            # models.Settings(namespace='core', key='default_task_number_format', value='#'),
            # models.Settings(namespace='core', key='default_task_number_sequence', value='Random'),
            # models.Settings(namespace='core', key='default_task_priority', value='Low'),
            # models.Settings(namespace='core', key='new_task_alert_status', value='disable'),
            # models.Settings(namespace='core', key='new_task_alert_admin_email', value='off'),
            # models.Settings(namespace='core', key='new_task_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='new_task_alert_department_members', value='off'),
            # models.Settings(namespace='core', key='new_activity_alert_status', value='disable'),
            # models.Settings(namespace='core', key='new_activity_alert_last_respondent', value='off'),
            # models.Settings(namespace='core', key='new_activity_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='new_activity_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='task_assignment_alert_status', value='disable'),
            # models.Settings(namespace='core', key='task_assignment_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='task_assignment_alert_team_lead', value='off'),
            # models.Settings(namespace='core', key='task_assignment_alert_team_members', value='off'),
            # models.Settings(namespace='core', key='task_transfer_alert_status', value='disable'),
            # models.Settings(namespace='core', key='task_transfer_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='task_transfer_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='task_transfer_alert_department_members', value='off'),
            # models.Settings(namespace='core', key='overdue_task_alert_status', value='disable'),
            # models.Settings(namespace='core', key='overdue_task_alert_assigned_agent', value='off'),
            # models.Settings(namespace='core', key='overdue_task_alert_department_manager', value='off'),
            # models.Settings(namespace='core', key='overdue_task_alert_department_members', value='off'),
        ])
        session.commit()


        templates_data = [
            models.Template(
                code_name='test',
                subject='Test Email',
                body='<p>This is a test email.</p>',
                active=1
            ),
            models.Template(
                code_name='email confirmation',
                subject='Confirm your Account',
                body='<p>Confirm your email <a href="{}">here</a></p>',
                active=1
            ),
            models.Template(
                code_name='reset password',
                subject='Reset your password',
                body='<p>Reset your password <a href="{}">here</a></p>',
                active=1
            ),
            models.Template(
                code_name='user_new_activity_notice',
                subject='New Activity Notice',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_new_message_auto_response',
                subject='New Message Auto-Response',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_new_ticket_auto_reply',
                subject='New Ticket Auto-Reply',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_new_ticket_auto_response',
                subject='New Ticket Auto-Response',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_new_ticket_notice',
                subject='New Ticket Notice',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_overlimit_notice',
                subject='Overlimit Notice',
                body='',
                active=1
            ),
            models.Template(
                code_name='user_response_template',
                subject='Response/Reply Template',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_internal_activity_alert',
                subject='Internal Activity Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_new_message_alert',
                subject='New Message Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_new_ticket_alert',
                subject='New Ticket Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_overdue_ticket_alert',
                subject='Overdue Ticket Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_ticket_assignment_alert',
                subject='Ticket Assignment Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='agent_ticket_transfer_alert',
                subject='Ticket Transfer Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='task_new_activity_alert',
                subject='New Activity Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='task_new_activity_notice',
                subject='New Activity Notice',
                body='',
                active=1
            ),
            models.Template(
                code_name='new_task_alert',
                subject='New Task Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='overdue_task_alert',
                subject='Overdue Task Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='task_assignment_alert',
                subject='Task Assignment Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='task_transfer_alert',
                subject='Task Transfer Alert',
                body='',
                active=1
            ),
            models.Template(
                code_name='ticket_email_confirmation',
                subject='Your Ticket Was Created!',
                body='<p>Your ticket has been successfully created.</p><p></p><p>You can continue to reply to your email or visit our website and search for ticket number {}. Any agent replies will also appear as a reply to your original email.</p>',
                active=1
            ),
            models.Template(
                code_name='guest_ticket_email_confirmation',
                subject='Your Ticket Was Created!',
                body='<p>Your ticket has been successfully created.<br><br><br>Your ticket number is {}. The link below will allow you to log in and check the status of this ticket. If you would like to view all your tickets at once, create an account with the same email you are using now.</p><p><br>{}</p>',
                active=1
            )
        ]
        session.add_all(templates_data)
        session.commit()

    session.close()