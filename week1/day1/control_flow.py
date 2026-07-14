# DAY 1 - FILE 3: Control Flow
# Run with: python3 control_flow.py

# =============================================
# SECTION 1: if / elif / else
# =============================================

print("=== IF/ELIF/ELSE ===")

def classify_status_code(code):
    if code == 200:
        return "OK - SUCCESS"
    elif code == 201:
        return "Created - Resource created"
    elif code == 204:
        return "No Content - Deleated successfully"
    elif 400 <= code < 500:
        return f"Client Error - Code: {code}"
    elif code >= 500:
        return f"Server error - Code: {code}"
    else:
        return f"Unknown code: {code}"
    
print(classify_status_code(300))    #Unknown code: 300
print(classify_status_code(450))    #Client Error - Code: 450
print(classify_status_code(200))    #OK - SUCCESS
print(classify_status_code(201))    #Created - Resource created
print(classify_status_code(404))    #Client Error - Code: 404
print(classify_status_code(500))    #Server error - Code: 500
print(classify_status_code(422))    #Client Error - Code: 422

# Ternary - one liner conditional
status = 200
result = "PASS" if status == 200 else "FAIL"
print(result)