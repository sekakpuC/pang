* The Classic Game "Pang"
  * pang_client
  * pang_server at port 2345
  * pang_web at port 80

* How to run
  * server
    * python -V  // expect 3.8.x
    * python -m venv venv
    * call venv\scripts\activate
    * pip install -r requirements.txt
    * python init_db.py
    * python pang_server_main.py
    * python pang_web_main.py
  * client
    * python -V  // expect 3.8.x  
    * python -m venv venv
    * call venv\scripts\activate
    * pip install -r requirements.txt
    * python pang_client_main.py

* Requirements
  * Python 3.8
  
* Technical stacks
  * pang_client
    * Python 3.8
    * pygame framework
    * TCP socket client
  * pang_server
    * Multi-threaded TCP server
    * SQLite 3 DB
  * pang_web
    * Flask framework
    * SQLite 3 DB
    * Mobile friendly web leaderboard      
