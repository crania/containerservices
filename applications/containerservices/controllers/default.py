# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################
import boto3
import json

try:
    thisSession = boto3.session.Session(aws_access_key_id=session.aws_key,aws_secret_access_key=session.aws_secret_key,region_name=session.aws_region)
    CS = thisSession.client('ecs')
    session.aws_secret_key

except:
    CS = boto3.client('ecs')

def accounts():
    form = SQLFORM.grid(db.accounts)
    return locals()

def current_session():
    session.asdf = 'asdf'
    form = SQLFORM.factory(
        Field('account', db.accounts, requires = IS_IN_DB(db,db.accounts.id,'%(description)s')),
        )
    if form.process().accepted:
        
        session.aws_account = form.vars.account
        accountvars = db(db.accounts.id == form.vars.account).select().first()
        session.aws_key = accountvars.aws_key
        session.aws_secret_key = accountvars.aws_secret_key
        session.aws_region = accountvars.region
        print session.aws_account, session.aws_key, session.aws_secret_key
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)

def index():
    #print session.asdf 
    ecs_clusters = []
    #CS = boto3.client('ecs')
    #CS.create_cluster()
    #CS.register_container_instance()
    clusters= CS.describe_clusters()
    print clusters
    for cluster in clusters['clusters']:
        #print cluster['clusterName']
        thisCluster = ecs_cluster(clusterName =cluster['clusterName'],status=cluster['status'],
                    clusterArn=cluster['clusterArn'])
        task_definitions_for_cluster = CS.list_tasks(cluster=cluster['clusterArn'])
        instances = CS.list_container_instances(cluster=cluster['clusterArn'])
        for instance_arn in instances['containerInstanceArns']:
            print instance_arn
            instance = CS.describe_container_instances(containerInstances=[instance_arn])
            print instance
            instance_details = instance['containerInstances'][0]
            registered_resources = instance_details['registeredResources']
            #print registered_resources
            for resource in registered_resources:
                print resource
                if resource['name']=='CPU':
                    cpu = resource['integerValue']
                elif resource['name']=='MEMORY':
                    memory = resource['integerValue']
                elif resource['name']=='PORTS':
                    ports = resource['stringSetValue']

            remaining_resources = instance_details['remainingResources']
            #print registered_resources
            for resource in remaining_resources:
                print resource
                if resource['name']=='CPU':
                    remainingCPU = resource['integerValue']
                elif resource['name']=='MEMORY':
                    remainingMemory = resource['integerValue']
                elif resource['name']=='PORTS':
                    remainingPorts = resource['stringSetValue']


            thisInstance = ecs_instance(cluster='default', status=instance_details['status'], memory=memory, cpu=cpu,
                         ports='', instanceId=instance_details['ec2InstanceId'],
                         agentConnected=instance_details['agentConnected'],
                         containerInstanceArn=instance_details['containerInstanceArn'], 
                         remainingCPU=remainingCPU, remainingMemory=remainingMemory, remainingPorts=remainingPorts)
            thisCluster.instances.append(thisInstance)
        ecs_clusters.append(thisCluster)
    task_definitions_families = CS.list_task_definition_families()
    task_definitions = CS.list_task_definitions()
    print instances
    response.flash = T("Welcome to web2py!")
    return dict(clusters=ecs_clusters,instances=instances)#,tdf=task_definitions_families,td=task_definitions,lt=task_definitions_for_cluster)

def task_definitions():
    form = SQLFORM.grid(db.ecs_task_def)
    return locals()

def families():
    form = SQLFORM.grid(db.ecs_families)
    return locals()

def register_task():
    
    form = SQLFORM(db.ecs_registered_tasks)
    if form.accepts(request,session):
        #CS = boto3.client('ecs')
        family = db(db.ecs_families.id==request.post_vars.ecs_family).select().first()['ecs_family']
        task, volumes = get_ecs_registered_task_dict(request.post_vars.task_definition)
        print family
        print task
        CS.register_task_definition(containerDefinitions=[task], family=family, volumes=volumes)
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    #CS = boto3.client('ecs')
    return dict(form=form)

def printTask():
    print get_ecs_registered_task_json(1)
    return dict(a='b')
    
def list_registered_tasks():
    #CS = boto3.client('ecs')
    #CS.deregister_task_definition(taskDefinition='arn:aws:ecs:us-west-2:181873281313:task-definition/avh2ours:1')
    #CS.run_task(taskDefinition='arn:aws:ecs:us-west-2:181873281313:task-definition/theleansalesforce:2')
    tasks = CS.list_task_definitions()
    print tasks
    tasksList = []
    for task in tasks['taskDefinitionArns']:
        tasksList.append(CS.describe_task_definition(taskDefinition=task))
        
    return dict(m=tasksList)

def run_reg():
    a = CS.run_task(taskDefinition='arn:aws:ecs:us-east-1:181873281313:task-definition/avh2ours:4')
    print a
    return dict(a=a)

#def run_all_registered_tasks():
    #CS = boto3.client('ecs')
#    tasks =  CS.list_task_definitions()
#    notices = []
#    for task in tasks['taskDefinitionArns']:
#        notices.append(CS.run_task(taskDefinition=task))
#    return notices
        
        
def list_tasks():
    #CS = boto3.client('ecs')
    CS.stop_task(task='arn:aws:ecs:us-east-1:181873281313:task/7fa6e056-4feb-4bbc-b6c3-2f47aa439d62')
    CS.stop_task(task='arn:aws:ecs:us-east-1:181873281313:task/d86b10a8-fb40-48eb-9c62-806b4dcd2338')
    a=CS.list_tasks()
    
    describedtasks =[]
    print a
    for b in a['taskArns']:
        print b
        b = CS.describe_tasks(tasks=[b])
        describedtasks.append(b)
    return dict(a=a,dt=describedtasks)
        
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
