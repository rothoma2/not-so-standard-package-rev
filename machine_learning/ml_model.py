import json

import xgboost as xgb
from sklearn.preprocessing import OrdinalEncoder
import pandas as pd
import pickle
from pprint import pprint 
import openai
import os
from rich.console import Console

class Model:
    def __init__(self, json_content):

        NUM_FEATURES = [
            'count_words', 'number_of_lines', 'number_of_urls', 'number_of_ip_addresses', 'square_brackets_mean', 'square_brackets_std_dev', 'square_brackets_third_quartile', 'square_brackets_max_value', 'equal_signs_mean', 'equal_signs_std_dev', 'equal_signs_third_quartile', 'equal_signs_max_value', 'plus_signs_mean', 'plus_signs_std_dev', 'plus_signs_third_quartile', 'plus_signs_max_value', 'yara_sensitive_data_exfiltration', 'yara_suspicious_process_control', 'yara_shady_links', 'yara_command_overwrite', 'yara_clipboard_access', 'yara_eval_obfuscation', 'yara_base64_decode', 'yara_steganography', 'yara_anti_analysis', 'yara_suspicious_file_ops', 'yara_funcion_calls', 'yara_command_execution', 'yara_silent_process_execution', 'shanon_entropy__mean', 'shanon_entropy__median', 'shanon_entropy__variance', 'shanon_entropy__max', 'shanon_entropy__1Q', 'shanon_entropy__3Q', 'shanon_entropy__outliers', 'obfuscated_code_python'
        ]
        CAT_FEATURES = [
            'file_name_category'
        ]
        self.FEATURES = NUM_FEATURES #+ CAT_FEATURES

        self.json_content = json_content
        json_data = json.loads(json_content)
        #json_data["shanon_entropy__max"] = 8

        self.pandas_df = pd.DataFrame([json_data])

        self.pandas_df['file_name_category'] = self.pandas_df.apply(lambda row: self.file_name_category(row), axis=1)
        
        model_path = '/home/robert/git/fallback/not-so-standard-package/machine_learning/xgboost_model.pkl'
        self.loaded_model = self.load_model(model_path)

    def file_name_category(self, row):
        if "main" in row['file_name']:
            return "main"
        elif "init" in row['file_name']:
            return "init"
        elif "setup" in row['file_name']:
            return "setup"
        elif row['file_name'].startswith("_"):
            return "class"
        else:
            return "other"

    def load_model(self, model_path):
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    
    def predict(self):
        final_list_of_features = self.FEATURES

        self.pandas_df["predicted_label"] = self.loaded_model.predict(self.pandas_df[[x for x in final_list_of_features]])
        self.pandas_df["probability_xgboost"] = self.loaded_model.predict_proba(self.pandas_df[[x for x in final_list_of_features]])[:,1]

        if self.pandas_df["predicted_label"][0] == 1:
            
            file_path = self.pandas_df["full_file_path"][0]
            print(f"Evaluating: {file_path}")

            with open(file_path, 'r') as file:
                file_contents = file.read()

                prompt = """Act as a Malware Analyst. I am going to give you a file of python code. Analyze this code to see if it is a malicious python file. 
                        If it does such suspicious things, point me where and why you think this is malicious.
                        On the explanation take snippets of the source code when explaining in steps like Im a junior Developer. Be suscint. Explain it on a paragraph. No Yapping.
                        Provide this information in the following format:
                        Malicious: yes/no
                        Confidence score: %
                        Explanation:"""
                
                prompt = prompt + str(file_contents)
                openai_analysis = self.ask_openai_analyst(prompt)

                console = Console()
                console.print(f"This file is: [red]MALICIOUS[/red] ! ! !: {self.pandas_df['file_name'][0]}")
                print("With a confidence score of: ", round(self.pandas_df["probability_xgboost"][0], 2))
                print(openai_analysis)

        else:
            console = Console()
            console.print(f"This file is: [green]OK[/green] ! ! !: {self.pandas_df['file_name'][0]}")
            print("With a confidence score of: ", round((1-self.pandas_df["probability_xgboost"][0]), 2))


    def ask_openai_analyst(self, question_to_gpt):

        model_name="gpt-3.5-turbo"

        openai.organization = os.getenv("openai_organization")
        openai.api_key = os.getenv("openai_api_key")

        message = {
                'role': 'user',
                'content': question_to_gpt
            }
        
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[message]
        )

        chatbot_response = response.choices[0].message['content']
        return chatbot_response.strip()
