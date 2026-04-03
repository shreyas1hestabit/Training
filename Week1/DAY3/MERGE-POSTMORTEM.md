MERGE CONFLICT RESOLUTION

1.PROJECT SETUP
    REPO STRUCTURE
    a. repo-A -> Main integration repo (TEAM A)
    b. repo-B -> Secondary repo (TEAM B)
    Common file involved in conflict: auth-system/auth.js
    ![list]("/home/shreyasinghal/Training-day3/screenshots/list.png")

2.INITIAL STATE (Before Conflict)
    Both repositories had a common authorization system.
    The file auth.js existed in both repos with similar logic.
    Main branch was clean and in sync with origin/main.
    ![i]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-33-53.png")

3.TEAM A CHANGES (repo-A)
    WHAT TEAM A DID
    --Updated authorization logic comments
    --No functional change, only clarification
    Code(Team A version)
    ![repoa]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-37-58.png")
    Git commands used
    ![commita]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-40-02.png")

4.TEAM B CHANGES (repo-b)
    WHAT TEAM B DID
    --Modified the same file auth.js
    --Added a comment and changed logic allowing non-employees
    Code(Team B version)
    ![repob]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 17-50-53.png")
    Git commands used
    ![commitb]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-44-24.png")
    
5.CREATING THE CONFLICT
    --Team B changes were fetched into repo-A.
    --Both teams modified the same lines in auth.js
    Command that created conflict
    ![error]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-46-56.png")
    
6.CONFLICT MAKERS IN FILE
![conflict]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 17-03-24.png)

7.CONFLICT RESOLUTION DECISION
    DECISION TAKEN
    --Keep Team A's secure logic
    --Preserve Team B comment history only if relevant
    --Remove insecure logic
    ![res]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-53-35.png")
    
8.COMPLETING THE MERGE
![mergecomplete]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-55-15.png")

9.VERIFYING MERGE HISTORY
    --Merge commit is visible
    --Both Team A and Team B commits are preserved
    ![graph]("/home/shreyasinghal/Training-day3/screenshots/Screenshot from 2026-01-08 18-56-39.png")
