from api4jenkins import Jenkins

from config import (
    JENKINS_HOST,
    JENKINS_PASSWORD,
    JENKINS_USERNAME,
    NOTED_JOB,
    STUB_OFF_JOB,
)


jenkins = Jenkins(JENKINS_HOST, auth=(JENKINS_USERNAME, JENKINS_PASSWORD))


def build_noted_pipeline(commit_hash: str) -> str:
    """Makes request to Jenkins on build the pipline with website deploying.

    Attrs:
        commit_hash: a hash of commit which to build.
    Returns:
        Status information.
    """
    job = jenkins.get_job(NOTED_JOB)
    if job.building:
        return "building"
    job.build(COMMIT_HASH=commit_hash)
    return "build"


def build_stub_off() -> str:
    """Makes request to Jenkins on build the job to set off a website stub.

    Returns:
        Status information.
    """
    job = jenkins.get_job(STUB_OFF_JOB)
    if job.building:
        return "building"
    job.build()
    return "build"
