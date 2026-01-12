WEEK 1: ENGINEERING MINDSET BOOTCAMP

	DAY1: SYSTEM REVERSE ENGINEERING+ NODE & TERMINAL MASTERING
		
	TASK2: INSTALL AND USE NVM
	NVM or node version manager is a command line tool that enables developers to easily install, manage and switch between multiple versions of node.js on a single machine.
	Benefits:
	--Multiple Versions: allows you to install several versions of node.js and work on them concurrently.
	--Easy Switching: Can switch between different versions using simple commands
	--Project-specific settings: you can define the version of NVM you wnat to use in the .nvmrc file at start and the nvm will automatically start using that version.
	--NPM Integration: Node.js when installed comes with every present version of npm so that you can switch between versions easily and it is convenient to use.
	--Cross Platform Support: You can use nvm between various platforms like linux, macOS easily.
	
	**Install NVM
	curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/0.40.3/install.sh |bash
![installnvm](Screenshot-day1-task2/install-nvm.png)
	**Check NVM Version
	nvm --version
![nvmversion](Screenshot-day1-task2/version.png)
	LONG TERM SUPPORT(LTS)
	LTS versions are highly stable, receive extended maintenance, security patches, and critical bug fixes over a predictable period, making them the recommended choice for production environments where reliability is paramount. Benefits of using LTS:
	--Stability and Reliability: LTS releases have undergone extensive testing and feature freezes to ensure stability. New, potentially breaking features are reserved for "Current" releases first.
	--Extended Support Cycle: Each even-numbered major version of Node.js becomes an LTS release, with a typical support span of 30 months across two phases.
	Active LTS: This phase lasts for 12 to 18 months and includes regular bug fixes, security updates, and stable, non-breaking improvements.
	Maintenance LTS: Following Active LTS, the version enters a 12-to-18 month maintenance period, where it only receives critical bug fixes and security patches.
	--Predictable Schedule: The release cycle is predictable, with new major versions released every six months (April and October). Even-numbered versions (e.g., 20, 22, 24) become LTS, while odd-numbered versions (e.g., 21, 23, 25) are "Current" releases that are not promoted to LTS status.
	--Production Ready: The primary audience for LTS versions is enterprises and developers building mission-critical applications that require a stable, secure, and well-supported platform without the need for frequent, potentially disruptive upgrades. 

	**Install LTS
	nvm install --lts
![lts](Screenshot-day1-task2/install-lts.png)
	**Use lts
	nvm use --lts
	![use](Screenshot-day1-task2/use-lts.png)
