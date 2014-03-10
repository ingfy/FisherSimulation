class MetaInfo(object):
    def __init__(self, source, target, timestamp):
        self.source = source
        self.target = target
        self.timestamp = timestamp
        
    def reply(self, timestamp):
        return MetaInfo(self.target, self.source, timestamp)

class Message(object):
    def __init__(self, metainfo):
        self.metainfo = metainfo

class Inform(Message):
    pass

class DeclareIntention(Inform):
    pass
    
class Request(Message):
    pass
    
### Specific messages

class TargetArea(DeclareIntention):
    def __init__(self, metainfo, cell):
        Message(self, metainfo)
        self.cell = cell
        
class Complaint(Inform):
    def __init__(self, metainfo, target_message):
        Message(self, metainfo)
        self.target_message = target_message
        
class Vote(Inform):
    def __init__(self, metainfo, target_message, complaints):
        Message(self, metainfo)
        self.target_message = target_message
        self.complaints = complaints

class VoteResponse(Inform):
    def __init__(self, metainfo, vote):
        Message(self, metainfo)
        self.vote = vote
        
class VoteBuild(VoteResponse):
    pass
    
class VoteDontBuild(VoteResponse):
    pass