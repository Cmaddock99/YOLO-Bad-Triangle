# Lab 2 Text Entry Answers

## Task 2: Cyber Defense Matrix

| Scenario | Asset Class | Operational Function | Short rationale |
| --- | --- | --- | --- |
| A | Data | Protect | It is checking the `.pkl` file before it gets used, so I put this under Data and Protect. |
| B | Applications | Detect | It is watching the LLM app and sending alerts if someone is trying prompt abuse, so I put this under Applications and Detect. |
| C | Devices | Respond | Isolating the servers and cutting off the keys is a response step after the issue is found. |
| D | Data | Identify | The AI BOM is there to track where the training data came from and which version was used. |

## Task 3: MITRE ATLAS Mapping

### 1. Sponge Attack

- Tactics: `AML.TA0000` AI Model Access, `AML.TA0001` AI Attack Staging, `AML.TA0011` Impact
- Techniques:
- `AML.T0040` AI Model Inference API Access
- `AML.T0043` Craft Adversarial Data
- `AML.T0034.001` Resource-Intensive Queries
- `AML.T0029` Denial of AI Service
- Impact: `AML.T0029` Denial of AI Service

### 2. Audio Adversarial Perturbation

- Tactics: `AML.TA0001` AI Attack Staging, `AML.TA0004` Initial Access, `AML.TA0011` Impact
- Techniques:
- `AML.T0043` Craft Adversarial Data
- `AML.T0015` Evade AI Model
- `AML.T0052` Phishing
- `AML.T0048.000` Financial Harm
- Impact: `AML.T0048.000` Financial Harm

### 3. Hugging Face Repository Hijack

- Tactics: `AML.TA0004` Initial Access, `AML.TA0005` Execution, `AML.TA0009` Collection, `AML.TA0010` Exfiltration, `AML.TA0011` Impact
- Techniques:
- `AML.T0012` Valid Accounts
- `AML.T0010.001` AI Software
- `AML.T0011.001` Malicious Package
- `AML.T0037` Data from Local System
- `AML.T0025` Exfiltration via Cyber Means
- `AML.T0048.004` AI Intellectual Property Theft
- Impact: `AML.T0048.004` AI Intellectual Property Theft

## Knowledge Check

### 1. The Nature of Evasion

A person probably would not notice the FGSM noise because the pixel changes are really small. The image still looks the same to us, but it changes the input enough for the model to give a different answer.

### 2. The Flaw in Chat Templates

Tags like `<|im_start|>system` look important, but to the model they are still just text. Everything gets flattened into one token sequence, so later malicious instructions can still mess with earlier ones.

### 3. Semantic vs. Syntactic Analysis

Normal security tools usually look for fixed patterns like code signatures or suspicious syntax. Prompt injection does not always have one fixed pattern because the same harmful idea can be written a lot of different ways, so simple matching will miss some of them.

### 4. The Navigator Export

It matters because making the adversarial sample and actually using it are two different parts of the attack. A defender would not look for them in the same place, and the way you stop them is different too.

### 5. Detection vs. Protection

An IDS goes in Detect because it mainly watches activity and alerts on it. It does not really stop the action by itself. Protect would be something that actually blocks or prevents the attack.
