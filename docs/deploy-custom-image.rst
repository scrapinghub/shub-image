.. _shub-image-deploy:

=========================================
Deploy a custom image to Scrapy Cloud 2.0
=========================================

.. include:: deprecation-warning.rst

**Scrapy Cloud 2.0** is the newest Scrapy Cloud platform version which allows you to run Scrapy spiders in Docker containers. This document will show you how to use the shub-image_ command line tool to deploy custom Docker images for your Scrapy projects to Scrapy Cloud 2.0.

.. note:: If you don't need a custom Docker image, you can continue using shub_ to deploy your spiders. Just make sure to **upgrade** it before doing so:

    .. code-block:: bash

        $ pip install shub --upgrade

.. _shub-image: https://github.com/scrapinghub/shub-image/
.. _shub: https://github.com/scrapinghub/shub

Installation
============
Install the ``shub-image`` tool via pip:

.. code-block:: bash

    $ pip install shub-image

Deployment
==========
This section describes how to build and deploy to Scrapy Cloud 2.0 a custom Docker image for a Scrapy project.


.. warning:: Make sure you are working on a Scrapy Cloud 2.0 project before following this guide. You can migrate your old projects via `Scrapy Cloud web dashboard <http://dash.scrapinghub.com>`_.

.. _step-one:

1. Initialization
-----------------
Open up a terminal and go to your crawler's project folder in your local machine:

.. code-block:: bash

    $ cd path/to/your/project

And then run the :ref:`init command <commands-init>`:

.. code-block:: bash

    $ shub-image init --requirements path/to/requirements.txt

This will create a Dockerfile for your container including ``requirements.txt`` as a dependency and using `python:2.7 <https://hub.docker.com/r/library/python/>`_ as `the base image <https://docs.docker.com/engine/reference/builder/>`_ for your custom image. If you want to use a different one, pass the ``--base-image`` option, like this:

.. code-block:: bash

    $ shub-image init --base-image scrapinghub/base:12.04

In this case, it will use the image available at https://hub.docker.com/r/scrapinghub/base tagged with ``12.04``.

.. warning:: Make sure to include `scrapinghub-entrypoint-scrapy <https://pypi.python.org/pypi/scrapinghub-entrypoint-scrapy>`_ in your requirements.txt file. It is a support layer to pass all the job data to Scrapy inside a Mesos task. If you ignore this, your Scrapy projects won't work at Scrapy Cloud 2.0.

2. Define your target image
---------------------------
Now you need to define the Docker repository that will store the image built by this tool. To do this, open your project's ``scrapinghub.yml`` file and add an ``images`` section to it, like this:

.. code-block:: yaml

    projects:
        default: 29629
    images:
        default: yourusername/repository


The settings above define that ``shub-image`` will push the image of your Docker container to https://hub.docker.com/r/yourusername/repository. You can also specify the complete URL for your repository if you are not using the default registry (which is https://hub.docker.com).

.. tip:: Your project might not have a ``scrapinghub.yml`` file, because it has been introduced with recent versions of `shub`_. Make sure to upgrade your `shub`_ package by running:

    .. code-block:: bash

            $ pip install shub --upgrade

    And then create ``scrapinghub.yml`` by running:

    .. code-block:: bash

            $ shub deploy

    **After this**, don't forget to add the ``images`` section to it, since shub doesn't include it for you.


3. Build the image
------------------
Once you have the Dockerfile (generated in :ref:`step 1 <step-one>`) and your target image settings, run the :ref:`build <commands-build>` command to make ``shub-image`` build the Docker image for you:

.. code-block:: bash

    $ shub-image build
    The image yourusername/repository:1.0 build is completed.

After doing so, you can run the :ref:`test <commands-test>` command to make sure everything is alright for deployment:


.. code-block:: bash

    $ shub-image test


4. Push the image to the registry
---------------------------------
This step will push the image you just built to the repository defined in the ``scrapinghub.yml`` file. To do this, run the :ref:`push <commands-push>` command:

.. code-block:: bash

    $ shub-image push
    Pushing yourusername/repository:1.0 to the registry.
    The image yourusername/repository:1.0 pushed successfully.

In the example above, the image was pushed to https://hub.docker.com/r/yourusername/repository.


5. Deploy your image to Scrapy Cloud 2.0
----------------------------------------
Once your image has been uploaded to the Docker registry, you have to deploy it to Scrapy Cloud 2.0 using the :ref:`deploy <commands-deploy>` command:

.. code-block:: bash

    $ shub-image deploy
    Deploy task results: <Response [302]>
    You can check deploy results later with 'shub-image check --id 10'.
    Deploy results:
     {u'status': u'started'}
     {u'status': u'progress', u'last_step': u'pulling'}
     {u'status': u'ok', u'project': 29629, u'version': u'1.0', u'spiders': 1}

