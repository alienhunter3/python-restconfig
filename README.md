# python-restconfig
ConfigParser Subclass and Flask blueprint to provide network backed configmap functionality.

I used abstract classes as much as possible to allow easy extension. The ReadOnlyConfig class and the RestBlueprint both 
use the Connection abstract class to retrieve data. I have implemented a RawConfigParser Connection and a RestAPI
Connection for this package. To add other backends, create a subclass of Connection as desired, and you can use it with 
either the ReadOnlyConfig class, or the restconfig blueprint.

Right now, I'm working on read access only. I may provide read/write in the future.