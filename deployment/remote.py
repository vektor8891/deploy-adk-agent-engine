import os
import sys

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

from adk_short_bot.agent import root_agent

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("user_id", "test_user", "User ID for session operations.")
flags.DEFINE_string("session_id", None, "Session ID for operations.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.DEFINE_bool("list", False, "Lists all deployments.")
flags.DEFINE_bool("create_session", False, "Creates a new session.")
flags.DEFINE_bool("list_sessions", False, "Lists all sessions for a user.")
flags.DEFINE_bool("get_session", False, "Gets a specific session.")
flags.DEFINE_bool("send", False, "Sends a message to the deployed agent.")
flags.DEFINE_string(
    "message",
    "Shorten this message: Hello, how are you doing today?",
    "Message to send to the agent.",
)
flags.mark_bool_flags_as_mutual_exclusive(
    [
        "create",
        "delete",
        "list",
        "create_session",
        "list_sessions",
        "get_session",
        "send",
    ]
)


def create() -> None:
    """Creates a new deployment."""
    # First wrap the agent in AdkApp
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Now deploy to Agent Engine
    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ],
        extra_packages=["./adk_short_bot"],
    )
    print(f"Created remote app: {remote_app.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    remote_app = agent_engines.get(resource_id)
    remote_app.delete(force=True)
    print(f"Deleted remote app: {resource_id}")


def list_deployments() -> None:
    """Lists all deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    print("Deployments:")
    for deployment in deployments:
        print(f"- {deployment.resource_name}")


def create_session(resource_id: str, user_id: str) -> None:
    """Creates a new session for the specified user."""
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    print("Created session:")
    print(f"  Session ID: {remote_session['id']}")
    print(f"  User ID: {remote_session['user_id']}")
    print(f"  App name: {remote_session['app_name']}")
    print(f"  Last update time: {remote_session['last_update_time']}")
    print("\nUse this session ID with --session_id when sending messages.")


def list_sessions(resource_id: str, user_id: str) -> None:
    """Lists all sessions for the specified user."""
    remote_app = agent_engines.get(resource_id)
    sessions = remote_app.list_sessions(user_id=user_id)
    print(f"Sessions for user '{user_id}':")
    for session in sessions["sessions"]:
        print(f"- Session ID: {session['id']}")


def get_session(resource_id: str, user_id: str, session_id: str) -> None:
    """Gets a specific session."""
    remote_app = agent_engines.get(resource_id)
    session = remote_app.get_session(user_id=user_id, session_id=session_id)
    print("Session details:")
    print(f"  ID: {session.get('id')}")
    print(f"  User ID: {session['userId']}")
    print(f"  App name: {session['appName']}")
    print(f"  Last update time: {session['lastUpdateTime']}")
    print(f"  Available fields: {list(session.keys())}")

def send_message(resource_id: str, user_id: str, session_id: str, message: str) -> None:
    """Sends a message to the deployed agent."""
    remote_app = agent_engines.get(resource_id)

    print(f"Sending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    for event in remote_app.stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        print(event)


def main(argv=None):
    """Main function that can be called directly or through app.run()."""
    # Parse flags first
    if argv is None:
        argv = flags.FLAGS(sys.argv)
    else:
        argv = flags.FLAGS(argv)

    load_dotenv()

    # Now we can safely access the flags
    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    user_id = FLAGS.user_id

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STAGING_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    if FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.list:
        list_deployments()
    elif FLAGS.create_session:
        if not FLAGS.resource_id:
            print("resource_id is required for create_session")
            return
        create_session(FLAGS.resource_id, user_id)
    elif FLAGS.list_sessions:
        if not FLAGS.resource_id:
            print("resource_id is required for list_sessions")
            return
        list_sessions(FLAGS.resource_id, user_id)
    elif FLAGS.get_session:
        if not FLAGS.resource_id:
            print("resource_id is required for get_session")
            return
        if not FLAGS.session_id:
            print("session_id is required for get_session")
            return
        get_session(FLAGS.resource_id, user_id, FLAGS.session_id)
    elif FLAGS.send:
        if not FLAGS.resource_id:
            print("resource_id is required for send")
            return
        if not FLAGS.session_id:
            print("session_id is required for send")
            return
        send_message(FLAGS.resource_id, user_id, FLAGS.session_id, FLAGS.message)
    else:
        print(
            "Please specify one of: --create, --delete, --list, --create_session, --list_sessions, --get_session, or --send"
        )


if __name__ == "__main__":
    app.run(main)
