#/bin/bash
######################################################
# Don't forget <<chmod +x start.sh>>                 #
# Tiago Barros 88963                                 #
######################################################



gnome-terminal --tab --title="server" -- /bin/bash -c "source ./venv/bin/activate && python3 server.py;" & 
gnome-terminal --tab --title="viewer" -- /bin/bash -c "source ./venv/bin/activate && python3 viewer.py;" & 
sleep 0.5
gnome-terminal --tab --title="student" -- /bin/bash -c "source ./venv/bin/activate && python3 student.py;" &
