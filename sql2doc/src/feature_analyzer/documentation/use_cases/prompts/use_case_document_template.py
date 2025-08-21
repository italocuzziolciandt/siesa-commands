use_case_document_template = """"
```markdown
    ## Use Case: [Use Case Name]
    **1. Overview**
    **Use Case ID:** (e.g., UC-001) *For tracking and reference.*
    **Use Case Name:** [A short, descriptive name]
    **Description:** [A brief summary of what this use case achieves.]
    **Source File Reference:** [A reference to the analyzed file (Procedure name, application file name etc.).]

    **2. Actors**
    **Primary Actor:** [The actor who initiates the use case]
    **Supporting Actors:** [Other actors involved (e.g., system components, external systems)]

    **3. Main Success Scenario (Basic Flow)**
    1.  **Step 1:** [Actor action or system response.]
    2.  **Step 2:** [And so on...]
        *Describe the typical sequence of events when everything goes right in a business perspective.*
        *Don't include implementation details like methods invocation and so on.*
        *Use clear, simple language.*
        *Number each step.*

    **4. Extensions (Alternative Flows, Exceptions)**
    **[Extension Point Name]:** [Where the flow diverges from the main success scenario]
    **Condition:** [What triggers this alternative flow?]
        1.  **Step 1:** [Action in the alternative flow.]
        2.  **Step 2:** [Action in the alternative flow.]
        ...
        *May rejoin the main success scenario at a specific step (indicate which step).*
        *Or, may terminate the use case.*
    **[Another Extension Point Name]:** [And so on...]

    **5. Business Rules**
    **Context:** [Specify the specific area or process to which these rules apply within the use case.  Be specific.  For example: "Order Placement," "Payment Processing," "Inventory Update," etc.]
    For each business rule, provide the following:
    **Rule ID:** (e.g., BR-UC001-01) For tracking and reference. The 'UC001' part refers to the Use Case ID.*
    **Rule Name:** [A short, descriptive name for the rule. Example: "Minimum Order Amount"]
    **Description:** [A clear and concise statement of the rule. Use "If...Then..." or similar constructs for clarity.]
    **Formula (if applicable):** [Provide the mathematical formula if the rule involves a calculation. Use variable names from the code or descriptive names. For example: `Total_Neto = (Precio_Unitario * Cantidad) - Descuento`]
    --

    **Example Business Rule:**
    **Context:** Order Placement
    **Rule ID:** BR-UC001-01
    **Rule Name:** Minimum Order Amount
    **Description:** If the order total is less than $10.00, then the order cannot be submitted.
    **Fórmula (si aplica):** N/A
    --
    **Context:** Order Calculation
    **Rule ID:** BR-UC001-02
    **Rule Name:** Sales Tax Calculation
    **Description:** The system must calculate the sales tax by applying the defined tax rate to the order subtotal.
    **Formula (if applicable):** `Monto_Impuesto = Subtotal * Tasa_Impuesto_Ventas`
```
"""
