
class Queue:

    def __init__(self,lenght):
        self.queue = []
        self.lenght_queue = lenght
        self.converged = False

    def get_queue(self):
        return(self.queue)
    def get_max_lenght(self):
        return(self.lenght_queue)
    def get_converged(self):
        return(self.converged)

    def set_converged(self,value):
        self.converged = value

    def get_queue_lenght(self):
        return(len(self.get_queue()))

    # Function that manages the queue of spectral gaps
    def add_element_to_queue(self,new_element):

        if (self.lenght_queue > self.get_queue_lenght()):
            self.queue.append(new_element)
        elif (self.lenght_queue == self.get_queue_lenght()):
            self.queue.pop(0)
            self.queue.append(new_element)
        else:
            print("ERROR QUEUE LENGHT MUST BE <= LENGHT")