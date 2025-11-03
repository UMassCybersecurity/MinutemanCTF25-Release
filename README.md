<p align="center">
  <img src="./docs/images/Minuteman-CTF-Logo.png" width="45%">&nbsp;&nbsp;&nbsp;
  <img src="./docs/images/CTFd.png" width="45%">
</p>

---

<p align="center">
  <h3 align="center">
    <a href="https://minuteman.umasscybersec.org/"> 🚩 Minuteman CTF 2025 </a> 
  </h3>
  <h3 align="center">
    🕠 October 17th, 6:00 PM EST - October 19th, 12:00 PM EST 
  </h3>
</p>

---
- [🚀 Quickstart - *for challenge authors*](#-quickstart---for-challenge-authors)
  - [Writing Challenges](#writing-challenges)
  - [Deploying Challenges](#deploying-challenges)
---

## 🚀 Quickstart - *for challenge authors* 
### Writing Challenges


1. **Create a new branch** for your challenge using the format:
`${CHALLENGE_CATEGORY}/${CHALLENGE_NAME}`

2.  **Create a new directory** for your challenge within the appropriate category directory:  
   `/challenges/${CHALLENGE_CATEGORY}/${CHALLENGE_NAME}`  
    - Although differences in the branch name and challenge's path name won't break anything, please try to keep them the safe for consistency. 
    - A challenge's category is determined based on it's parent folder, *NOT* in it's `info.yaml`. **To switch a challenge to another category**, you can move it to that category's parent folder 

3. **Each challenge directory must include the following files:**

  - **Required:**: 

  - This is a sample `info.yaml`. 
```
# category: must change folder
display-name-on-ctfd: "Simple XSS" # say this can be different from your challenge-naem

# uuid can be generated with `uuidgen` on Linux 
uuid: "8dbe4bf4-d57d-403c-8ad5-0a283162d2cd"
# flag format is 
flag: "MINUTEMAN{XSS-1s-C00l}"
description: "See if you can find the XSS bug!" # have example showing newlines in YAML
connection-info: "{{ HOST }}:{{ PORT }}"
attribution: "Asritha Bodepudi" 
tags:
  - xss 
  - easy
hints:
  - "Use BurpSuite!"
  - "This is reflected XSS"
```

### Deploying Challenges


