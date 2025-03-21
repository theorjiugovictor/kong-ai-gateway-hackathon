# Customer Support AI Hackathon Template

This project serves as a starting point for building an AI-powered customer support solution. The goal is to create technology that provides excellent customer support by having an understanding of all available facts, best practices, spare parts, and service staff related to customer inquiries.

## Features

- Persistent chat sessions with UUID-based identification
- Couchbase storage for chat history
- AI-powered chat interface with knowledge base integration
- Knowledge base browsing and searching
- Advanced Opper AI integration with structured output and conversation management

## Prerequisites

To get started, make sure you install Polytope:

### Docker or OrbStack
You'll need Docker or OrbStack to run the app. You can install Docker from [here](https://docs.docker.com/get-docker/) and OrbStack from [here](https://docs.orbstack.dev/install).

### Polytope CLI
On macOS:
```bash
brew install polytopelabs/tap/polytope-cli
```

Also make sure you're running at least Polytope 0.1.31:
```bash
pt --version
- The current CLI version is: 0.1.31-bae4935de-macos-arm64
```

If you're on an older version, you can update it with:
```bash
brew upgrade polytope-cli
```

For installation on Windows and Linux, see [the docs](https://polytope.com/docs/quick-start).

## Components
This app has two main components:
- [The API](./api) - A Python FastAPI backend that handles chat session management, knowledge base querying, and Opper AI integration
- [The UI](./frontend) - A React TypeScript frontend that provides the user interface

## Running the app
To run the app, clone this repository and navigate to the project directory:

```bash
git clone [repository-url]
cd customer-support-ai
```

Next, set the API keys you'll need as secrets:
```bash
pt secret set opper-api-key YOUR_OPPER_API_KEY
```

You can get an Opper API key by signing up at [Opper AI](https://opper.ai).

Finally, run the following command to start the app:
```bash
pt run stack
```

Then open the UI at [http://localhost:3000](http://localhost:3000). This can take a little while to return something useful - especially on the first run, because it needs to set up all the dependencies.

API documentation is automatically generated and can be found at [http://localhost:3000/docs](http://localhost:3000/docs).

## RESTful Chat API Design

The API follows a RESTful design with the following endpoints:

- `POST /api/chats` - Create a new chat session
- `GET /api/chats/{chat_id}` - Get a chat session by ID
- `GET /api/chats/{chat_id}/messages` - Get all messages for a chat session
- `POST /api/chats/{chat_id}/messages` - Add a message to a chat session and get a response
- `DELETE /api/chats/{chat_id}` - Delete a chat session and all its messages

Example usage:

```bash
# Create a new chat session
curl -X POST http://localhost:3000/api/chats -H "Content-Type: application/json" -d '{}'

# Get chat details (replace UUID with the one from previous response)
curl http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000

# Send a message and get a response
curl -X POST http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is your return policy?"}'

# Get chat history
curl http://localhost:3000/api/chats/550e8400-e29b-41d4-a716-446655440000/messages

# Search knowledge base
curl 'http://localhost:3000/api/knowledge-base/search?query=warranty'
```

## About Opper AI

This template uses [Opper AI](https://opper.ai) for LLM response generation and knowledge base integration. The response generation follows a pattern:

```python
def bake_response(messages):
    response, _ = opper.call(
        name="generate_response",
        instructions="Generate a helpful, friendly but brief response to the user's message in the conversation.",
        input={"messages": messages},
        output_type=str,
    )
    return response
```

Learn more about the [Opper SDK on GitHub](https://github.com/opper-ai/opper-python) and in the [official documentation](https://docs.opper.ai/).

## Hackathon Challenge

The challenge is to build an AI-powered technology that provides great customer support by having an understanding of all available facts, best practices, spare parts, and service staff related to customer inquiries.

Key aspects to consider:
1. **Knowledge integration**: How to effectively integrate domain knowledge
2. **Contextual understanding**: Properly interpreting user questions
3. **Accurate answers**: Providing correct and helpful responses
4. **Source attribution**: Citing knowledge sources when relevant
5. **Handling escalation**: Identifying when human intervention is needed

You'll have hot reload, so any changes you make to the code will be reflected in the UI immediately - however, if you add or remove packages you'll need to restart the app.
