import entities

class Directory(object):
    def __init__(self):
        self._catalogue = []
        self._log = []
        self._messages_sent = 0   
        self._live_print_messages = False
        self._recording = None
        
    def start_recording(self):
        self._recording = len(self._log)
        
    def stop_recording(self):
        assert self._recording is not None, "No recording ongoing"
        recording = self._log[self._recording:]
        self._recording = None
        return recording
        
    def in_catalogue(self, agent):
        return agent in [a for a, _, __ in self._catalogue]
    
    def send_message(self, sender, recipient, message):
        if self.in_catalogue(recipient):
            if self._live_print_messages:
                print message
            recipient.receive_message(sender, message)
            self._log.append(message)
            self._messages_sent += 1
        
    def register_communicating_agent(self, agent, type, voting=False):
        self._catalogue.append((agent, type, voting))
        
    def get_voting_agents(self):
        return self.get_agents(only_voters=True)        
        
    def get_agents(self, type=None, exclude=None, only_voters=False, 
            predicate=None):
        return [a for a, t, v in self._catalogue if 
            (type is None or t == type) and 
            (exclude is None or not a == exclude) and
            (not only_voters or v) and
            (predicate is None or predicate(a))
        ]
        
    def get_municipality(self):
        muns = self.get_agents(type = entities.Municipality)
        assert len(muns) == 1, \
            "Unexpected number of municipalities: %d" % len(muns)
        return muns[0]
        
    def get_government(self):
        govs = self.get_agents(type = entities.Government)        
        assert len(govs) == 1, \
            "Unexpected number of governments: %d" % len(govs)        
        return govs[0]
        
    def get_timestamp(self):
        return self.get_system_time()
         
    def get_system_time(self):
        return self._messages_sent