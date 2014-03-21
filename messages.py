import vote

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
    def __init__(self, metainfo, str):
        Message(self, metainfo)
        self.str = str

    def get_str_summary(self):
        return self.str
    
class Reply(Message):
    @classmethod
    def reply_to(c, message, directory):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message
        )

    
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
        
class VoteCall(Message, Reply):
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

class VoteResponse(Message, Reply):
    def __init__(self, metainfo, vote_call, vote):
        Message(self, metainfo)
        self.vote_call = vote_call        
        self.vote = vote
        
    @classmethod
    def reply_to(c, message, directory, vote):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message,
            vote
        )
        
    def reaction(self, recipient):
        recipient.vote(self)
        
    def get_str_summary(self, world_map, str): 
        return  "Vote approve for cell : (%d, %d)" if 
            self.vote == vote.APPROVE else 
            "Vote COMPLAIN for cell: (%d, %d)" % 
                world_map.get_structure().get_cell_position(
                    self.vote_call.target_message.cell
                )
            
class VoteResponseInform(Message, Reply):
    def __init__(self, metainfo, vote_response):
        Message(self, metainfo):
        self.vote_response = vote_response
        
    def reaction(self, recipient):
        recipient.vote_response_inform_notification(self)
        
    def get_str_summary(self):
        return "Agent %s voted %s." % (
            self.vote_response.metainfo.sender.get_id(),
            "APPROVE" if 
                self.vote_response.vote == vote.APPROVE else 
                "COMPLAINT"
        )