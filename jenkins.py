import os

from jenkinsapi.custom_exceptions import UnknownJob
from jenkinsapi.jenkins import Jenkins

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
    JENKINS_HOST, username=JENKINS_USERNAME, password=JENKINS_PASSWORD
)


def build_job(job: str, **kwargs):
    """Makes request to Jenkins on build the job.

    Attrs:
        job: a job path.
        kwargs: a job parameters.
    Returns:
        Status information or the error/info message.
    """
    try:
        job = jenkins[job]
    except UnknownJob as error:
        print(error)
        return "Unknown job path."

    if job.is_queued_or_running():
        return "The job is currently building or queued."

    try:
        job.invoke(build_params={**kwargs})
    except ValueError as error:
        if not error.args[0].startswith("Not a Queue URL"):
            raise

    return "build"


def get_job_details():
    """Get job details of each job that is running on the Jenkins instance"""
    output = []
    for _, job_instance in jenkins.get_jobs():
        output.append(
            "Job Name: %s\n" % job_instance.name
            + "Job Description: %s\n" % (job_instance.get_description())
            + "Is Job running: %s\n" % (job_instance.is_running())
            + "Is Job enabled: %s\n\n" % (job_instance.is_enabled())
        )
    return "".join(output)
