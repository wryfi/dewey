# Dewey

<img
  src="https://upload.wikimedia.org/wikipedia/commons/0/01/Melvil_Dewey_1891.jpg"
  width="120px" style="float: left; margin-right: 15px">
</img>

This is Dewey, the PLOS ops inventory management system. Dewey is named for
Melvil Dewey, the creator of the [Dewey Decimal System](https://en.wikipedia.org/wiki/Dewey_Decimal_Classification) for
classifying materials in a library.

Like Dewey's decimal system, this project is all about cataloging resources and
classifying them according to their properties. Unlike Dewey, we're cataloging
computer equipment, hosts, and other technology resources, instead of books.

While Melvil chose to use numeric classifications, we mostly use descriptive
ones.

## Purpose and Intent

Dewey is designed to be a canonical source of information for what should
exist in the world of compute infrastructure. Its purpose is not to discover
what exists in your network, but to be the reference for what should exist.

Dewey is suitable for integrating with configuration management systems like
saltstack, and extensive salt integration is planned. At PLOS, Dewey provides
an external pillar for salt, which defines all hosts and their roles.

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
