# python-restconfig
ConfigParser Subclass and Flask blueprint to provide network backed configmap functionality.

I used abstract classes as much as possible to allow easy extension. You can create a subclass of Connection to provide other
backends for the client than the provided REST API. It is also easy to create a subclass of the ConfigData class so that
you can provide the REST API with a baking store other than a ConfigParser.

Right now, I'm working on read access only. I may provide read/write in the future.