Now you can schedule your spiders via both web dashboard or shub.

.. warning:: The deploy step for a project might be slow for the first time you do it.


.. _commands:

Commands
========
Each of the commands we used in the steps above has some options that allow you to customize their behavior. For example, the :ref:`push <commands-push>` command allows you to pass your registry credentials via the ``--username`` and ``--password`` options. This section lists the options available for each command.

.. _commands-init:

init
----
The first command you have to run when migrating your projects to run on Scrapy Cloud 2.0 is ``shub-image init``. This command generates a ``Dockerfile`` to be used later by the :ref:`build <commands-build>` command to create a Docker container based on your Scrapy project.

The generated Dockerfile will likely fit your needs. But if it doesn't, it's just a matter of editing the file.

Options for init
^^^^^^^^^^^^^^^^

.. function:: --project <text>

Define the Scrapy project where the settings are going to be read from.

**Default value**: ``default`` from current folder's ``scrapy.cfg``.


.. function:: --base-image <text>

Define which `base Docker image <https://docs.docker.com/engine/reference/builder>`_ your custom image will build upon.

**Default value**: ``python:2.7``


.. function:: --requirements <path>

Set ``path`` as the Python requirements file for this project.

**Default value**: project directory ``requirements.txt``


.. function:: --base-deps <list>

Add system dependencies for your image, overriding the default ones. The ``<list>`` parameter should be a comma separated list with no spaces between dependencies.

**Default value**: ``telnet,vim,htop,strace,iputils-ping,lsof``


.. function:: --add-deps <list>

Provide additional system dependencies to install in your image along with the default ones. The ``<list>`` parameter should be a comma separated list with no spaces between dependencies.


.. function:: --list-recommended-reqs

List recommended Python requirements for a Scrapy Cloud 2.0 project and exit.


**Example:**

.. code-block:: bash

    $ shub-image init --base-image scrapinghub/base:12.04 \
    --requirements other/requirements-dev.txt \
    --add-deps phantomjs,tmux


.. _commands-build:

build
-----
This command uses the Dockerfile created by the :ref:`init <commands-init>` command to build the image that's going to be deployed later.

It reads the target images from the `scrapinghub.yml <http://doc.scrapinghub.com/shub.html#configuration>`_ file, which is generated by the deploy command from shub_ >= 2.0. You should add a section called ``images`` on it using the following format:

.. code-block:: yaml

    images:
        default: username/project
        private: your.own.registry:port/username/project
        fallback: anotheruser/project


Options for build
^^^^^^^^^^^^^^^^^

.. function:: --list-targets

List available targets and exit.


.. function:: --target <text>

Define the image for release. The ``<text>`` parameter must be one of the target names listed by ``list-targets``.

**Default value**: ``default``


.. function:: --version <text>

Tag your image with ``<text>``. You'll probably not need to set this manually, because the tool automatically sets this for you.

If you pass the ``--version`` parameter here, you will have to pass the exact same value to any other commands that accept this parameter (:ref:`push <commands-push>` and :ref:`deploy <commands-deploy>`).

**Default value**: identifier generated by shub.


.. function:: -d/--debug

Increase the tool's verbosity.


**Example:**

.. code-block:: bash

    $ shub-image build --list-targets
    default
    private
    fallback
    $ shub-image build --target private --version 1.0.4

.. _commands-push:

push
----
This command pushes the image built by the ``build`` command to the registry (the ``default`` one or another one specified with the ``--target option``).


Options for push
^^^^^^^^^^^^^^^^

.. function:: --list-targets

List available targets and exit.


.. function:: --target <text>

Define the image for release. The ``<text>`` parameter must be one of the target's names listed by ``list-targets``.

**Default value**: ``default``


.. function:: --version <text>

Tag your image with ``<text>``. If you provided a custom version to the :ref:`build <commands-build>` command, make sure to provide the same value here.

**Default value**: identifier generated by shub.


.. function:: --username <text>

Set the username to authenticate in the Docker registry.

**Note**: we don't store your credentials and you'll be able to use OAuth2 in the near future.


.. function:: --password <text>

Set the password to authenticate in the Docker registry.


.. function:: --email <text>

Set the email to authenticate in the Docker registry (if needed).


.. function:: --apikey <text>

(beta) Use provided apikey to authenticate in the Scrapy Cloud Docker registry.


.. function:: --insecure

Use the Docker registry in insecure mode.


.. function:: -d/--debug

Increase the tool's verbosity.


Most of these options are related with Docker registry authentication. If you don't provide them, ``shub-image`` will try to push your image using the plain HTTP ``--insecure-registry`` docker mode.

