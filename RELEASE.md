1.2.1 [Jun 23rd, 2020]:
---
 * Now the dispatcher runs the check commands before running an executor
 * Fix error when connects with faraday fails when trying to access with SSL to not SSL server
 * Fix error when connects with faraday fails when server does not respond
 * Fix error when connects with faraday fails when SSL verification fails
 * Fix error attempting to create an executor with a comma in the name
 * Now the wizard ask if you want use the default SSL behavior
 * Started the process of [documentation][doc]
 * The new official executors are:  
    * arachni
    * openvas
    * zap
 * Nmap executor now acepted multi target
 * Fix W3af executor now uses python2
 * Escape user-controlled executor parameters in order to prevent OS argument injection (not command injection)
 * [Faraday][faraday] versions: 3.11, 3.11.1

1.2 [May 27th, 2020]:
---
 * Now we have official executors, packaged with the dispatcher
 * Fix error when killed by signal
 * Fix error when server close connection
 * Fix error when ssl certificate does not exists
 * Fix error when folder `~/.faraday` does not exists, creating it
 * The new official executors are:  
    * nessus
    * nikto
    * nmap
    * sublist3r
    * wpscan
    * w3af
 * [Faraday][faraday] versions: 3.11, 3.11.1

1.1 [Apr 22th, 2020]:
---
 * The dispatcher now runs with a `faraday-dispatcher run` command
 * `faraday-dispatcher wizard` command added which generates configuration .ini file
 * Manage execution_id within WS and API communication
 * The route of [Faraday][faraday] ws comunication change from / to /websockets
 * Better error management, now shows error and exceptions depending on log levels
 * Better management of invalid token errors
 * Add ssl support
 * [Faraday][faraday] versions: 3.11, 3.11.1

1.0 [Dec 17th, 2019]:
---
 * You can add fixed parameters than shouldn't came by the web (e.g. passwords) are set in the dispatcher.ini
 * Now its possible to manage multiple executors within one agent
 * Now is possible to receive params from the [Faraday][faraday] server
 * [Faraday][faraday] versions: 3.10, 3.10.1, 3.10.2

0.1 [Oct 31th, 2019]:
---
 * First beta version published 
 * Basic structure implemented, with executor with fixed values
 * [Faraday][faraday] versions: 3.9.2, 3.9.3

[faraday]: https://github.com/infobyte/faraday
[doc]: https://infobyte.github.io/faraday_agent_dispatcher/
