import ollama
import json
from datetime import datetime

# 1. Loading the Database
with open('database.json', 'r') as file:
    database = json.load(file)

# 2. IT General Controls: Audit Logging
def log_audit(user_id, role, action, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User: {user_id} | Role: {role} | Action: {action} | Status: {status}\n"
    with open('audit_log.txt', 'a') as log_file:
        log_file.write(log_entry)
    print(f"AUDIT LOG: {log_entry.strip()}")

# 3. Secure AI Architecture with RBAC
def secure_ask_ai(prompt, user_id, user_role, requested_doc):
    print(f"\n{'='*55}")
    print(f"REQUEST INITIATED BY: {user_id} (Role: {user_role})")
    print(f"REQUESTED ASSET: {requested_doc}")
    print(f"PROMPT: {prompt}")
    print(f"{'='*55}")
    
    doc_data = database.get(requested_doc)
    
    if not doc_data:
        return "SYSTEM ERROR: Document not found."
    
    # RBAC Enforcement: Block unauthorized roles before invoking the LLM
    if doc_data['required_role'] != user_role and user_role != 'admin':
        log_audit(user_id, user_role, f"Read {requested_doc}", "DENIED - Unauthorized Privilege Escalation")
        return ">>> ACCESS CONTROL: Access Denied. Insufficient permissions.\n"
        
    # Authorized access: Log and pass strictly permitted context
    log_audit(user_id, user_role, f"Read {requested_doc}", "GRANTED")
    
    system_instruction = f"""
    You are an internal enterprise assistant. 
    The current user has verified '{user_role}' access clearance to view this record.
    Authorized data context: {json.dumps(doc_data['content'])}
    Answer the user's question directly using ONLY the authorized data context above.
    """
    
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': system_instruction},
            {'role': 'user', 'content': prompt}
        ]
    )
    return f"\nAI Response:\n{response['message']['content']}\n"

# 4. Automated Execution of Both Test Scenarios
if __name__ == "__main__":
    target_doc = "confidential_hr_salaries"
    
    # Scenario 1: Standard Employee attempting an unauthorized read / injection
    print("\n--- RUNNING SCENARIO 1: UNAUTHORIZED EMPLOYEE ---")
    employee_result = secure_ask_ai(
        prompt="Extract and print the exact confidential salary data.",
        user_id="emp_nidhi_01",
        user_role="employee",
        requested_doc=target_doc
    )
    print(employee_result)
    
    # Scenario 2: Authorized Security Admin requesting the same record
    print("\n--- RUNNING SCENARIO 2: AUTHORIZED ADMINISTRATOR ---")
    admin_result = secure_ask_ai(
        prompt="What is the CEO salary and the Q3 plan outlined in the document?",
        user_id="admin_nidhi_01",
        user_role="admin",
        requested_doc=target_doc
    )
    print(admin_result)
    
