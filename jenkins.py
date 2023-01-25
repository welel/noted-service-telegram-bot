import os

from api4jenkins import Jenkins

from config import JENKINS_HOST, JENKINS_PASSWORD, JENKINS_USERNAME


if (
    "JENKINS_HOST" not in os.environ
    or "JENKINS_PASSWORD" not in os.environ
    or "JENKINS_USERNAME" not in os.environ
):
    raise AssertionError(
        "Please configure JENKINS_HOST, JENKINS_PASSWORD and JENKINS_USERNAME \
            as environment variables"
    )


jenkins = Jenkins(
    JENKINS_HOST, auth=(JENKINS_USERNAME, JENKINS_PASSWORD), token=True
)


def build_job(job: str, **kwargs):
    """Makes request to Jenkins on build the job.

    Attrs:
        job: a job path.
        kwargs: a job parameters.
    Returns:
        Status information or the error/info message.
    """
    job = jenkins.get_job(job)
    if not job:
        return "The given path is incorrect."
    if job.building:
        return "The job is currently building."
    job.build(**kwargs)
    return "build"
