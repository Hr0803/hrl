from socket import *
import time
import select

receiverIP = input("IP address of receiver: ")
window_size = int(input("window size: "))
timeout_sec = float(input("timeout second: "))
file_name = input("file name: ")

f = open(file_name, 'rb')
if f.__sizeof__() % 1471 == 0:
    total_N = int(f.__sizeof__() / 1471)
else:
    total_N = int(f.__sizeof__() / 1471 + 1)


sender_sock = socket(AF_INET, SOCK_DGRAM)
sender_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sender_sock.bind(('', 0))

sender_sock.sendto(file_name.encode(), (receiverIP, 10080))
sender_sock.sendto(str(total_N).encode(), (receiverIP, 10080))


last_ACK = -1
window_base = 0

is_sended_pkt = list()
is_get_ACK = list()
timers_pkt = list()
time_recv = list()

def set_time(val):
    return "%7s" % ("%.3f" % float(val))

for i in range(0, int(total_N)):
    is_sended_pkt.append(False)
    is_get_ACK.append(False)
    timers_pkt.append(0.000)
    time_recv.append(0.000)

input_list = [sender_sock]
start_time = time.time()

for i in range (0, total_N):
    timer_index = last_ACK + 1
    for i in range(window_base, window_base + window_size):
        data = f.read(1471)
        sender_sock.sendto(data, (receiverIP, 10080))
        sender_sock.sendto(str(i).encode(), (receiverIP, 10080))
        if is_sended_pkt[i] == True:
                timers_pkt[i] = time.time() - start_time
                print(set_time(timers_pkt[i]), ' pkt: ', "%5s" % str(i), ' Sender > Receiver retransmission')
        else:
            timers_pkt[i] = time.time() - start_time
            is_sended_pkt[i] = True
            print(set_time(timers_pkt[i]), ' pkt: ', "%5s" % str(i), ' Sender > Receiver')

while(last_ACK != total_N -1):
    input_ready, write_ready, except_ready = select.select(input_list, [], [], 0.00001)
    if len(input_ready) == True:
        ACK_recv, addr = sender_sock.recvfrom(1024)
        ACK_recv = ACK_recv.decode()
        time_recv[int(ACK_recv)] = time.time() - start_time
        print(set_time(time_recv[int(ACK_recv)]), ' ACK: ', "%5s" % ACK_recv, 'Sender < Receiver')
        if ACK_recv == str(last_ACK + 1):
            is_get_ACK[int(ACK_recv)] = True
            last_ACK += 1
            timer_index += 1

            if int(ACK_recv) < total_N - window_size:
                sender_sock.sendto(str(int(ACK_recv)+ window_size).encode(), addr)
                is_sended_pkt[int(ACK_recv) + window_size] = True
                send_time = timers_pkt[int(ACK_recv) + window_size] = time.time() - start_time
                print(set_time(send_time), ' pkt: ', "%5s" % str(int(ACK_recv) + window_size), ' Sender > Receiver')
                window_base += 1
        else:
            if(timer_index != total_N):
                ret_timeout = float(time.time() - start_time - timers_pkt[timer_index])
                if is_get_ACK[timer_index] == False and ret_timeout > timeout_sec:
                    print(set_time(time.time() - start_time), ' pkt: ', "%5s" % str(timer_index), ' | timeout Since', set_time(timers_pkt[timer_index]))
                    break


f.close()

transfer_time = set_time(time.time() - start_time)
print((total_N / float(transfer_time)), " pkts / sec")


















