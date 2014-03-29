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

class PlanHearing(Message):
    def __init__(self, metainfo, plan):
        Message.__init__(self, metainfo)
        self.plan = plan
        
    def reaction(self, recipient):
        recipient.plan_hearing_notification(self)
        
    def get_str_summary(self):
        return "Plan distributed with: \n\t" + ", and \n\t".join(
            "%d aquaculture sites" % len(self.plan.aquaculture_sites()),
            "%d reserved zones" % len(self.plan.reserved_zones())
        )

class VoteResponse(Reply):
    def __init__(self, metainfo, plan_hearing, cell, vote):
        Message.__init__(self, metainfo)
        self.plan_hearing = plan_hearing    
        self.cell = cell
        self.vote = vote
        
    def get_cell(self):
        return self.cell
        
    @classmethod
    def reply_to(c, directory, message, cell, vote):
        return c(
            message.metainfo.reply(directory.get_timestamp()),
            message,
            cell,
            vote
        )
        
    def reaction(self, recipient):
        recipient.vote(self)
        
    def get_str_summary(self, world_map, str): 
        return  "Vote approve for cell : (%d, %d)" if \
            self.vote == vote.APPROVE else \
            "Vote COMPLAIN for cell: (%d, %d)" % \
                world_map.get_structure().get_cell_position(
                    self.vote_call.target_message.cell
                )
            
class VoteResponseInform(Reply):
    def __init__(self, metainfo, vote_response):
        Message.__init__(self, metainfo)
        self.vote_response = vote_response
        
    def reaction(self, recipient):
        recipient.vote_response_inform_notification(self)
        
    def get_str_summary(self):
        return "Agent %s voted %s." % (
            self.vote_response.metainfo.sender.get_id(),
            "APPROVE" if self.vote_response.vote == vote.APPROVE \
                else "COMPLAINT"
        )