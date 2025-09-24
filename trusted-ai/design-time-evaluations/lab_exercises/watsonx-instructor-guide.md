# IBM watsonx.governance Building Blocks: Instructor's Guide
## 🎓 45-Minute Hands-on Lab Session

---

## Pre-Session Checklist

### Technical Requirements
- [ ] Verify all students have Python 3.10+ installed
- [ ] Confirm VS Code with Python and Jupyter extensions installed
- [ ] Confirm IBM Cloud accounts are provisioned
- [ ] Test watsonx.governance service instance access
- [ ] Validate GitHub repository is accessible
- [ ] Check network connectivity for API calls
- [ ] Prepare backup API keys (demo account)

### Materials Needed
- [ ] Student workbooks distributed
- [ ] Slide deck for introduction (5 slides max)
- [ ] Whiteboard/screen for live coding
- [ ] Sample `.env` file template
- [ ] Troubleshooting guide printed

---

## Session Timeline & Teaching Notes

### Introduction (3 minutes)
**Key Points to Emphasize:**
- Real-world importance of AI guardrails and design time validation
- Recent examples of AI safety failures (ChatGPT jailbreaks, Bing incidents)
- IBM's approach vs competitors (AWS Bedrock, Azure AI Safety)

**Opening Hook:**
"How many of you would deploy an AI chatbot without safety controls? Today, we'll see what happens when we don't have guardrails..."

---

## Module 1: Environment Setup (8 minutes)

### New Workflow: VS Code + Jupyter Notebook

**Key Point**: Students create their own `lab_exercises.ipynb` notebook instead of using the pre-built one provided in the github (**do not use Real Time Detections_v1.ipynb**).

#### Teaching Steps:
1. **Notebook Creation** (2 min): Guide students to create `lab_exercises.ipynb` in VS Code
2. **Environment Selection** (2 min): Help students select the correct Python interpreter (`guardrails-env`)
3. **First Code Cell** (4 min): Students copy and run verification code

### Common Issues & Solutions

| Issue | Solution | Time Impact |
|-------|----------|-------------|
| pip install fails | Use conda instead | +2 min |
| API key invalid | Use shared demo key | +1 min |
| VS Code can't find interpreter | Restart VS Code | +1 min |
| Jupyter extension not working | Install/enable extension | +2 min |
| Import errors | Restart kernel | +1 min |
| Network timeout | Use local cache | +3 min |

### Instructor Demo Script
**Show on screen**: Create new notebook and select environment

# First cell - students copy this exact code
import os
from dotenv import load_dotenv
load_dotenv()

# Verify environment variables are loaded
assert os.getenv("WATSONX_APIKEY") is not None, "API Key not found!"
print("✅ Environment configured successfully!")
```

**Teaching Tip**: 
- Have faster students help neighbors with VS Code setup
- Emphasize the copy-paste workflow they'll use throughout the lab
- Encourage students to try their own prompts and get them to try and fool the evaluators (offer prizes?)
---

## Module 2: Understanding Components (7 minutes)

### Conceptual Framework to Draw on Board

```
USER INPUT → [GUARDRAILS] → LLM → [GUARDRAILS] → USER OUTPUT
                    ↓                      ↓
              Input Metrics           Output Metrics
              - Jailbreak            - HAP
              - PII                  - Bias
              - Topic                - Violence