**Example:**

.. code-block:: bash

    $ shub-image push --target private --version 1.0.4 \
    --username johndoe --password johndoepwd

This example authenticates the user ``johndoe`` to the registry ``your.own.registry:port`` (as defined in the :ref:`build command example <commands-build>`).


.. _commands-deploy:

deploy
------
This command deploys your release image to Scrapy Cloud 2.0.


Options for deploy
^^^^^^^^^^^^^^^^^^

.. function:: --list-targets

List available targets and exit.


.. function:: --target <text>

Target name that defines where the image is going to be pushed to.

**Default value**: ``default``


.. function:: --version <text>

The image version that you want to deploy to Scrapy Cloud 2.0. If you provided a custom version to the :ref:`build <commands-build>` and :ref:`push <commands-push>` commands, make sure to provide the same value here.


**Default value**: identifier generated by shub


.. function:: --username <text>

Set the username to authenticate in the Docker registry.

**Note**: we don't store your credentials and you'll be able to use OAuth2 in the near future.


.. function:: --password <text>

Set the password to authenticate in the registry.


.. function:: --email <text>

Set the email to authenticate in the Docker registry (if needed).


.. function:: --apikey <text>

(beta) Use provided apikey to authenticate in the Scrapy Cloud Docker registry.


.. function:: --insecure

Use the Docker registry in insecure mode.


.. function:: --async

Make deploy asynchronous. When enabled, the tool will exit as soon as the deploy is started in background. You can then check the status of your deploy task periodically via the :ref:`check <commands-check>` command.

**Default value**: ``False``


.. function:: -d/--debug

Increase the tool's verbosity.


**Example:**

.. code-block:: bash

    $ shub-image deploy --target private --version 1.0.4 \
    --username johndoe --password johndoepwd --async

This command will deploy the image from the ``private`` target, using user credentials passed as parameters and exit as soon as the deploy process starts (``--async``).


.. _commands-upload:

upload
------

It is a shortcut for the build -> push -> deploy chain of commands.

**Example:**

.. code-block:: bash

    $ shub-image upload --target private --version 1.0.4 \
    --username johndoe --password johndoepwd


Options for upload
^^^^^^^^^^^^^^^^^^

The ``upload`` command accepts the same parameters as the :ref:`deploy <commands-deploy>` command.


.. _commands-check:

check
-----
This command checks the status of your deployment and is useful when you do the deploy in asynchronous mode.

By default, the ``check`` command will return results from the last deploy.

Options for check
^^^^^^^^^^^^^^^^^

.. function:: --id <number>

The id of the deploy you want to check the status.

**Default value**: the id of the latest deploy.


**Example:**

.. code-block:: bash

    $ shub-image check --id 0

This command above will check the status of the first deploy made (id 0).


.. _commands-test:

test
----
This command checks if your local setup meets the requirements for a deployment at Scrapy Cloud 2.0. You can run it right after the :ref:`build command <commands-build>` to make sure everything is ready to go before you push your image with the :ref:`push command <commands-push>`.


Options for test
^^^^^^^^^^^^^^^^

.. function:: --list-targets

List available targets and exit.

.. function:: -d/--debug

Increase the tool's verbosity.


Troubleshooting
===============

Image not found while deploying
-------------------------------
Make sure the repository you set in your ``scrapinghub.yml`` images section exists in the registry. Consider this ``scrapinghub.yml`` example file:


.. code-block:: yaml

    projects:
        default: 555555
    images:
        default: johndoe/scrapy-crawler

``shub-image`` will try to deploy the image to http://hub.docker.com/johndoe/scrapy-crawler, since `hub.docker.com <http://hub.docker.com>`_ is the default registry. So, to make it work, you have to log into your account there and create the repository.

Otherwise, you are going to get an error message like this:

.. code-block:: json

    Deploy results: {u'status': u'error', u'last_step': u'pulling', u'error': u"DockerCmdFailure(u'Error: image johndoe/scrapy-crawler not found',)"}


Uploading to a private repository
---------------------------------
If you are using a private repository to push your images to, make sure to pass your registry credentials to both :ref:`push <commands-push>` and :ref:`deploy <commands-deploy>` commands:

.. code-block:: bash

    $ shub-image push --username johndoe --password yourpass
    $ shub-image deploy --username johndoe --password yourpass


ImportError while initializing the project
------------------------------------------
If you are getting an ``ImportError`` like this while running ``shub-image init``:

.. code-block:: bash

    ...
        from shub import config as shub_config
    ImportError: cannot import name config

You should make sure you have the latest version of shub_ installed by running:

.. code-block:: bash

    $ pip install shub --upgrade
