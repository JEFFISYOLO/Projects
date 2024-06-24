from flask import Flask, request, render_template
import pandas as pd
import openai
import pyttsx3
import os

app = Flask(__name__)

# Set your API key
openai.api_key = ''

# Define the paths to the CSV files and summary file
summary_file_path = 'C:/Users/HP/Desktop/Python/Interntest2/summaries.txt'
archive_path = 'C:/Users/HP/Downloads/archive'
train_csv_path = os.path.join(archive_path, 'train.csv')
validation_csv_path = os.path.join(archive_path, 'validation.csv')
test_csv_path = os.path.join(archive_path, 'test.csv')

# Load the CSV files
train_df = pd.read_csv(train_csv_path)
validation_df = pd.read_csv(validation_csv_path)
test_df = pd.read_csv(test_csv_path)

# Function to call OpenAI GPT-3.5 for summarization
def create_chat_completion(article_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes scientific articles."},
        {"role": "user", "content": article_text}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message['content']

# Audio output function using pyttsx3
def TTS(text):
    engine = pyttsx3.init()
    newVoiceRate = 150
    engine.setProperty("rate", newVoiceRate)
    engine.say(text)
    engine.runAndWait()

# Function to store summary
def store_summary(num, summary):
    try:
        with open(summary_file_path, 'a') as file:
            file.write(f"num: {num}\n")
            file.write(summary + "\n")
            file.write("--------------------\n")
        print(f'Successfully wrote to {summary_file_path}')
    except IOError as e:
        print(f'Error writing to file: {e}')

# Function to read summaries
def read_summaries():
    summaries = []
    try:
        with open(summary_file_path, 'r') as file:
            lines = file.readlines()
            summary = {}
            for line in lines:
                if line.startswith("num:"):
                    if summary:
                        summaries.append(summary)
                        summary = {}
                    summary['num'] = line.split(":")[1].strip()
                elif line.startswith("--------------------"):
                    continue
                else:
                    summary['summary'] = summary.get('summary', '') + line.strip() + " "
            if summary:
                summaries.append(summary)
    except FileNotFoundError:
        print("Summary file not found.")
    except IOError as e:
        print(f'Error reading file: {e}')
    return summaries

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    file_type = request.form['file_type']
    article_index = int(request.form['article_index'])

    # Define the DataFrame based on selection
    if file_type == "Train":
        df = train_df
    elif file_type == "Validation":
        df = validation_df
    else:
        df = test_df

    article_text = df.iloc[article_index]['article']

    # Perform summarization
    summary = create_chat_completion(article_text)

    # Text-to-Speech output
    TTS(summary)

    # Store the summary
    store_summary(article_index, summary)

    return render_template('index.html', original_text=article_text, summary_text=summary)

@app.route('/summaries')
def summaries():
    summaries = read_summaries()
    return render_template('summaries.html', summaries=summaries)

if __name__ == "__main__":
    app.run(debug=True)