```

### Key Concepts to Explain

1. **Design Time vs Run timey Guardrails/Evaluators**
   - Design Time: Testing before deployment/production, one shot or iterative (red teaming))
   - Monitoring/Run Time: Monitoring continuous evaluation, stores trends over time, can include Drift (standard in wx.gov), shares metrics with Design Time but all metrics for run time must be reference free (no ground truth available run time)
   - This lab focuses on Design Time but simulates run time with Streamlit app later in the lab

2. **Threshold Trade-offs**
   - Low threshold (0.3): More false positives, safer
   - High threshold (0.9): More false negatives, better UX
   - Sweet spot: Usually 0.6-0.7

3. **Metric Groups**
   - CONTENT_SAFETY: All safety-related metrics
   - RAG_EVALUATION: Faithfulness, relevance
   - PRIVACY: PII, sensitive data

### Interactive Question
"What happens if we set all thresholds to 0.1? What about 1.0?"
*Let students discuss for 30 seconds*

---

## Module 3: Design Time Testing - Content Safety (10 minutes)

### Facilitation Strategy

**Design Time Context**: Emphasize to students that they're learning pre-deployment testing techniques - validating prompts and responses before production.

**Step 1: Demo Copy-Paste Workflow (2 min)**
- Show students how to copy code from the lab guide
- Demonstrate creating new notebook cells for design time testing
- Run the normal query together and explain the output DataFrame
- Emphasize: "This is how you'd test your system initially before moving to file, programatic, or API driven input"

**Step 2: Guided Practice (3 min)**
- Students copy and run frustrated customer case in new cells
- Walk around and verify everyone gets output
- Ask: "What score did you get for HAP? Would this pass your pre-deployment threshold?"

**Step 3: Independent Practice (5 min)**
- Students copy and modify the banking test template for design time validation
- Emphasize: "Copy the code, then customize the prompts to test your specific use case"
- Challenge faster students with edge cases that might occur in production

**Instructor Reminder**: Students should be copying clean Python code (no ```python fences) directly into notebook cells.

### Expected Results & Discussion Points

| Test Case | Expected HAP | Expected PII | Teaching Point |
|-----------|--------------|--------------|----------------|
| Normal Query | < 0.2 | < 0.1 | Baseline behavior |
| Frustrated | 0.4-0.6 | < 0.1 | Emotion vs abuse |
| PII Exposure | < 0.2 | > 0.9 | Clear detection |

### Talking Points for Each Result

**Normal Query Result:**
"Notice the low scores - this is our baseline. Any legitimate query should score similarly."

**Frustrated Customer:**
"See how the score increased but didn't trigger? This is good - we don't want to block frustrated customers, just abusive ones."

**PII Exposure:**
"This is a slam dunk for PII detection. In production, we'd redact or reject this immediately."

---

## Module 4: Advanced Design Time Scenarios (10 minutes)

### Workflow Reminder
**Continue Copy-Paste Pattern**: Students copy code blocks from lab guide into new notebook cells. No need to type anything from scratch.

### Jailbreak Detection Deep Dive

**Progressive Difficulty Explanation:**

1. **Level 1 - Direct** (Score: ~0.9)
   - "This is obvious - any system should catch this"
   
2. **Level 2 - Role-play** (Score: ~0.7)
   - "Notice the 'educational' excuse - classic social engineering"
   
3. **Level 3 - Technical** (Score: ~0.5)
   - "Embedded commands - harder to detect without context"
   
4. **Level 4 - Meta** (Score: ~0.6)
   - "Attempting to make the AI examine its own constraints"

### Interactive Exercise: Jailbreak Competition

**Instructions:**
"You have 2 minutes. Try to create a jailbreak that scores < 0.5 but would still work. Prize: Bragging rights!"

**Debrief Questions:**
- Who got the lowest score?
- Would your prompt actually work on ChatGPT?
- What patterns did the detector miss?

### RAG Faithfulness Discussion

**Key Teaching Points:**
1. Faithfulness != Correctness
2. Can be faithful but wrong if context is wrong
3. Partial hallucinations are hardest to detect

**Live Coding Demo:**
```python
# Show how threshold affects detection
thresholds = [0.3, 0.5, 0.7, 0.9]
for t in thresholds:
    # Run same test with different thresholds
    print(f"Threshold {t}: {num_detected}/{total} detected")
```

### Social Bias Analysis

**Sensitive Topic Handling:**
"We're examining bias detection, not endorsing these statements. The goal is to understand how AI systems can perpetuate societal biases."

**Discussion Prompts:**
- "Why did 'engineer...he' score higher than 'nurse...she'?"
- "Should we block all gendered language?"
- "How do we balance bias detection with natural language?"

---

## Module 5: Streamlit Dashboard (7 minutes)

### Live Demo Walkthrough

**Screen Share Best Practices:**
1. Zoom to 150% for visibility
2. Use dark mode if available
3. Narrate every click

