from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
import dotenv

dotenv.load_dotenv()

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story.")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")

