import praw

from subreddit_archiver import (
        cli,
        db,
        states,
        get_posts,
        utils
        )


USER_AGENT = "subreddit-archiver"


@utils.clean_exit
def archive(subreddit, out_file, batch_size, credentials):
    # TODO: validate if a subreddit exists
    reddit = praw.Reddit(
            client_id = credentials['client_id'],
            client_secret = credentials['client_secret'],
            user_agent = USER_AGENT
            )
    db_connection = db.get_connection(out_file, credentials)
    state = states.State(db_connection)

    if state.get_progress() == states.Progress.IDLE:
        state.set_subreddit(subreddit)
        state.set_subreddit_created_utc(reddit.subreddit(subreddit).created_utc)
        state.set_progress(states.Progress.SAVING_POSTS)
        print(state.get_progress())
        print(states.Progress.SAVING_POSTS)

    if state.get_progress() == states.Progress.SAVING_POSTS:
        get_posts.archive_posts(reddit, db_connection, batch_size)

        state.set_progress(states.Progress.COMPLETED)

    if state.get_progress() == states.Progress.COMPLETED:
        print("Completed archiving")

@utils.clean_exit
def update(out_file, batch_size, credentials):
    reddit = praw.Reddit(
            client_id = credentials['client_id'],
            client_secret = credentials['client_secret'],
            user_agent = USER_AGENT
            )
    db_connection = db.get_connection(out_file, credentials)
    state = states.State(db_connection)

    try:
        state.get_most_recent_post_utc()
    except KeyError:
        print("Unable to update archive. No posts have been saved yet.")
        exit(1)

    get_posts.update_posts(reddit, db_connection, batch_size)

def main():
    args = cli.get_arg_parser().parse_args()

    if args.command == "archive":
        archive(args.subreddit, args.file, args.batch_size, args.credentials)
    if args.command == "update":
        update(args.file, args.batch_size, args.credentials)
