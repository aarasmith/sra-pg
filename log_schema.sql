/* Index(['host', 'host_ip', 'name', 'msg', 'args', 'levelname', 'pathname',
       'filename', 'module', 'exc_info', 'exc_text', 'stack_info', 'lineno',
       'funcName', 'timestamp', 'thread', 'threadName', 'processName',
       'process', 'message'],
*/       
CREATE TABLE IF NOT EXISTS logs(
    host text,
    host_ip text,
    name text,
    msg text,
    args text,
    levelname text,
    pathname text,
    filename text,
    module text,
    exc_info text,
    exc_text text,
    stack_info text,
    lineno text,
    funcname text, --case_change
    timestamp text,
    thread text,
    threadname text, --case_change
    processname text, --case_change
    process text,
    message text,
    foreign key (name) references posts (id)
)