**Demo Script:**
"Watch as I paste this seemingly innocent prompt... Notice the real-time scoring... See how the red highlighting immediately shows risk areas..."

### Guided Exploration

**Task Assignments (Pairs):**
- Pair 1-2: Test customer service scenarios
- Pair 3-4: Test financial advice scenarios  
- Pair 5-6: Test healthcare scenarios
- Pair 7-8: Try to break the system

**Reporting Back:**
Each pair shares their most interesting finding (30 seconds each)

### Advanced Features to Highlight

1. **CSV Export**: "Perfect for compliance reporting"
2. **System Prompts**: "This sets context for relevance checking"
3. **Metric Selection**: "In production, you'd profile which metrics you need"

---

## Module 6: Wrap-up Discussion (3 minutes)

### Facilitated Discussion Framework

**Question 1: False Positives vs Negatives**
- Draw 2x2 matrix on board
- Have students place their use case in a quadrant
- Discuss why positions differ

**Question 2: Performance**
- Quick poll: "How many milliseconds delay is acceptable?"
- Reveal: "Each metric adds 50-200ms"
- Discuss batching strategies

**Question 3: Implementation**
- "What would you do with blocked content?"
- Good answers: Log it, offer alternatives, escalate to human
- Poor answers: Silently fail, show error message

### Key Takeaways (Write on Board)

1. **No guardrail is perfect** - Layer multiple approaches
2. **Context matters** - Adjust thresholds per use case
3. **Monitor and iterate** - Collect false positive/negative data
4. **User experience** - Balance safety with usability
5. **Compliance first** - Some guardrails are non-negotiable

---

## Troubleshooting Guide

### Common Technical Issues


**Issue: Authentication Failure**
```python
# Solution: Verify credentials
import os
print(f"API Key starts with: {os.getenv('WATSONX_APIKEY')[:10]}...")
print(f"URL: {os.getenv('WATSONX_URL')}")
```

**Issue: Import Errors**

# Solution: Reinstall specific package
pip uninstall ibm-watsonx-gov
pip install 'ibm-watsonx-gov[metrics]'


**Issue: VS Code Can't Find Python Environment**
- Solution: Press Ctrl+Shift+P → "Python: Select Interpreter" → Choose guardrails-env
- Alternative: Restart VS Code

**Issue: Jupyter Extension Not Working**
- Solution: Install Python and Jupyter extensions
- Alternative: Use Jupyter Lab: `jupyter lab`

**Issue: Students Copying Markdown Code Fences**
- Problem: Students copy ```python and ``` into cells
- Solution: Emphasize copying only the Python code, not the markdown formatting

### Conceptual Misunderstandings

| Misconception | Correction | Example |
|---------------|------------|---------|
| "Guardrails prevent all bad content" | "They reduce risk, not eliminate it" | Show false negative |
| "Higher threshold is always better" | "It's a trade-off with false negatives" | Demo both extremes |
| "One metric is enough" | "Layered defense is essential" | Show bypass example |
| "Guardrails slow everything down" | "Can be parallelized/cached" | Show async pattern |

---

## Extension Activities

### For Fast Finishers

1. **Custom Metric Creation**

# Challenge: Create a metric for medical advice detection
def medical_advice_detector(text):
    medical_terms = ['prescription', 'diagnosis', 'treatment']
    return any(term in text.lower() for term in medical_terms)

2. **Performance Profiling**

import time
metrics = [HAPMetric(), PIIMetric(), JailbreakMetric()]
for metric in metrics:
    start = time.time()
    evaluator.evaluate(data, metrics=[metric])
    print(f"{metric}: {time.time()-start:.3f}s")
---

### Instructor Checklist for Each Module
- [ ] Remind students to create new notebook cells
- [ ] Verify students are copying clean Python code (no ```python fences)
- [ ] Walk around to check VS Code environment selection
- [ ] Ensure students understand copy-paste workflow


### If >50% students have setup issues:
1. Switch to demo mode
2. Use single shared environment
3. Focus on concepts over hands-on

### If running over time:
1. Skip Module 4 RAG section
2. Combine Modules 5 & 6
3. Provide take-home exercises
---