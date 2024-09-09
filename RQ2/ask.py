import os
from openai import OpenAI

client = OpenAI(api_key="redacted", base_url="https://api.deepseek.com/beta")

with open("../RQ1/deepseek.txt", "r") as file:
    extracted_info = file.read()

def generate_prompt(sentence_number, condition_events, expected_operations, relationships):
    prompt = f"""
Based on the extracted information from the 3GPP TS 24.301 specification, generate a test procedure for the following scenario (Sentence {sentence_number}):

Condition event(s): {condition_events}
Expected operation(s): {expected_operations}
Relationship(s): {relationships}

It is crucial that you use the specific condition events, expected operations, and relationships provided above in your test procedure.

Generate a sequence of steps to indirectly trigger the condition event(s) and observe the expected operation(s), considering the specified relationships. The test procedure should include the following:
1. Preconditions: Any necessary setup or initial conditions required for the test.
2. Test Steps:
   a. Sequence of actions or messages to indirectly trigger the condition event(s).
   b. Observations or checks to verify the occurrence of the expected operation(s).
3. Postconditions: Any cleanup or final conditions to be met after the test.

Please provide the generated test procedure in the following format:
Test Procedure: Verification of Sentence {sentence_number} Behavior
Preconditions:
1. <precondition_1>
2. <precondition_2>
...
Test Steps:
1. <test_step_1>
2. <test_step_2>
...
Expected Results:
1. <expected_result_1>
2. <expected_result_2>
...
Postconditions:
1. <postcondition_1>
2. <postcondition_2>
...
"""
    return prompt

def extract_info(text):
    sentences = text.split('Sentence ')[1:]  # Split by 'Sentence ' and remove the first empty element
    info_list = []
    for sentence in sentences:
        parts = sentence.strip().split('\n')
        sentence_number = parts[0].strip(':')
        condition_events = "Not specified"
        expected_operations = "Not specified"
        relationships = "Not specified"
        
        for part in parts[1:]:
            if part.startswith("Condition event(s):"):
                condition_events = part.split(':', 1)[1].strip()
            elif part.startswith("Expected operation(s):"):
                expected_operations = part.split(':', 1)[1].strip()
            elif part.startswith("Relationship(s):"):
                relationships = part.split(':', 1)[1].strip()
        
        info_list.append((sentence_number, condition_events, expected_operations, relationships))
    return info_list

info_list = extract_info(extracted_info)
output_file = 'test_procedures_2.txt'
for sentence_number, condition_events, expected_operations, relationships in info_list:
    print(f"\nProcessing Sentence {sentence_number}:")
    print(f"Condition events: {condition_events}")
    print(f"Expected operations: {expected_operations}")
    print(f"Relationships: {relationships}")

    prompt = generate_prompt(sentence_number, condition_events, expected_operations, relationships)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="deepseek-coder",
        )
        
        response_content = chat_completion.choices[0].message.content.strip()
        
        with open(output_file, 'a') as file:
            file.write(f"\n\nTest Procedure for Sentence {sentence_number}:\n")
            file.write("Original Extracted Information:\n")
            file.write(f"Condition event(s): {condition_events}\n")
            file.write(f"Expected operation(s): {expected_operations}\n")
            file.write(f"Relationship(s): {relationships}\n")
            file.write("\nGenerated Test Procedure:\n")
            file.write(response_content)
            file.write("\n" + "="*50 + "\n")
        
        print(f"Test procedure for Sentence {sentence_number} generated and saved.")
    
    except Exception as e:
        print(f"Skipping Sentence {sentence_number} due to error: {str(e)}")
        continue

print("All test procedures generated and saved to", output_file)

print("\nFirst few lines of ../RQ1/deepseek.txt:")
with open("../RQ1/deepseek.txt", "r") as file:
    print(file.read(500))
