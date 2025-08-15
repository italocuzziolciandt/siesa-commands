use_case_document_template = """"
```markdown
    ## Use Case: [Use Case Name]
    **1. Overview**
    *   **Use Case ID:** (e.g., UC-001) *For tracking and reference.*
    *   **Use Case Name:** [A short, descriptive name]
    *   **Description:** [A brief summary of what this use case achieves.]
    *   **Source File Reference:** [A reference to the analyzed file (Procedure name, application file name etc.).]

    **2. Actors**
    *   **Primary Actor:** [The actor who initiates the use case]
    *   **Supporting Actors:** [Other actors involved (e.g., system components, external systems)]

    **3. Goal in Context**
    *   **Goal:** [What the primary actor wants to achieve by using this functionality.]
    *   **Scope:** [The system or component that is the subject of this use case. Helps define boundaries.]

    **4. Preconditions**
    *   [What must be true *before* the use case can begin. List each precondition.]
        *   *Example: "The user must be logged in."*
        *   *Example: "The database must be available."*

    **5. Postconditions**
    *   **Success Guarantee (or Minimal Guarantee):** [What *will* be true after the use case completes *successfully*.]
        *   *Example: "The item is added to the shopping cart."*
        *   *Example: "The user's password has been successfully reset."*
    *   **Failure Guarantee:** [What will be true even if the use case fails. This is often about maintaining data integrity.]
        *   *Example: "The system state remains unchanged if the use case fails."*
        *   *Example: "Partial transaction is rolled back."*

    **6. Main Success Scenario (Basic Flow)**
    1.  **Step 1:** [Actor action or system response.]
    2.  **Step 2:** [And so on...]
        *   *Describe the typical sequence of events when everything goes right in a business perspective.*
        *   *Don't include implementation details like methods invocation and so on.*
        *   *Use clear, simple language.*
        *   *Number each step.*

    **7. Extensions (Alternative Flows, Exceptions)**
    *   **[Extension Point Name]:** [Where the flow diverges from the main success scenario]
        *   **Condition:** [What triggers this alternative flow?]
        *   1.  **Step 1:** [Action in the alternative flow.]
        *   2.  **Step 2:** [Action in the alternative flow.]
        *   ...
        *   *May rejoin the main success scenario at a specific step (indicate which step).*
        *   *Or, may terminate the use case.*

    *   **[Another Extension Point Name]:** [And so on...]

    **8. Open Issues** (Optional)
    *   [List any unresolved questions or issues related to this use case.]
```
"""
