import vote

class MetaInfo(object):
    type = "single"

    """Metainfo object for messages.
    
    Contains the source agent, recipient and time of the message.
    
    Attributes:
        source:     An Agent, the sender of the message
        target:     An Agent, the recipient of the message
        timestamp:  An integer representing the the message was sent
        type:       A string indicating that the message has a single recipient.
    """

    def __init__(self, source, target, timestamp=None):
        self.source = source
        self.target = target
        self.timestamp = timestamp
        
    def reply(self, timestamp):
        """Creates a new MetaInfo object for a reply to the message containing
           this MetaInfo instance.
           
        Parameters:
            timestamp:  The time of sending of the new message.
            
        Returns:
            A new MetaInfo object where the new source is the old target, and
            the new target is the old source.
        """
        return MetaInfo(self.target, self.source, timestamp)
        
class BroadcastMetaInfo(MetaInfo):
    type = "broadcast"

    """Broadcast MetaInfo object for broadcasts.
    
    The difference from normal MetaInfo objects is that the target is instead
    a list of targets.
    
    Attributes:
        targets:    A list of agents that will receive the message.
        type:       A string indicating that 
    """
    
    def __init__(self, source, targets, timestamp=None):
        MetaInfo.__init__(self, source, None, timestamp)
        self.targets = targets

class Message(object):
    def __init__(self, metainfo):
        self.metainfo = metainfo
        
    def reaction(self, recipient):
        pass
        
    def get_str_summary(self, world_map):
        raise NotImplementedException()

class Reply(Message):
    reply_to_type = Message

    def __init__(self, metainfo, reply_to):
        assert isinstance(reply_to, self.reply_to_type), "Unexpected type for reply_to."
        Message.__init__(self, metainfo)
        self.reply_to = reply_to

    @classmethod
    def reply_to(c, message, directory):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message
        )

    
### Specific messages

class Inform(Message):
    """General information message containing a string.
    
    Attributes:
        str:        The information string 
    """
    def __init__(self, metainfo, str):
        Message.__init__(self, metainfo)
        self.str = str

    def get_str_summary(self, world_map):
        return self.str
    

class PlanHearing(Message):
    def __init__(self, metainfo, plan):
        Message.__init__(self, metainfo)
        self.plan = plan
        
    def reaction(self, recipient):
        recipient.plan_hearing_notification(self)
        
    def get_str_summary(self, world_map):
        return "Plan distributed with: \n\t" + ", and \n\t".join([
            "%d aquaculture sites" % len(self.plan.aquaculture_sites()),
            "%d reserved zones" % len(self.plan.reserved_zones())
        ])

class VoteResponse(Reply):
    reply_to_type = PlanHearing

    def __init__(self, metainfo, reply_to, votes):
        Reply.__init__(self, metainfo, reply_to)
        self.votes = votes
        
    def reaction(self, recipient):
        recipient.vote(self)
        
    def get_str_summary(self, world_map): 
        approvals = len([v for v in self.votes if v.value == vote.APPROVE])
        complaints = len(self.votes) - approvals
        return  "Vote response with %d complaints and %d approvals" % (complaints, approvals)
            
class VoteResponseInform(Reply):
    reply_to_type = VoteResponse

    def __init__(self, metainfo, reply_to):
        Reply.__init__(self, metainfo, reply_to)
        
    def reaction(self, recipient):
        recipient.vote_response_inform_notification(self)
        
    def get_str_summary(self, world_map):
        return "Agent %s voted: %s." % (
            self.reply_to.metainfo.source.get_id(),
            self.reply_to.get_str_summary(world_map)
        )