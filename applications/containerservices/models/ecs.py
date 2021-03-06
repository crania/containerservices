# -*- coding: utf-8 -*-


class ecs_cluster(object):
    
    def __init__(self,clusterName,status,clusterArn,instances=[]):
        self.clusterName = clusterName
        self.status = status
        self.clusterArn = clusterArn
        self.instances = instances

class ecs_instance(object):
    
    def __init__(self, cluster, status, memory, cpu, ports, instanceId,
                 agentConnected, containerInstanceArn, remainingCPU, 
                 remainingMemory, remainingPorts):
        self.cluster = cluster
        self.status = status
        self.memory = memory
        self.cpu = cpu
        self.ports = ports
        self.instanceId = instanceId
        self.agentConnected = agentConnected
        self.containerInstanceArn = containerInstanceArn
        self.remainingCPU = remainingCPU
        self.remainingMemory = remainingMemory
        self.remainingPorts = remainingPorts
        
        
db.define_table('ecs_task_def',
                Field('name','string'),
                Field('image','string'),
                Field('cpu','integer'),
                Field('memory','integer'),
                Field('links','list:string'),
                Field('portMappings','list:string'),
                Field('essential','boolean'),
                Field('entryPoint','list:string'),
                Field('command','list:string'),
                Field('environment','list:string'),
                Field('mountPoints','list:string'),
                Field('volumesFrom','list:string'),
                format='%(name)s')

db.define_table('ecs_families',
                Field('ecs_family','string'),
                format='%(ecs_family)s')

db.define_table('ecs_registered_tasks',
                Field('ecs_family',db.ecs_families),
                Field('task_definition',db.ecs_task_def)
                )

def get_ecs_registered_task_dict(id):
    import json
    task = db(db.ecs_task_def.id == id).select().first().as_dict()
    
    evarlist = []
    #rewire envirnonment vars
    for evar in task['environment']:
        evarsL = evar.split('@')
        evardict = dict(name=evarsL[0],value=evarsL[1])
        evarlist.append(evardict)
    task['environment'] = evarlist
    #rewrire ports
    portMappingsList = []
    for portmapping in task['portMappings']:
        items = portmapping.split(',')
        item1 = items[0].split(':')
        item2 = items[1].split(':')
        portMappingDict = {item1[0] : int(item1[1]),item2[0] : int(item2[1])}
        portMappingsList.append(portMappingDict)
    task['portMappings'] = portMappingsList

    volumesList = []
    for volume in task['volumesFrom']:
        items = volume.split(',')
        item1 = items[0].split(':')
        item2 = items[1].split(':')
        hostDict = {item2[0] : item2[1]}
        volumesDict = {item1[0] : item1[1], 'host' : hostDict}
        volumesList.append(volumesDict)
    volumes = volumesList
    task['volumesFrom']=[]
    
    mountPointsList = []
    for mountPoint in task['mountPoints']:
        items = mountPoint.split(',')
        item1 = items[0].split(':')
        item2 = items[1].split(':')
        mountPointsDict = {item1[0] : item1[1],item2[0] : item2[1]}
        mountPointsList.append(mountPointsDict)
    task['mountPoints'] = mountPointsList
    
    print task 
    del task['id']
    return task, volumes
    #print json.dumps(task)
    #return json.dumps(task)
    

    
    '''portMappings = '['
    for mapping in task.portMappings:
        portMappings = portMappings + mapping + ','
    portMappings = portMappings + ']'

    environment = '['
    for env in task.environment:
        environment = environment + env + ','
    environment = environment + ']'
    
    jsonString = '['
    jsonString = jsonString + '{"name":"'+ task.name + '", "image":"'+task.image + '","cpu":"' + str(task.cpu) + '", "memory":"' + str(task.memory)+ '","links":[],"portMappings":' + portMappings + ',"essential":"' + str(task.essential).lower() + ',"entryPoint":[], "command":[], "environment'+environment+'"'
    
    
    jsonString = jsonString + ']'
    jsonString = json.loads(jsonString)
    return jsonString
    '''
