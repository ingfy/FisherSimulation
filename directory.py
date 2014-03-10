import entities

class Directory(object):
    def __init__(self):
        self._catalogue = []
        self._log = []
        self._messages_sent = 0   
    
    def send_message(self, sender, recipient, message):
        if recipient in self._catalogue:
            recipient.recieve_message(sender, recipient, message)
            self._log.append({
                sender: sender,
                recipient: recipient,
                contents: message,
                time: self.get_system_time()
            })
            #interface.message_sent(sender, recipient, message, self.get_system_time())
            self._messages_sent += 1
        
    def register_communicating_agent(self, agent, type):
        self._catalogue.append((agent, type))
        
    def get_agents(self, type=None):
        if type is None:
            return [a for a, _ in self._catalogue]        
        return [a for a, t in self._catalogue if t == type]
        
    def get_government(self):
        govs = self.get_agents(type = entities.Government)        
        assert len(govs) == 1, "Unexpected number of governments: %d" % len(govs)        
        return govs[0]
         
    def get_system_time(self):
        return self._messages_sent