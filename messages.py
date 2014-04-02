import vote

class MetaInfo(object):
    """Metainfo object for messages.
    
    Contains the source agent, recipient and time of the message.
    
    Attributes:
        source:     An Agent, the sender of the message
        target:     An Agent, the recipient of the message
        timestamp:  An integer representing the the message was sent
    """

    def __init__(self, source, target, timestamp):
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

class Message(object):
    def __init__(self, metainfo):
        self.metainfo = metainfo
        
    def reaction(self):
        raise NotImplementedException()
        
    def get_str_summary(self, world_map):
        raise NotImplementedException()

class Reply(Message):
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
        Message(self, metainfo)
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
    def __init__(self, metainfo, plan_hearing, cell, vote):
        Message.__init__(self, metainfo)
        self.plan_hearing = plan_hearing    
        self.cell = cell
        self.vote = vote
        
    def get_cell(self):
        return self.cell
        
    @classmethod
    def reply_to(c, message, directory, cell, vote):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message,
            cell,
            vote
        )
        
    def reaction(self, recipient):
        recipient.vote(self)
        
    def get_str_summary(self, world_map): 
        return  ("Vote approve for cell : (%d, %d)" if \
            self.vote == vote.APPROVE else \
            "Vote COMPLAIN for cell: (%d, %d)") % \
                world_map.get_structure().get_cell_position(
                    self.cell
                )
            
class VoteResponseInform(Reply):
    def __init__(self, metainfo, vote_response):
        Message.__init__(self, metainfo)
        self.vote_response = vote_response
        
    def reaction(self, recipient):
        recipient.vote_response_inform_notification(self)
        
    def get_str_summary(self, world_map):
        return "Agent %s voted %s." % (
            self.vote_response.metainfo.source.get_id(),
            "APPROVE" if self.vote_response.vote == vote.APPROVE \
                else "COMPLAINT"
        )