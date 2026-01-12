WEEK 1: ENGINEERING MINDSET BOOTCAMP

	DAY1: SYSTEM REVERSE ENGINEERING+ NODE & TERMINAL MASTERING

	    TASK1: TO IDENTIFY AND DOCUMENT
		    1. OS VERSION
	            INTRODUCTION: An OS version is a release of system software( like windows, macOS, Android) that:
	            --Marks particular point in the OS's lifecycle that helps differentiating it from various versions.
	            --Every version has different features, updates, and build, design, bug fixes etc.
	            --Each version is a unique combination of numbers and letters (eg: ubuntu 24.03.3)
				
	            WHY DO WE NEED OS: OS is responsible for managing all the resources of the computer which ensures that OS acts as perfect intermediary between hardware and applications. It basically is important for the following:
	            -- Troubleshooting: Helps identify issues and compatibility problems.
	            -- Software Compatibility: Ensures applications run correctly on your specific OS build.
	            -- Security: Knowing your version helps you to secure your system by having compatible security tools, software, updates.
				
	            TYPES OF OS: There are mainly four types of OS:
	            a. Desktop OS: Windows, macOS, Linux for computers
	            b. Mobile OS: Android, iOS for smartphones
	            c. Network OS: Windows Server, Linux for managing networked resources
	            d. Real-Time OS(RTOS): Needed for systems with strict timing like cars or medical services or defense.
	            Other various types include Batch, Time-Sharing and Distributed OS.
	            ** FACTORS FOR OS SELECTION
	            -- CUSTOMER USE CASE: This is the most crucial factor. It specifies that how the system will be used.
				    a. General Consumer Use: For typical home users an OS that is user- friendly which supports wide range of softwares that are compatible with various media formats should be used like windows, macOS.
				    b. Business: Enterprises generally prioritize various other factors than user-friendliness or compatibility with wide range of formats. They focus more on specific proprietary software that serves the company's requirements like stability, security, robust networking capabilities, and strong technical support like Linux distributions or Unix-based systems for servers.
				    c. Servers: These environments require high stability, security, reliability, scalability and efficient handling of multiple concurrent requests like Linux, Unix.
				    d. Development: Developers generally prefer flexibility which allows them to integrate with diverse range of programming languages and server environments like Linux.
				    e. Gaming: People into gaming need OS with high performance,broad compatibility with graphics hardware, extensive driver support and a vast game library like Windows.
				    f. Mobile Devices: These OS's also need to be user friendly as they are used by everyone in their day to day lives, touch interface, low power consumption and app ecosystems like Android and iOS.
	            -- HARDWARE COMPATIBILTY AND REQUIREMENTS: An OS must support the specific or already planned hardware like CPU architecture, available memory (RAM), storage, graphic cards etc. Like macOS only works with Apple hardware.
	            -- SOFTWARE COMPATIBLITY: If we need specific softwares to work on then we need an OS compatible to it. Certain professional or industry specific software might only be available on a single platform.
	            -- SECURITY AND STABILITY: Different OSes have varying levels of vulnerability to security threats. The security model and the frequency/quality of security updates are critical for users dealing with sensitive information. Stability is crucial in server environments where downtime is unacceptable.
	            -- COST AND LICENSING MODEL: The financial consideration include the upfront purchase cost of the OS license and its related software. Windows and macOS require purchasing license whereas most linux distributions are open-source.
	            --SUPPORT AND COMMUNITY: The availability of reliable techincal support is essential for troubleshooting.
				
	            FIVE MOST COMMONLY USED OS: 
	            --Microsoft Windows
	            --Apple macOS
	            --Google Android
	            --Apple iOS
	            --Linux.
				
	            COMMANDS TO IDENTIFY OS VERSION:
	            a. cat /etc/os-release
				    DESCRIPTION: Displays comprehensive OS identification data, including name, version and ID. This is recommended and widely used method.
				    WORKS ON: Most modern Linux distributions.
				    ![release](Screenshots-day1-task1/cat-etc-os-release.png)
	            b. hostnamectl
				    DESCRIPTION: Provides system information in a neat format, including OS and kernel version.
				    WORKS ON: System-based distributions.
				    ![hostname](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/hostnamectl.png)
	            c. lsb_release -a
				    DESCRIPTION: Shows Linux Standard Base (LSB) and distribution-specific information.
				    WORKS ON: Distribution with lsb-release package installed.
				    ![lsb](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/lsb_release-a.png)
	            d. cat /etc/*-release
				    DESCRIPTION: A heuristic approach to display contents of all files ending with -release, which often includes the relevant version file.
				    WORKS ON: Many distributions.
				    ![starrelease](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/cat-etc-*-release.png)
    2. CURRENT SHELL
    a. ps -p $$
    DESCRIPTION: The actual running process command name
    RELIABILITY FOR CURRENT SHELL: High
    ![psp](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/ps-p$$.png)
    b. echo $0
    DESCRIPTION: The name the shell was invoked with
    RELIABILITY FOR CURRENT SHELL: Medium
    ![echozero](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/ech-$0.png)
    c. ls -l /proc/$$/exe
    DESCRIPTION: The actual shell executable path
    RELIABILITY FOR CURRENT SHELL: High
    ![proc](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/ls-l-proc-$$-exe.png)
    d. echo $$SHELL
    DESCRIPTION: Your default configured logon shell.
    RELIABILITY FOR CURRENT SHELL: Low
    ![shell](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/echo$$shell.png)
   3. NODE BINARY PATH
   **Node Binary Path commands were not working when I tried them first. The reason to it was that I did not install node npm, so it could not track the location or path or the details I was asking because my system did not have any folder or library named nodejs or npm.
   Commands before installing nodejs npm-----> ![not](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/npm-before-installation.png)
   Command to install nodejs npm-------------> ![install](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/install-nodejs-npm.png)
    a. which node
    Displays full path to the node executable that your shell will use when you type node.
    ![node](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/which-node.png)
    b. which nodejs
    On some older or specific Debian-based systems (like Ubuntu), the executable might be named nodejs instead of node due to a naming conflict
    ![nodejs](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/which-node-js.png)
    c. whereis node
    This command is similar to which but often provides additional information, such as the location of source files and manual pages, if available.
    ![whereis](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/where-is-node.png)
    d. type node
    command tells you whether node is a built-in command, a function, an alias, or a binary file and provides it location.
    ![type](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/type-node.png)
    e. npm bin -g
    If you want to find the directory where globally installed npm binaries (which includes the globally installed node executable if installed via a version manager like nvm or certain npm configurations) are stored, you can use this command. 
    This command is throwing an error because bin is not used in updated versions(2026) of nodejs npm, rather we can use npm config get prefix.
    ![bin](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/npm-bin-g.png)
   4. NPM GLOBAL INSTALLATION PATH
    a. npm root -g
    This command prints the absolute path to the directory where global packages are installed
    ![root](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/nom-root-g.png)
    b. npm config get prefix
    This command prints the "prefix" where npm is configured to install global items. The actual packages are typically in a node_modules subfolder within this prefix
    ![config](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/npm-config-get-prefix.png)
  5. ALL PATH ENTRIES THAT INCLUDE "node" OR "npm"
    a. echo $PATH | tr ':' '\n' | grep -i 'node/|npm'
    List PATH entries and show only directories related to Node or npm.
    ![echo](/home/shreyasinghal/Desktop/Training Bootcamp/Week1/Day1/Task1/Screenshots-day1-task1/echo-path-tr-grep.png)
    
