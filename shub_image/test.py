import click
from shub.deploy import list_targets

from shub import exceptions as shub_exceptions
from shub_image import utils

SHORT_HELP = "Test a built image with Scrapy Cloud contract"
HELP = """ TODO """

SH_EP_SCRAPY_WARNING = \
    'You should add scrapinghub-entrypoint-scrapy(>=0.7.0) dependency' \
    ' to your requirements.txt or to Dockerfile to run the image with' \
    ' Scrapy Cloud.'


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("target", required=False, default="default")
@click.option("-l", "--list-targets", help="list available targets",
              is_flag=True, is_eager=True, expose_value=False,
              callback=list_targets)
@click.option("-d", "--debug", help="debug mode", is_flag=True)
@click.option("--version", help="release version")
def cli(target, debug, version):
    test_cmd(target, version)


def test_cmd(target, version):
    config = utils.load_release_config()
    image = config.get_image(target)
    version = version or config.get_version()
    image_name = utils.format_image_name(image, version)
    docker_client = utils.get_docker_client()
    for check in [_check_image_exists,
                  _check_start_crawl_entry,
                  _check_list_spiders_entry,
                  _check_sh_entrypoint]:
        check(image_name, docker_client)


def _check_image_exists(image_name, docker_client):
    """Check that the image exists on local machine."""
    # if there's no docker lib, the command will fail earlier
    # with an exception when getting a client in get_docker_client()
    from docker.errors import NotFound
    try:
        docker_client.inspect_image(image_name)
    except NotFound as exc:
        utils.debug_log("{}".format(exc))
        raise shub_exceptions.NotFoundException(
            "The image doesn't exist yet, please use build command at first.")


def _check_sh_entrypoint(image_name, docker_client):
    """Check that the image has scrapinghub-entrypoint-scrapy pkg"""
    status, logs = _run_docker_command(
        docker_client, image_name,
        ['pip', 'show', 'scrapinghub-entrypoint-scrapy'])
    if status != 0 or not logs:
        raise shub_exceptions.NotFoundException(SH_EP_SCRAPY_WARNING)


def _check_list_spiders_entry(image_name, docker_client):
    """Check that the image has list-spiders entrypoint"""
    status, logs = _run_docker_command(
        docker_client, image_name, ['which', 'list-spiders'])
    if status != 0 or not logs:
        raise shub_exceptions.NotFoundException(
            "list-spiders command is not found in the image.\n"
            "Please upgrade your scrapinghub-entrypoint-scrapy(>=0.7.0)")


def _check_start_crawl_entry(image_name, docker_client):
    """Check that the image has start-crawl entrypoint"""
    status, logs = _run_docker_command(
        docker_client, image_name, ['which', 'start-crawl'])
    if status != 0 or not logs:
        raise shub_exceptions.NotFoundException(
            "start-crawl command is not found in the image.\n"
            + SH_EP_SCRAPY_WARNING)


def _run_docker_command(client, image_name, command):
    """A helper to execute an arbitrary cmd with given docker image"""
    container = client.create_container(image=image_name, command=command)
    client.start(container)
    statuscode = client.wait(container=container['Id'])
    logs = client.logs(container=container['Id'], stdout=True,
                       stderr=True if statuscode else False,
                       stream=False, timestamps=False)
    utils.debug_log("{} results:\n{}".format(command, logs))
    return statuscode, logs
