# Python connection to Qsys 
## Summary
<p> this repo is to have proof of concept to send and receive data between a python app and a qsys design.</p>
<p> currently this is only set up to receive changes from a qsys design and only on a single gain block. There is no front end at this point. Eventually this will connect to a vue front end and have full control over the qsys design with any component that has QRC access.</p>

## To Run
- install dependencies
    - pip install -r requirements.txt
- run python -m pyqsys.client

## TODO
1. Need to keep connection alive. 
2. Get all available components
    - separate them into groups
        - audio
        - video
        - control
    - create a change group for each type of component
3. Connect the front end vue app via websocket
    - vue app should live on the system pc as the python app