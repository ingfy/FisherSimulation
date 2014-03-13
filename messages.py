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
        
    def reaction(self):
        raise NotImplementedException()

class Inform(Message):
    pass
    
class Reply(Message):
    @classmethod
    def reply_to(c, message, directory):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message
        )

class DeclareIntention(Inform):
    pass
    
class Request(Message):
    pass
    
### Specific messages

class TargetArea(DeclareIntention):
    def __init__(self, metainfo, cell):
        Message(self, metainfo)
        self.cell = cell
        
    def reaction(self, recipient):
        recipient.target_notification(self)
        
    def get_str_summary(self, world_map):
        return "Cell targeted at: (%d, %d)" % 
            world_map.get_structure().get_cell_position(self.cell)
        
class VoteCall(Inform, Reply):
    def __init__(self, metainfo, target_message):
        Message(self, metainfo)
        self.target_message = target_message
        
    def reaction(self, recipient):
        recipient.vote_call_notification(self)
        
    def get_str_summary(self, world_map):
        return "Call for vote targeted at: (%d, %d)" %
            world_map.get_structure().get_cell_position(
                self.target_mesasge.cell
            )

class VoteResponse(Inform, Reply):
    def __init__(self, metainfo, vote_call):
        Message(self, metainfo)
        self.vote_call = vote_call        
        
    def _get_str_summary(self, world_map, str): 
        return str % world_map.get_structure().get_cell_position(
                self.vote_call.target_message.cell
            )
        
class VoteBuild(VoteResponse):
    def reaction(self, recipient):
        recipient.vote_build_notification(self)

    def get_str_summary(self, world_map):
        self._get_str_summary(world_map,
            "Vote build for cell targeted at: (%d, %d)"
        )
    
class VoteDontBuild(VoteResponse):
    def reaction(self, recipient):
        recipient.vote_dont_build_notification(self)

    def get_str_summary(self, world_map):
        self._get_str_summary(world_map,
            "Vote DON'T build for cell targeted at: (%d, %d)"
        )