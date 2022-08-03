#Jesus Ugarte
#Airtime TCP transmission Challenge
from functools import reduce
import socket as sock
import collections

#Get Value from a big-endian bytearray (Most Significant Value of Byte Arr)
def get_big_endian_value(byte_ar):
    return int(reduce(lambda x, y: x | y,
                      [x << i * 8 for i, x in enumerate(byte_ar[::-1])]))

#CheckSum Computation to Detect errors in Data
def checksum(seq, data):
    for i in range(0, len(data) - 3, 4):
        chunk = data[i:i + 4]
        seq = bytearray([(seq[j] ^ chunk[j]) & 0xFF for j in range(4)])
    leftovers = len(data) % 4 #If Mutiple of 4, go ahead and assign leftover
    if leftovers:
        lastchunk = bytearray(data[-(leftovers):])
        # Assign 0xAB for every single empty bytearray from the last chunks
        lastchunk += bytearray([0xAB for i in range(4 - leftovers)]) 
        seq = bytearray([(seq[j] ^ lastchunk[j]) & 0xFF for j in range(4)])
    return seq

#Stream Function
def tcp_stream():

    ADDRESS = ("challenge2.airtime.com", 2323)
    EMAIL = "jesusugarte10@gmail.com"

    #TCP HandShake Portion
    socket = sock.create_connection(ADDRESS)
    handshake = socket.recv(4096).decode("utf-8")
    challenge = handshake[handshake.find(":") + 1:].strip()
    socket.send(f"IAM:{challenge}:{EMAIL}:at\n".encode('utf-8'))
    success = socket.recv(4096)
    if not success:
        print("Unable to Stablish Connection")
        return

    # Initializing DISCT tructure to store chunks of data
    chunks = {}

    #writting  PCM in write binary mode
    with open("data.pcm", "wb") as file_obj:
        data = bytearray(socket.recv(2048))
        while data:
            SEQ = data[:4]
            sequence_number = get_big_endian_value(SEQ)
            CHK = data[4:8]
            LEN = data[8:12]
            length = get_big_endian_value(LEN)
            PCM_CONTENT = data[12:12 + length]
            computed_checksum = checksum(SEQ, PCM_CONTENT)

            # If the checksum matches append PCM Content into dhe chunk Dictionary
            # At the index of the sequence number given by the big endian Value
            if computed_checksum == CHK:
                chunks[sequence_number] = PCM_CONTENT
                
            # Slice data to start of next packet and add new data if it exists.
            data = data[12 + length:]
            data += bytearray(socket.recv(2048))

            # Sort the ordered chunks, Time Complexity O(n log n) average
            ordered_chunks = collections.OrderedDict(sorted(chunks.items(),
                                                            key=lambda t: t[0]))
        
        #write in file the bynary Time Complexity O(n)
        for i in ordered_chunks:
            file_obj.write(ordered_chunks[i])

    socket.close()

tcp_stream()