#!/usr/bin/env python
"""The Net1 P2P client."""

import starter
import argparse
import select
import socket
import struct
import sys
import json

## message types ##
GETPEERLIST = 3
PEERLIST = 4
ADVERT = 5
GETCHUNKLIST = 6
CHUNKLIST = 7
GETCHUNK = 8
CHUNK = 9

def main():
    """Our main function. Put your code here."""
    args = parse_args() 
    userPort = args.p
    trackerPort = args.r
    CONNECTIONS = 5
    userPeer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    userHost = args.b
    trackerHost = args.t
    ADDRESS = (userHost, userPort)
    TRACKER = (trackerHost, trackerPort)
    userPeer.bind(ADDRESS)    
    userPeer.listen(CONNECTIONS)
    userPeer.setblocking(0)    
    TRANSMITSIZE = 4096
    running = 1
    VERSION = 1
    messageType = 0
    messageLength = 0
    listOfPeers = [ADDRESS]
    userPeerSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    outputs = []
    errors = []
    
    input = [userPeer, sys.stdin]

    protocolHeader = struct.pack("!BBH", VERSION, messageType, messageLength)
    ## chunkHeader = 

    if trackerPort is not None and trackerHost is not None:
        userPeerSend.connect((trackerHost, trackerPort))
        messageLenth = 0
        protocolHeader = struct.pack("!BBH", VERSION, GETPEERLIST, messageLength)
        userPeerSend.send(protocolHeader)
        data = userPeerSend.recv(TRANSMITSIZE)
        for s in json.loads(data[4:]):
            listOfPeers.append(tuple(s))                                              
        protocolHeader = struct.pack("!BBH", VERSION, ADVERT, len(ADDRESS))
        advertiseSelf = json.dumps(ADDRESS)
        userPeerSend.send(protocolHeader + advertiseSelf)
        
        print listOfPeers

        
    
    while running:
        inputReady, outputReady, exceptionReady = select.select(input, outputs, errors)
         
    
        for connectedPeer in inputReady:
            if connectedPeer == userPeer:
                ## handle the server socket
                clientPeer, address = userPeer.accept()
                input.append(clientPeer)

            elif connectedPeer == sys.stdin:
                ## handle standard input
                junk = sys.stdin.readline()
                running = 0

            else:
                ## handle all other sockets
                dataReceived = connectedPeer.recv(TRANSMITSIZE)
                if dataReceived:
                    receivedVersion, receivedMessageType, receivedLength = struct.unpack("!BBH", dataReceived[:4])
                    if dataReceived[4:]:
                        receivedPayload = dataReceived[4:]
                    if receivedVersion == 1:
                        
                        if receivedMessageType == GETPEERLIST:
                            ## Peer makes a request for peerlist, send peer list
                            protocolHeader = struct.pack("!BBH", VERSION, PEERLIST, len(listOfPeers))
                            payload = json.dumps(listOfPeers)
                            connectedPeer.send(protocolHeader + payload)
                            print ('Received Request for Peerlist')
                           
                        elif receivedMessageType == PEERLIST:
                            ## Updates the list of peers after making a request for a peer list
                            addPeer = tuple(json.loads(receivedPayload))                                              
                            listOfPeers.append(addPeer)
                            print (listOfPeers)
                            
                        
                        elif receivedMessageType == ADVERT:
                            ## Adds a advertised peer to the list of peers
                            print "Adding peer..."
                            addPeer = tuple(json.loads(receivedPayload))                                              
                            listOfPeers.append(addPeer)
                            print (listOfPeers)

                    else:
                        print 'wrong version'
                        
                else:
                    connectedPeer.close()
                    input.remove(connectedPeer)
                    
    
    print listOfPeers
    print args.b, args.p
    userPeer.close()
    

def parse_args():
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(description="NetI P2P Network")
    parser.add_argument('-b', help="Local bind IP", required=True)
    parser.add_argument('-p', help="Local bind port", required=True, type=int)
    parser.add_argument('-t', help="IP of tracker")
    parser.add_argument('-r', help="Port of tracker", type=int)
    parser.add_argument('-f', help="Name of file to seed")
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    main()
