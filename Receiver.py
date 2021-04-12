from socket import *
import time
import random

def time2float(t_val):
    return "%.3f" % float(t_val)


packet_loss_rate = float(input('packet loss probability: '))

receiver_sock = socket(AF_INET, SOCK_DGRAM)
receiver_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

buf = receiver_sock.getsockopt(SOL_SOCKET, SO_RCVBUF)
print('socket recv buffer size: ', buf)
if int(buf) != 10000000:
    receiver_sock.setsockopt(SOL_SOCKET, SO_RCVBUF, 10000000)
print('socket recv buffer size updated: ', receiver_sock.getsockopt(SOL_SOCKET, SO_RCVBUF))

receiver_sock.bind(('', 10080))
print('The server is ready to receive')

def is_pkt_drop(val):
    num = random.randrange(1, 101)
    if num <= int(val*100):
        return True
    else:
        return False


last_ACK = 0

pkt_recv, addr = receiver_sock.recvfrom(1471)
data = pkt_recv
filename = pkt_recv
f = open(filename, 'wb')
total_N, addr = receiver_sock.recvfrom(1471)
for i in range(0, int(total_N)+1):
    pkt_recv, addr = receiver_sock.recvfrom(1471)
    data = pkt_recv

    start_time = time.time()
    print(time2float(time.time() - start_time), ' pkt: ', "%5s" % str(last_ACK), ' Receiver < Sender')
    if (is_pkt_drop(packet_loss_rate)):
        print(time2float(time.time() - start_time), ' pkt: ', "%5s" % str(last_ACK), ' | Dropped')
    else:
        f.write(data)
        receiver_sock.sendto(str(last_ACK).encode(), addr)
        print(time2float(time.time() - start_time), ' ACK: ', "%5s" % str(last_ACK), ' Receiver > Sender')
        last_ACK += 1

f.close
print("\nfile transmitted successfully")