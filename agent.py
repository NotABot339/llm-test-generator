import json
import time
import openai
from openai.types.beta.threads.run import Run
import os
import docstring_parser

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

class Agent:
    def __init__(self, name: str, personality: str, tools=[]):
        self.name = name
        self.personality = personality
        self.tools = tools
        self.tool_belt = {}
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        self.assistant = self.client.beta.assistants.create(
            name=self.name,
            model="gpt-4o-mini"
        )
        self.thread = self.client.beta.threads.create()
        self.run = None

    def create_thread(self):
        self.thread = self.client.beta.threads.create()

    def add_message(self, message):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

    def add_custom_tools(self, custom_tools: dict[str, callable]={}):
        self.tool_belt = custom_tools

    def get_last_message(self):
        return self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        ).data[0].content[0].text.value

    def create_vector_store(self):
        self.store = self.client.beta.vector_stores.create()
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.store.id]}},
        )

    def clean_store_files(self):
        for file in self.client.beta.vector_stores.files.list(self.store.id):
            self.client.files.delete(file.id)

    def send_store_files(self, filelist):
        file_streams = [open(path, "rb") for path in filelist]

        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.store.id, files=file_streams
        )

    def _get_tools_in_open_ai_format(self):
        python_type_to_json_type = {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object"
        }

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.__name__,
                    "description": docstring_parser.parse(tool.__doc__).short_description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            p.arg_name: {
                                "type": python_type_to_json_type.get(p.type_name, "string"),
                                "description": p.description
                            }
                            for p in docstring_parser.parse(tool.__doc__).params

                        },
                        "required": [
                            p.arg_name
                            for p in docstring_parser.parse(tool.__doc__).params
                            if not p.is_optional
                        ]
                    }
                }
            }
            for tool in self.tool_belt.values()
        ]

    def _create_run(self):
        all_tools = self.tools + self._get_tools_in_open_ai_format()
        # try:
        response = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            tools=all_tools,
            instructions=f"""
                Your name is: {self.name}
                Your personality is: {self.personality}
            """,
            temperature=0.1,
            top_p=1.0 
        )
        return response
        # except openai.RateLimitError as e:
        #     print("Rate limit exceeded. Retrying...")
        #     retry_after = int(e.headers.get("Retry-After", 5))+1 # Use Retry-After header if available
        #     time.sleep(retry_after)
        #     return self._create_run()

    def _retrieve_run(self, run: Run):
        # print("Retrieving run")
        return self.client.beta.threads.runs.retrieve(
            run_id=run.id, thread_id=self.thread.id)

    def _cancel_run(self, run: Run):
        self.client.beta.threads.runs.cancel(
            run_id=run.id, thread_id=self.thread.id)

    def _call_tools(self, run_id: str, tool_calls: list[dict]):
        tool_outputs = []

        # we iterate over all the tool_calls to deal with them individually
        for tool_call in tool_calls:
            # we get the function object from the tool_call
            function = tool_call.function
            # we extract the arguments from the function. They are in JSON so we need to load them with the json module.
            function_args = json.loads(function.arguments)
            # we map the function name to our Agent's tool belt
            function_to_call = self.tool_belt[function.name]
            # we call the found function with the provided arguments
            function_response = function_to_call(**function_args)
            # we append the response to the tool_outputs list
            tool_outputs.append(
                {"tool_call_id": tool_call.id, "output": function_response})

        # we submit the tool outputs to OpenAI
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )

    def _poll_run(self, run: Run):
        status = run.status
        start_time = time.time()
        while status != "completed":
            if status == 'failed':
                if run.last_error.code == 'rate_limit_exceeded':
                    print("Rate limit exceeded. Waiting for 5 seconds")
                    # self._cancel_run(run)
                    time.sleep(5)
                    return False
                else:
                    print("Run failed with error: {}".format(run.last_error.message))
                    return False
            if status == 'expired':
                print("Run expired.")
                return False
            if status == 'requires_action':
                self._call_tools(
                    run.id, run.required_action.submit_tool_outputs.tool_calls)

            time.sleep(5)
            run = self._retrieve_run(run)
            status = run.status
        return True
            # elapsed_time = time.time() - start_time
            # if elapsed_time > 120:  # 2 minutes
            #     self._cancel_run(run)
            #     raise Exception("Run took longer than 2 minutes.")

    def run_agent(self):
        run = self._create_run()
        if self._poll_run(run):
            message = self.get_last_message()
            return message
        else:
            return self.run_agent()
    