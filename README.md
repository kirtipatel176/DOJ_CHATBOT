## Project Overview

The **Department of Justice Chatbot** is an innovative AI-powered tool designed to assist individuals by providing quick and accurate legal information related to the **Department of Justice**. It leverages cutting-edge technologies such as **React.js**, **Python**, and **LangChain** to deliver a seamless user experience for anyone seeking legal assistance.

This chatbot serves as a digital assistant for citizens, legal professionals, and anyone interested in understanding legal processes, rights, and regulations under the jurisdiction of the **India Department of Justice**. It allows users to ask questions about a wide range of legal topics, from criminal justice to civil rights, and receive immediate, accurate, and well-informed responses powered by **OpenAI GPT** and **LangChain**.

### Purpose

The primary goal of this project is to make legal knowledge more accessible to everyone. Many individuals face difficulties when trying to understand legal jargon or the complexities of the law. The **Department of Justice Chatbot** solves this problem by offering an easy-to-use interface where users can interact with an AI system that understands and responds to their legal queries in simple, human-like language. This project is aimed at promoting legal literacy and empowering individuals with the information they need to navigate the legal landscape.

### Functionality

The **Department of Justice Chatbot** is capable of:

- **Answering Legal Questions**: The chatbot can answer queries about various legal topics, including civil and criminal law, government regulations, rights, legal processes, and more. It uses the LangChain framework to provide detailed, context-aware responses to complex legal inquiries.

- **Interactive Chat Interface**: Users interact with the bot through a real-time chat interface built using **React.js**. It provides an intuitive, easy-to-navigate platform for users to ask questions and receive answers instantly.

- **AI-Powered Responses**: The chatbot relies on **OpenAI GPT** models to generate intelligent and relevant legal responses based on the context of the query. The AI system is trained with a broad dataset of legal knowledge to provide accurate and trustworthy information.

- **Natural Language Processing (NLP)**: By utilizing **LangChain**, the chatbot efficiently handles the processing of legal language and multi-turn conversations, ensuring that it can respond appropriately to follow-up questions and context.

---

### Working

The system is designed to work seamlessly through a combination of frontend and backend technologies:

1. **Frontend (React.js)**:  
   The **React.js** frontend provides a user-friendly chat interface where users can type their questions and receive instant responses. The UI is designed to be simple and intuitive, ensuring a smooth experience for both tech-savvy users and those unfamiliar with legal terminology.

2. **Backend (Python with LangChain)**:  
   The **Python** backend is responsible for handling the core functionality of the chatbot. It processes user queries and integrates with the **LangChain** framework to generate contextual, high-quality answers. LangChain connects the Python backend to the **OpenAI GPT** model, allowing the system to answer complex legal questions accurately.

3. **Gemini Model**:  
   The chatbot uses the **Gemini ** model to generate responses that feel human-like and context-aware. It is fine-tuned to understand legal terminology and provide helpful, accurate answers to users' inquiries.

4. **Scalable Architecture**:  
   The system is built with scalability in mind, meaning additional features, legal modules, and languages can be easily added as the project evolves. The backend is flexible and can integrate new models or legal databases as necessary.

---

By combining powerful AI models with an easy-to-use chat interface, the **Department of Justice Chatbot** is set to become a valuable tool for anyone needing legal assistance, enhancing the accessibility of legal knowledge in a user-friendly format.

---

## Structure of the Folder 
```bash
DOJ_CHATBOT/
├── backend/                   # Backend folder (Python)
│   ├── app.py                 # Main Python application
│   ├── requirements.txt       # Python dependencies
│   └── ...                    # Other backend files
├── frontend/                  # Frontend folder (React.js)
│   ├── src/                   # React source code
│   ├── public/                # Public assets (images, etc.)
│   └── package.json           # React configuration and dependencies
├── README.md                  # Project documentation
└── LICENSE                    # Project license
```
## Installation

Follow these instructions to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/kirtipatel176/DOJ_CHATBOT.git
cd DOJ_CHATBOT
```

