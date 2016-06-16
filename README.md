# Dewey

<img
  src="artwork/dewey.png"
  align="left" width="200px" hspace="25px" vspace="20px">
</img>

Meet Dewey, the environment management robot. Originally named for
Melvil Dewey, (of the
[Dewey Decimal System](https://en.wikipedia.org/wiki/Dewey_Decimal_Classification)),
we decided the bot from [Silent Running](http://www.imdb.com/title/tt0067756/)
makes a better mascot.

It's also appropriate, since Dewey is a loyal robot, who is seen all alone
at the end of the movie, caring for the environment (a forest greenhouse on a
space ship), holding a battered old watering can as he drifts deeper into space.

## Purpose and Intent

Dewey is designed to be the canonical source of information about your computing
environments. A computing environment consists of hosts, clusters, and other
resources, and is built on top of networks and hardware. Dewey lets you store,
model, and manage all of this information, from rack to virtual machine.

On top of this model, Dewey will automate provisioning of virtual machines into
different environments, with role-based access controls per environment. The
initial provisioning integration will be with saltstack/salt-cloud, but other
integrations will be possible.

Unlike OpenNMS and other discovery-based management solutions, Dewey is
designed around defining what your environments should look like, not
discovering what's out there.

Dewey is suitable for integrating with configuration management systems like
saltstack, and salt integration is a major focus of the project. At PLOS, Dewey
provides an external pillar for salt, which defines all hosts and their roles.

## Architecture

Dewey is a Django application that leverages django-rest-framework for providing
a rest interface. No further interface is currently defined, but an HTML
frontend could be easily implemented.

## Setting up a development environment

Dewey is developed against python-3.2 and django-1.8. To get started, you must
first install python.

Once you have a working python, set up a virtual environment for containing
its dependencies:

* `pyvenv ~/.virtualenvs/dewey`

Export the environment variables required for configuration by appending the
following to `~/.virtualenvs/dewey/bin/activate`:

```
# set the Django settings module (more on this in a moment)
export DJANGO_SETTINGS_MODULE="dewey.settings.chaumes"
export SECRET_KEY='somereallylongrandomstringwithpunctuationandstuff'
export POSTGRES_PASSWORD='secret!'
# needed for syncing with Ephor asset tracker
export JIRA_USERNAME='joesixpack'
export JIRA_PASSWORD='drinkspbr'
```

## THIS PAGE IS NOT YET DONE
