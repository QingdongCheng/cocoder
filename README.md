This project is a collaborative online judge website supporting collaborative code editing, compiling, and execution.
This document gives details of the implementation of code editor and code execution.

|Technology | Stack|
| --- | --- |
| Frontend-client | Angular.js, Socket.io |
| Frontend-server | Node.js, Socket.io, Redis, mongoDB |
| Backend-EXECUTOR | Flask, Docker |


1. User can use interactive code editor to edit code. Supported languages are Java and Python. 
   It is capable to add new languages.  
2. Multiple users can edit the same piece of code simultaneously. Each user’s change can be seen and 
   applied to all other user’s code immediately.  
3. User can compile the code by clicking ‘compile’ button. The compile result will be displayed to user. 
4. User can run the code by clicking ‘run’ button. The execution result will be displayed to user. 
5. User can browse pre-stored coding problem list. 
6. User can get details of a specific coding problem by clicking the problem in the list. 
7. User can submit the code through ‘submit’ button to submit the code to solve the chosen question. 
   The result, including compiling and running time, will be displayed to user.
8. Everyone can manually add new problems. (Todo: it's better to set up only admins can add new problems.) 
 


# Collaborative Editor 
Use socket.io as the communication protocol between client and server. 
* Client-server communication is heavy; 
* Full-duplex asynchronous messaging is prefered; 
* WebSockets pass through most firewalls without any reconfiguration. 

# Client-side Editor 
ACE Editor 
A Javascript-based editor for browser and support source code editing. 
It supports multiple languages, color themes, programing APIs for advanced usage. 
We need to dynamically get and change the status of the editor. 
These include getting the change of the content, applying the change to the current content, etc. 
 
ACE has been proven to be a stable editor by adopting by Cloud9 IDE. 
It is easier to get help from community considering the number of users.  
 
Editing Session
Editing session is the concept similar to file. It keeps file content, list of participants, editing history and metadata. 
Multiple users can be in the same editing session, in which case, they work on the same source file simultaneously.  

Users in the same editing session will be synced whenever the source file has been changed. 
In addition, users can see everyone’s cursor position in real time. 

How does the Editor handle collision?
Ace use operational Transformation algorithm to handle the collision. 
Google docs use the same algorithm for synchronisation.
In fact, there are two ways of synchronasation in collabrative editing: 
operational transformation and differential synchronisation.


Editing session will be kept in memory (M) temporarily and stored in Redis (R).  
 
Fast Forwarding Restore It is very natural and common that a new user jumps into an existing session. 
Or, the existing user may leave the editing page then come back later. 
In this scenario, we should resume user’s editing session by restoring the editor content and fast forward to the latest point. 

## Keep All Change Events 
This solution is straightforward
server stores all change events it receives in an ordered list: [event_0, event_1, event_2 … event_n]. 
When a new user joins the editing session, server sends the list of all change events to user. 
User then applies all changes locally to catch up. 
However, this solution is not optimal as the size of events list increases rapidly. 
It will consume a lot of bandwidth and memory. 
 
## Keep Latest Snapshot 
In this solution, server will not keep all events. 
Instead, it keeps a latest snapshot of editor content. 
Behaving like an ACE editor, the server will keep a local copy of editor content and apply changes every time it gets a change event. 
This solution is fast and memory efficient when restoring content for user - just send the snapshot. 
However, it loses the ability to roll back to an old point or “undo” some operations on server side. 
 
## Combine Snapshot and Change Events (Adopted) 
This solution combines the above two. 
Server keeps a snapshot before a certain point (e.g. 1 hour before), and list of change events since that point: 
{snapshot_n, [event_n, event_n+1, 
event_n+2 ...]}. 
This solution limits the size of event list, as well as keep the ability for rolling back.  
 

# User Code Executor 
Users can submit their code through web UI.  
For security reasons, we cannot execute user code directly on server.  
We can utilize   
1. language specific security tool/package: SecurityManager in Java, Pypy in Python etc. 
2. Container technology: Docker etc. 3. Virtual machine: VirtualBox, Vagrant etc. 
 
Here we compare pros /cons of different approaches: 
 
Options   |                           Pros            |               Cons 
--- | --- | ---
Language Specific Tool/Package | Small overhead        |     Need configuration for each language; Need clean up work after the execution
Container Lightweight      |        Quick to initialize    |    Weaker OS isolation
Virtual Machine             |        Complete isolation      |  Slow to initialize
 
Container is an obvious winner if we want to support multiple languages and don’t worry about performance too much.  
