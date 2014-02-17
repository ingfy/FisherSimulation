class Directory(object):
    _catalogue = []
    log = []
    messages_sent = 0   
    
    def send_message(self, sender, recipient, message):
        if recipient in self._catalogue:
            recipient.recieve_message(sender, recipient, message)
            log.append({
                sender: sender,
                recipient: recipient,
                contents: message,
                time: self.get_system_time()
            })
            #interface.message_sent(sender, recipient, message, self.get_system_time())
            messages_sent += 1
        
    def register_communicating_agent(self, agent, type):
        self._catalogue.append((agent, type))
        
    def get_agents(self, type=None):
        if type is None:
            return [a for a, _ in self._catalogue]        
        return [a for a, t in self._catalogue if t == type]
         
    def get_system_time(self):
        return self.messages_sent