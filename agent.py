import priority

num_agents_created = 0

class IdentifyingAgent(object):
    _label = None

    def __init__(self):
        global num_agents_created
        num_agents_created += 1
        self._created_number = num_agents_created
        
    def name(self, label):
        self._label = label

    def get_id(self):
        s = "a%02d:%s" % (self._created_number, type(self).__name__)
        if self._label is not None:
            return "%s:%s" % (s, self._label)
        return s
        
class InvalidDirectoryException(Exception): pass

class CommunicatingAgent(IdentifyingAgent):
    _message_log = []
    _directory = None
    
    # Registers the agents to the directory, storing the directory
    # in the agent, and giving its own identifier away to the 
    # directory so it can be looked up later.
    def register(self, directory):
        self._directory = directory
        directory.register_communicating_agent(self)
    
    def get_directory(self):
        if self._directory is not None:
            return self._directory
        raise InvalidDirectoryException("No directory defined for %s." % self.get_id())
        
    def send_message(self, recipient, message):
        self.get_directory().send_message(recipient, message)
        self._message_log.append({
            direction: "sent",
            time: self.get_directory().get_system_time(),
            sender: self.get_id(),
            recipient: recipient,
            contents: message
        })
        
    def receive_message(self, sender, message):
        self._message_log.append({
            direction: "received",
            time: self.get_directory().get_system_time(),
            sender: sender,
            recipient: self.get_id(),
            contents: message
        })
        self.react_to_message(sender, message)        
        
class PrioritizingAgent(object):
    _priorities = {
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
    
    def set_priority(self, p, value):
        try:
            self._priorities[p] = value
        except KeyError:
            # TODO: log
            raise
    
    # Weighted average of priority values
    def get_priorities_satisfaction(self, influences):
        return sum([
            p.calculate_value(influences) * w for 
            p, self._priorities[p] in 
            self._priorities]
            )/len(self._priorities)