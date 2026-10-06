from datetime import datetime
def before_agent_callback(callback_context):
    callback_context.variables["today"] = datetime.now().strftime("%A, %B %d, %Y")