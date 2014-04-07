import priority
import messages

num_agents_created = 0

class IdentifyingAgent(object):
    def __init__(self):
        global num_agents_created
        num_agents_created += 1
        self._created_number = num_agents_created
        self._label = None
        
    def name(self, label):
        self._label = label

    def get_id(self):
        s = "a%02d:%s" % (self._created_number, type(self).__name__)
        if self._label is not None:
            return "%s:%s" % (s, self._label)
        return s

class CommunicatingAgent(IdentifyingAgent):
    # Registers the agents to the directory, storing the directory
    # in the agent, and giving its own identifier away to the 
    # directory so it can be looked up later.
    def register(self, directory, type=None, voting=False):
        self._directory = directory
        self._message_log = []
        directory.register_communicating_agent(self, type, voting)
    
    def get_directory(self):
        assert self._directory is not None, \
            "No directory defined for %s." % self.get_id()
        return self._directory
        
    def send_message(self, recipient, message):
        self.get_directory().send_message(message)
        self._message_log.append({
            "direction": "sent",
            "time": self.get_directory().get_system_time(),
            "sender": self.get_id(),
            "recipient": message.metainfo.target,
            "contents": message
        })        
        
    def broadcast_message(self, message):
        self.get_directory().broadcast_message(message)
        
    def receive_message(self, sender, message):
        self._message_log.append({
            "direction": "received",
            "time": self.get_directory().get_system_time(),
            "sender": sender,
            "recipient": self.get_id(),
            "contents": message
        })
        message.reaction(self)        
        
class VotingAgent(CommunicatingAgent):
    def decide_vote(self, target_message):
        raise NotImplementedException        
        
    def vote_call_notification(self, message):
        self._areas_threatened.add(message.target_message.cell)
        decision = self.decide_vote(message.target_mesasge)
        self.send_message(
            self.directory.get_government(),
            messages.VoteResponse.reply_to(
                message, 
                self.get_directory(),
                decision
        ))
        
class WorkingAgent(object):
    def work(self):
        raise NotImplementedException()
        
class PrioritizingAgent(object):
    def __init__(self):
        self._priorities = {
            priority.OwnProfits:                    0.0,
            priority.CommunityWealth:               0.0,
            priority.SalmonPrice:                   0.0,
            priority.WildFishPrice:                 0.0,
            priority.FishingIndustryExisting:       0.0,
            priority.NaturalFishHealth:             0.0,
            priority.AquacultureIndustryExisting:   0.0,
            priority.NonintrusiveAquaculture:       0.0,
            priority.PopulationHappiness:           0.0        
        }
    
    def set_priorities(self, p):
        self._priorities = p
    
    # Weighted average of priority values
    def get_priorities_satisfaction(self, influences):
        s = 0.0
        t = 0.0
        #print "Priorities for %s" % str(self.get_id())
        for p in self._priorities:
            w = self._priorities[p]
            value = p.calculate_value(influences)
            #print "\t%s: %f" % (p.name, value)
            s += value * w
            t += w
        return s / t