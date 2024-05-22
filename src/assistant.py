import anthropic
import json, logging
from datetime import datetime
from src.email_utils import EmailClient, Email
from src.save_file import cache



ASSISTANT_SYSTEM_PROMPT = """
You are a personal assistant here to be helpful. You will have access to some tools to send and read emails.
Only answer in english please.
If you use a tool include as much of the tool output as possible.
"""



class EmailAssistant:

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self.api_key = api_key
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            print("Error Copilot failed to make client connection to anthropic: " + str(e))
            raise e
        self.max_tokens = max_tokens
        self.model = model
        self.tools = [
            {
                "name": "time",
                "description": "Returns the current time in format %H:%M:%S.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        }
                    },

            }, {
                "name": "read_mail",
                "description": """Returns a processed string of all the text in the email html body.
                When this tool is used it is important that you answer in the following format:
                Title: "subject" <sender_address@example.com>
                Summary: summary of important information in email
                Suggestion: (Suggest how the email should be treated.)
                """,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "increment": {
                            "type": "integer",
                            "description":     """
                                            :param increment: Specifies which email to fetch (e.g. 1 for most recent or 10 for 10th most recent).
                                            """
                        }
                    },
                    "required": ["increment"]
                }
            }, {
                "name": "send_mail",
                "description": """Send a string message and subject to a specified email address""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "The subject of the email",
                        }, 
                        "message": {
                            "type": "string",
                            "description": "The message of the email",
                        },
                        "reciever": {
                            "type": "string",
                            "description": "The email address of the reciever of the email",
                        }
                    },
                    "required": ["subject", "message", "reciever"]
                }
            }

        ]
        self.email_client = EmailClient()
        self.email_client.connect()

    @staticmethod
    def get_time():
        return datetime.now().strftime("%H:%M:%S")
    
    def _count_tokens(self, message) -> int:
        count = self.client.count_tokens(message)
        return count

    def process_tool_call(self, tool_name, tool_input):
        if tool_name == "time":
            return self.get_time()
        if tool_name == "read_mail":
            return self._read_mail(increment=tool_input["increment"])
        if tool_name == "send_mail":
            try:
                print("Sending mail...")
                return self.email_client.send_mail(to_address=tool_input["reciever"], subject=tool_input["subject"], message=tool_input["message"])
            except Exception as e:
                logging.error(f"Failed to send mail: {e}")
                raise e
        
    def _read_mail(self, increment: int) -> str:
        try:
            print("Reading mail...")
            msg = self.email_client.get_mail(increment=increment)
            processed_msg = str(msg.processed_data)
            cache(msg)
            return processed_msg
        except Exception as e:
            logging.error(f"Failed to read mail: {e}")
            raise e

    def assistant_chat(self, user_message, max_tokens: int = 1024):
        message = self.client.beta.tools.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": user_message}],
            tools=self.tools,
        )

        logging.info(f"Initial Response:")
        logging.info(f"Stop Reason: {message.stop_reason}")
        logging.info(f"Content: {message.content}")

        if message.stop_reason == "tool_use":
            tool_use = next(block for block in message.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input

            logging.info(f"Tool Used: {tool_name}")
            logging.info(f"Tool Input: {tool_input}")

            tool_result = self.process_tool_call(tool_name, tool_input)

            logging.info(f"Tool Result: {tool_result}")

            response = self.client.beta.tools.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=ASSISTANT_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": message.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": tool_result,
                            }
                        ],
                    },
                ],
                tools=self.tools,
            )
        else:
            response = message

        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )

        logging.info(response.content)
        logging.info(f"Final Response: {final_response}")
        print(f"\n{'='*50}\nFinal Response:\n{final_response}\n{'='*50}")

        return final_response
    

    def _user_message(self) -> str:
        user_message = input("User: ")
        print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
        user_message = user_message.replace("\n", "")
        user_message = user_message.replace(" ", "")
        print(f"Estimated tokens {self._count_tokens(user_message)}\n")
        return user_message
    
    def assistant(self):
        print(f"\n{'='*50}\nEMAIL ASSISTANT ACTIVATED!\nTo exit the program simply type 'exit'.\n{'='*50}\n")
        while True:
            user_message = self._user_message()
            if user_message.lower() == "exit":
                self.email_client.disconnect()
                print(f"\n{'='*50}\nExiting program...\n{'='*50}")
                break
            else:
                self.assistant_chat(user_message)
