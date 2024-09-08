# USER = pi
# ADDRESS = 127.0.0.1
USER = hungnp
ADDRESS = 192.168.1.17
SHAREPOINT_ADDRESS = 192.168.1.8
SHAREPOINT = /app2
MOUNTPOINT = /mnt/app2
APP = main.py
DEBUG_PORT = 5678
PUBLIC_PORT = 8000

syncResource:
	# Do share the target folder from windows first.. do it manually !!
	ssh $(USER)@$(ADDRESS) "sudo -S mkdir -p $(MOUNTPOINT)"
	ssh $(USER)@$(ADDRESS) "sudo -S mount -t cifs -o username=hungnp,password=q123,file_mode=0777,dir_mode=0777 //$(SHAREPOINT_ADDRESS)$(SHAREPOINT) $(MOUNTPOINT)"

installDependencies:
	ssh $(USER)@$(ADDRESS) "sudo -S chmod +x $(MOUNTPOINT)/installDependencies.sh"
	ssh $(USER)@$(ADDRESS) "cd $(MOUNTPOINT)/ && sudo ./installDependencies.sh"

removeDependencies:
	ssh $(USER)@$(ADDRESS) "sudo -S chmod +x $(MOUNTPOINT)/removeDependencies.sh"
	ssh $(USER)@$(ADDRESS) "cd $(MOUNTPOINT)/ && sudo ./removeDependencies.sh"

debug:
	ssh -L $(DEBUG_PORT):localhost:$(DEBUG_PORT) -L $(PUBLIC_PORT):localhost:$(PUBLIC_PORT) $(USER)@$(ADDRESS) "sudo DISPLAY=:10 python $(MOUNTPOINT)/$(APP) --debug" || true

manualProfiling:
	# TODO

clean:
	ssh $(USER)@$(ADDRESS) "sudo pgrep -f $(APP) | xargs sudo kill" || true
	@echo Done! && exit

