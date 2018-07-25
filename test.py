from queue import Queue


out_msg = Queue()

tes = {'Al': 'text'}
out_msg.put(tes)

na = out_msg.get()
name, data = na.popitem()
print(name)
print(data)