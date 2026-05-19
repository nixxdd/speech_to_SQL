This is the project folder where everything will be.
To get started you must have Docker installed on your machine. Once installed open this folder in your terminal and
refer to commands in the "useful commands.txt" file.

The application is structured in the following way:

- FRONT END: To be implemented. Will allow the user to record a voice command and query the database

- BACK END: 
  - Ollama (sqlcoder): Running on the machine, it is the LLM used by WrenAI to query the database;
  - WrenAI: Running in Docker using its own stack. It allows the translation from natural language to sql-query;

- DATABASE: PostreSQL running in Docker. Will store the database used by the application.