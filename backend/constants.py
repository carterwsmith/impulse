from commands.constants import *

# Define the number of minutes that should pass before a session is not considered active.
ACTIVE_SESSION_TIMEOUT_MINUTES = 1

# Define the number of seconds that should pass between generating prompts for active sessions.
SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS = 10